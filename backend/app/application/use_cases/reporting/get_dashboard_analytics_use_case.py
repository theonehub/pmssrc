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
                approved_reimbursements=reimbursement_stats.get("approved_count", 0),
                approved_reimbursements_amount=reimbursement_stats.get("approved_amount", 0.0),
                
                # Leave metrics (placeholder)
                pending_leaves=0,
                
                # Department metrics
                total_departments=len(distributions.get("department_distribution", {})),
                
                # Distributions
                department_distribution=distributions.get("department_distribution", {}),
                role_distribution=distributions.get("role_distribution", {}),
                
                # Trends with enhanced attendance data
                attendance_trends={
                    "daily_summary": {
                        "present_today": attendance_stats.get("present_today", 0),
                        "absent_today": attendance_stats.get("absent_today", 0),
                        "late_today": attendance_stats.get("late_today", 0),
                        "work_from_home_today": attendance_stats.get("work_from_home_today", 0),
                        "on_leave_today": attendance_stats.get("on_leave_today", 0),
                        "pending_check_out": attendance_stats.get("pending_check_out", 0),
                        "attendance_percentage": attendance_stats.get("attendance_percentage", 0.0),
                        "checked_in_percentage": attendance_stats.get("checked_in_percentage", 0.0),
                        "productivity_score": attendance_stats.get("productivity_score", 0.0),
                        "average_working_hours": attendance_stats.get("average_working_hours", 0.0),
                        "total_overtime_hours": attendance_stats.get("total_overtime_hours", 0.0)
                    }
                },
                leave_trends={},
                
                generated_at=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Successfully generated dashboard analytics for organisation: {current_user.hostname}")
            return dashboard_analytics
            
        except Exception as e:
            logger.error(f"Error getting dashboard analytics for organisation {current_user.hostname}: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Return analytics with error information for debugging
            return DashboardAnalyticsDTO(
                total_users=0,
                active_users=0,
                inactive_users=0,
                recent_joiners_count=0,
                checkin_count=0,
                checkout_count=0,
                pending_reimbursements=0,
                pending_reimbursements_amount=0.0,
                approved_reimbursements=0,
                approved_reimbursements_amount=0.0,
                pending_leaves=0,
                total_departments=0,
                department_distribution={},
                role_distribution={},
                attendance_trends={
                    "daily_summary": {
                        "present_today": 0,
                        "absent_today": 0,
                        "late_today": 0,
                        "work_from_home_today": 0,
                        "on_leave_today": 0,
                        "pending_check_out": 0,
                        "attendance_percentage": 0.0,
                        "checked_in_percentage": 0.0,
                        "productivity_score": 0.0,
                        "average_working_hours": 0.0,
                        "total_overtime_hours": 0.0
                    }
                },
                leave_trends={},
                generated_at=datetime.utcnow().isoformat(),
                error_message=str(e)  # Add error for debugging
            )
    
    async def _get_user_statistics(self, current_user: "CurrentUser") -> Dict[str, Any]:
        """Get user-related statistics."""
        try:
            logger.info(f"Getting user statistics for organisation: {current_user.hostname}")
            # Get all users for the organisation
            users, total_count = await self.user_repository.find_with_filters(
                filters=None,  # Get all users
                hostname=current_user.hostname
            )
            logger.info(f"Found {total_count} users for organisation: {current_user.hostname}")
            
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
            import traceback
            logger.error(f"User statistics error traceback: {traceback.format_exc()}")
            return {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "recent_joiners_count": 0
            }
    
    async def _get_reimbursement_statistics(self, current_user: "CurrentUser") -> Dict[str, Any]:
        """Get reimbursement-related statistics with timespan filtering."""
        try:
            # Default to last 30 days if no timespan specified
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # Get pending reimbursements with timespan
            pending_reimbursements = await self.reimbursement_repository.get_pending_reimbursements_by_timespan(
                current_user.hostname, start_date, end_date
            )
            
            # Get approved reimbursements with timespan
            approved_reimbursements = await self.reimbursement_repository.get_approved_reimbursements_by_timespan(
                current_user.hostname, start_date, end_date
            )
            
            # Calculate statistics
            pending_count = len(pending_reimbursements)
            pending_amount = sum(
                reimbursement.amount for reimbursement in pending_reimbursements
            )
            
            approved_count = len(approved_reimbursements)
            approved_amount = sum(
                reimbursement.amount for reimbursement in approved_reimbursements
            )
            
            logger.info(f"Reimbursement statistics: {pending_count} pending (₹{pending_amount}), "
                       f"{approved_count} approved (₹{approved_amount}) in last 30 days")
            
            return {
                "pending_count": pending_count,
                "pending_amount": pending_amount,
                "approved_count": approved_count,
                "approved_amount": approved_amount,
                "total_count": pending_count + approved_count,
                "total_amount": pending_amount + approved_amount,
                "timespan_days": 30
            }
            
        except Exception as e:
            logger.error(f"Error getting reimbursement statistics: {e}")
            return {
                "pending_count": 0,
                "pending_amount": 0.0,
                "approved_count": 0,
                "approved_amount": 0.0,
                "total_count": 0,
                "total_amount": 0.0,
                "timespan_days": 30
            }
    
    async def _get_attendance_statistics(self, current_user: "CurrentUser") -> Dict[str, Any]:
        """Get attendance-related statistics with comprehensive metrics."""
        try:
            if not self.attendance_repository:
                logger.warning("Attendance repository not available, returning default values")
                return {
                    "checkin_count": 0,
                    "checkout_count": 0,
                    "total_employees": 0,
                    "present_today": 0,
                    "absent_today": 0,
                    "attendance_percentage": 0.0,
                    "pending_check_out": 0,
                    "average_working_hours": 0.0,
                    "late_today": 0,
                    "work_from_home_today": 0
                }
            
            # Get today's comprehensive attendance statistics
            today = date.today()
            stats = await self.attendance_repository.get_daily_statistics(today, current_user.hostname)
            
            logger.info(f"Attendance statistics for {current_user.hostname}: "
                       f"{stats.checked_in} checked in, {stats.checked_out} checked out, "
                       f"{stats.present_today} present, {stats.attendance_percentage:.1f}% attendance")
            
            return {
                # Basic check-in/out counts (for backward compatibility)
                "checkin_count": stats.checked_in,
                "checkout_count": stats.checked_out,
                
                # Comprehensive attendance metrics
                "total_employees": stats.total_employees,
                "present_today": stats.present_today,
                "absent_today": stats.absent_today,
                "late_today": stats.late_today,
                "work_from_home_today": stats.work_from_home_today,
                "on_leave_today": stats.on_leave_today,
                
                # Status tracking
                "pending_check_out": stats.pending_check_out,
                "attendance_percentage": round(stats.attendance_percentage, 1),
                
                # Working hours metrics
                "average_working_hours": round(stats.average_working_hours, 1),
                "total_overtime_hours": round(stats.total_overtime_hours, 1),
                
                # Additional calculated metrics
                "checked_in_percentage": round((stats.checked_in / max(stats.total_employees, 1)) * 100, 1) if stats.total_employees > 0 else 0.0,
                "productivity_score": round(stats.average_working_hours / 8.0 * 100, 1) if stats.average_working_hours > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting attendance statistics: {e}")
            import traceback
            logger.error(f"Attendance statistics error traceback: {traceback.format_exc()}")
            return {
                "checkin_count": 0,
                "checkout_count": 0,
                "total_employees": 0,
                "present_today": 0,
                "absent_today": 0,
                "attendance_percentage": 0.0,
                "pending_check_out": 0,
                "average_working_hours": 0.0,
                "late_today": 0,
                "work_from_home_today": 0,
                "checked_in_percentage": 0.0,
                "productivity_score": 0.0
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
        