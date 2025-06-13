"""
Get Dashboard Analytics Use Case
Aggregates data from all modules to provide consolidated dashboard analytics
"""

import logging
from typing import Dict, Any, TYPE_CHECKING
from datetime import datetime, timedelta, date

from app.application.dto.reporting_dto import DashboardAnalyticsDTO
from app.application.interfaces.repositories.user_repository import UserRepository
from app.application.interfaces.repositories.reimbursement_repository import ReimbursementRepository
from app.application.interfaces.repositories.attendance_repository import AttendanceRepository

if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class GetDashboardAnalyticsUseCase:
    """
    Use case for getting consolidated dashboard analytics.
    
    Aggregates data from multiple modules to provide a comprehensive
    dashboard view for the organisation.
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        reimbursement_repository: ReimbursementRepository,
        attendance_repository: AttendanceRepository = None
    ):
        """Initialize use case with dependencies."""
        self.user_repository = user_repository
        self.reimbursement_repository = reimbursement_repository
        self.attendance_repository = attendance_repository
    
    async def execute(self, current_user: "CurrentUser") -> DashboardAnalyticsDTO:
        """
        Execute the dashboard analytics use case.
        
        Args:
            current_user: Current user context with organisation info
            
        Returns:
            Dashboard analytics data
        """
        try:
            logger.info(f"Getting dashboard analytics for organisation: {current_user.hostname}")
            
            # Get user statistics
            user_stats = await self._get_user_statistics(current_user)
            
            # Get reimbursement statistics
            reimbursement_stats = await self._get_reimbursement_statistics(current_user)
            
            # Get department and role distributions
            distributions = await self._get_distributions(current_user)

            # Get attendance statistics
            attendance_stats = await self._get_attendance_statistics(current_user)
            
            # Combine all statistics
            dashboard_analytics = DashboardAnalyticsDTO(
                # User metrics
                total_users=user_stats.get("total_users", 0),
                active_users=user_stats.get("active_users", 0),
                inactive_users=user_stats.get("inactive_users", 0),
                recent_joiners_count=user_stats.get("recent_joiners_count", 0),
                
                # Attendance metrics
                checkin_count=attendance_stats.get("checkin_count", 0),
                checkout_count=attendance_stats.get("checkout_count", 0),
                
                # Reimbursement metrics
                pending_reimbursements=reimbursement_stats.get("pending_count", 0),
                pending_reimbursements_amount=reimbursement_stats.get("pending_amount", 0.0),
                
                # Leave metrics (placeholder)
                pending_leaves=0,
                
                # Department metrics
                total_departments=len(distributions.get("department_distribution", {})),
                
                # Distributions
                department_distribution=distributions.get("department_distribution", {}),
                role_distribution=distributions.get("role_distribution", {}),
                
                # Trends (placeholder for now)
                attendance_trends={},
                leave_trends={},
                
                generated_at=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Successfully generated dashboard analytics for organisation: {current_user.hostname}")
            return dashboard_analytics
            
        except Exception as e:
            logger.error(f"Error getting dashboard analytics for organisation {current_user.hostname}: {e}")
            # Return empty analytics instead of failing
            return DashboardAnalyticsDTO()
    
    async def _get_user_statistics(self, current_user: "CurrentUser") -> Dict[str, Any]:
        """Get user-related statistics."""
        try:
            # Get all users for the organisation
            users, total_count = await self.user_repository.find_with_filters(
                filters=None,  # Get all users
                hostname=current_user.hostname
            )
            
            active_users = sum(1 for user in users if user.is_active)
            inactive_users = total_count - active_users
            
            # Count recent joiners (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_joiners = sum(
                1 for user in users 
                if user.created_at and user.created_at >= thirty_days_ago
            )
            
            return {
                "total_users": total_count,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "recent_joiners_count": recent_joiners
            }
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "recent_joiners_count": 0
            }
    
    async def _get_reimbursement_statistics(self, current_user: "CurrentUser") -> Dict[str, Any]:
        """Get reimbursement-related statistics."""
        try:
            # Get pending reimbursements
            pending_reimbursements = await self.reimbursement_repository.get_pending_reimbursements(
                current_user.hostname
            )
            
            pending_count = len(pending_reimbursements)
            pending_amount = sum(
                reimbursement.amount for reimbursement in pending_reimbursements
            )
            
            return {
                "pending_count": pending_count,
                "pending_amount": pending_amount
            }
            
        except Exception as e:
            logger.error(f"Error getting reimbursement statistics: {e}")
            return {
                "pending_count": 0,
                "pending_amount": 0.0
            }
    
    async def _get_attendance_statistics(self, current_user: "CurrentUser") -> Dict[str, Any]:
        """Get attendance-related statistics."""
        try:
            if not self.attendance_repository:
                logger.warning("Attendance repository not available, returning default values")
                return {
                    "checkin_count": 0,
                    "checkout_count": 0
                }
            
            # Get today's attendance statistics
            today = date.today()
            stats = await self.attendance_repository.get_daily_statistics(today, current_user.hostname)
            
            return {
                "checkin_count": stats.checked_in,
                "checkout_count": stats.checked_out
            }
            
        except Exception as e:
            logger.error(f"Error getting attendance statistics: {e}")
            return {
                "checkin_count": 0,
                "checkout_count": 0
            }
    
    async def _get_distributions(self, current_user: "CurrentUser") -> Dict[str, Any]:
        """Get department and role distributions."""
        try:
            # Get all users for the organisation
            users, _ = await self.user_repository.find_with_filters(
                filters=None,  # Get all users
                hostname=current_user.hostname
            )
            
            # Calculate department distribution
            department_distribution = {}
            role_distribution = {}
            
            for user in users:
                # Department distribution
                dept = user.department or "Unassigned"
                department_distribution[dept] = department_distribution.get(dept, 0) + 1
                
                # Role distribution
                role = user.role.value if hasattr(user, 'role') and user.role else "user"
                role_distribution[role] = role_distribution.get(role, 0) + 1
            
            return {
                "department_distribution": department_distribution,
                "role_distribution": role_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting distributions: {e}")
            return {
                "department_distribution": {},
                "role_distribution": {}
            } 