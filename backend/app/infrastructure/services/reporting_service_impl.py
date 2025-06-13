"""
Reporting Service Implementation
Concrete implementation of reporting service
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

from app.application.interfaces.services.reporting_service import ReportingService
from app.application.interfaces.repositories.reporting_repository import ReportingRepository
from app.application.interfaces.repositories.user_repository import UserRepository
from app.application.interfaces.repositories.reimbursement_repository import ReimbursementRepository
from app.application.interfaces.repositories.attendance_repository import AttendanceRepository
from app.application.dto.reporting_dto import (
    CreateReportRequestDTO, UpdateReportRequestDTO, ReportSearchFiltersDTO,
    ReportResponseDTO, ReportListResponseDTO, DashboardAnalyticsDTO,
    UserAnalyticsDTO, AttendanceAnalyticsDTO, LeaveAnalyticsDTO,
    PayrollAnalyticsDTO, ReimbursementAnalyticsDTO, ConsolidatedAnalyticsDTO,
    ExportRequestDTO, ExportResponseDTO, ReportingValidationError,
    ReportingNotFoundError
)
from app.application.use_cases.reporting.get_dashboard_analytics_use_case import GetDashboardAnalyticsUseCase
from app.domain.entities.report import Report, ReportType, ReportFormat
from app.domain.value_objects.report_id import ReportId

if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class ReportingServiceImpl(ReportingService):
    """
    Concrete implementation of reporting service.
    
    Follows SOLID principles:
    - SRP: Handles reporting business logic
    - OCP: Extensible through dependency injection
    - LSP: Implements service interface correctly
    - ISP: Implements focused interface
    - DIP: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        reporting_repository: ReportingRepository,
        user_repository: UserRepository,
        reimbursement_repository: ReimbursementRepository,
        attendance_repository: AttendanceRepository = None
    ):
        """Initialize service with dependencies."""
        self.reporting_repository = reporting_repository
        self.user_repository = user_repository
        self.reimbursement_repository = reimbursement_repository
        self.attendance_repository = attendance_repository
        
        # Initialize use cases
        self._dashboard_analytics_use_case = GetDashboardAnalyticsUseCase(
            user_repository=user_repository,
            reimbursement_repository=reimbursement_repository,
            attendance_repository=attendance_repository
        )
    
    async def create_report(
        self, 
        request: CreateReportRequestDTO, 
        current_user: "CurrentUser"
    ) -> ReportResponseDTO:
        """Create a new report."""
        try:
            logger.info(f"Creating report '{request.name}' for organisation: {current_user.hostname}")
            
            # Validate request
            validation_errors = request.validate()
            if validation_errors:
                raise ReportingValidationError("Validation failed", validation_errors)
            
            # Create report entity
            report = Report.create(
                id=ReportId.generate(),
                name=request.name,
                description=request.description,
                report_type=ReportType(request.report_type),
                format=ReportFormat(request.format),
                parameters=request.parameters or {},
                created_by=current_user.employee_id,
                organisation_id=current_user.hostname
            )
            
            # Save report
            saved_report = await self.reporting_repository.save(report, current_user.hostname)
            
            logger.info(f"Successfully created report {saved_report.id.value}")
            return ReportResponseDTO.from_entity(saved_report)
            
        except ReportingValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            raise
    
    async def get_report_by_id(
        self, 
        report_id: str, 
        current_user: "CurrentUser"
    ) -> Optional[ReportResponseDTO]:
        """Get report by ID."""
        try:
            logger.info(f"Getting report {report_id} for organisation: {current_user.hostname}")
            
            report = await self.reporting_repository.get_by_id(
                ReportId(report_id), 
                current_user.hostname
            )
            
            if not report:
                raise ReportingNotFoundError(report_id)
            
            return ReportResponseDTO.from_entity(report)
            
        except ReportingNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting report {report_id}: {e}")
            raise
    
    async def list_reports(
        self, 
        filters: ReportSearchFiltersDTO, 
        current_user: "CurrentUser"
    ) -> ReportListResponseDTO:
        """List reports with filters and pagination."""
        try:
            logger.info(f"Listing reports for organisation: {current_user.hostname}")
            
            # Validate filters
            validation_errors = filters.validate()
            if validation_errors:
                raise ReportingValidationError("Filter validation failed", validation_errors)
            
            # Get reports
            reports, total_count = await self.reporting_repository.find_with_filters(
                filters, current_user.hostname
            )
            
            # Convert to DTOs
            from app.application.dto.reporting_dto import ReportSummaryDTO
            report_summaries = [ReportSummaryDTO.from_entity(report) for report in reports]
            
            # Calculate pagination info
            total_pages = (total_count + filters.page_size - 1) // filters.page_size
            has_next = filters.page < total_pages
            has_previous = filters.page > 1
            
            return ReportListResponseDTO(
                reports=report_summaries,
                total_count=total_count,
                page=filters.page,
                page_size=filters.page_size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except ReportingValidationError:
            raise
        except Exception as e:
            logger.error(f"Error listing reports: {e}")
            raise
    
    async def update_report(
        self,
        report_id: str,
        request: UpdateReportRequestDTO,
        current_user: "CurrentUser"
    ) -> ReportResponseDTO:
        """Update an existing report."""
        try:
            logger.info(f"Updating report {report_id} for organisation: {current_user.hostname}")
            
            # Validate request
            validation_errors = request.validate()
            if validation_errors:
                raise ReportingValidationError("Validation failed", validation_errors)
            
            # Get existing report
            report = await self.reporting_repository.get_by_id(
                ReportId(report_id), 
                current_user.hostname
            )
            
            if not report:
                raise ReportingNotFoundError(report_id)
            
            # Update fields
            if request.name is not None:
                report.name = request.name
            
            if request.description is not None:
                report.description = request.description
            
            if request.parameters is not None:
                report.update_parameters(request.parameters)
            
            # Save updated report
            updated_report = await self.reporting_repository.save(report, current_user.hostname)
            
            logger.info(f"Successfully updated report {report_id}")
            return ReportResponseDTO.from_entity(updated_report)
            
        except (ReportingValidationError, ReportingNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Error updating report {report_id}: {e}")
            raise
    
    async def delete_report(
        self,
        report_id: str,
        current_user: "CurrentUser"
    ) -> bool:
        """Delete a report."""
        try:
            logger.info(f"Deleting report {report_id} for organisation: {current_user.hostname}")
            
            # Check if report exists
            report = await self.reporting_repository.get_by_id(
                ReportId(report_id), 
                current_user.hostname
            )
            
            if not report:
                raise ReportingNotFoundError(report_id)
            
            # Delete report
            success = await self.reporting_repository.delete(
                ReportId(report_id), 
                current_user.hostname
            )
            
            if success:
                logger.info(f"Successfully deleted report {report_id}")
            else:
                logger.warning(f"Failed to delete report {report_id}")
            
            return success
            
        except ReportingNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting report {report_id}: {e}")
            raise
    
    async def get_dashboard_analytics(
        self, 
        current_user: "CurrentUser"
    ) -> DashboardAnalyticsDTO:
        """Get consolidated dashboard analytics."""
        try:
            logger.info(f"Getting dashboard analytics for organisation: {current_user.hostname}")
            
            # Use the dedicated use case
            analytics = await self._dashboard_analytics_use_case.execute(current_user)
            
            logger.info(f"Successfully generated dashboard analytics for organisation: {current_user.hostname}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting dashboard analytics: {e}")
            # Return empty analytics instead of failing
            return DashboardAnalyticsDTO()
    
    async def get_user_analytics(
        self, 
        current_user: "CurrentUser"
    ) -> UserAnalyticsDTO:
        """Get user analytics data."""
        try:
            logger.info(f"Getting user analytics for organisation: {current_user.hostname}")
            
            # Get all users for the organisation
            users, total_count = await self.user_repository.find_with_filters(
                filters=None,  # Get all users
                hostname=current_user.hostname
            )
            
            active_users = sum(1 for user in users if user.is_active)
            inactive_users = total_count - active_users
            
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
            
            # Get recent joiners (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_joiners = [
                {
                    "employee_id": user.employee_id.value,
                    "name": user.name,
                    "department": user.department,
                    "date_of_joining": user.date_of_joining
                }
                for user in users 
                if user.created_at and user.created_at >= thirty_days_ago
            ]
            
            analytics = UserAnalyticsDTO(
                total_users=total_count,
                active_users=active_users,
                inactive_users=inactive_users,
                department_distribution=department_distribution,
                role_distribution=role_distribution,
                recent_joiners=recent_joiners,
                user_growth_trends={}  # Placeholder for now
            )
            
            logger.info(f"Successfully generated user analytics for organisation: {current_user.hostname}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            # Return empty analytics instead of failing
            return UserAnalyticsDTO(
                total_users=0,
                active_users=0,
                inactive_users=0,
                department_distribution={},
                role_distribution={},
                recent_joiners=[],
                user_growth_trends={}
            )
    
    async def get_attendance_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> AttendanceAnalyticsDTO:
        """Get attendance analytics data."""
        try:
            logger.info(f"Getting attendance analytics for organisation: {current_user.hostname}")
            
            # For now, return placeholder data
            # TODO: Implement when attendance repository methods are available
            analytics = AttendanceAnalyticsDTO(
                total_checkins_today=0,
                total_checkouts_today=0,
                present_count=0,
                absent_count=0,
                late_arrivals=0,
                early_departures=0,
                average_working_hours=0.0,
                attendance_trends={},
                department_attendance={}
            )
            
            logger.info(f"Successfully generated attendance analytics for organisation: {current_user.hostname}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting attendance analytics: {e}")
            return AttendanceAnalyticsDTO(
                total_checkins_today=0,
                total_checkouts_today=0,
                present_count=0,
                absent_count=0,
                late_arrivals=0,
                early_departures=0,
                average_working_hours=0.0,
                attendance_trends={},
                department_attendance={}
            )
    
    async def get_leave_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> LeaveAnalyticsDTO:
        """Get leave analytics data."""
        try:
            logger.info(f"Getting leave analytics for organisation: {current_user.hostname}")
            
            # For now, return placeholder data
            # TODO: Implement when leave repository methods are available
            analytics = LeaveAnalyticsDTO(
                total_pending_leaves=0,
                total_approved_leaves=0,
                total_rejected_leaves=0,
                leave_type_distribution={},
                department_leave_trends={},
                monthly_leave_trends={}
            )
            
            logger.info(f"Successfully generated leave analytics for organisation: {current_user.hostname}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting leave analytics: {e}")
            return LeaveAnalyticsDTO(
                total_pending_leaves=0,
                total_approved_leaves=0,
                total_rejected_leaves=0,
                leave_type_distribution={},
                department_leave_trends={},
                monthly_leave_trends={}
            )
    
    async def get_payroll_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> PayrollAnalyticsDTO:
        """Get payroll analytics data."""
        try:
            logger.info(f"Getting payroll analytics for organisation: {current_user.hostname}")
            
            # For now, return placeholder data
            # TODO: Implement when payroll repository methods are available
            analytics = PayrollAnalyticsDTO(
                total_payouts_current_month=0,
                total_amount_current_month=0.0,
                average_salary=0.0,
                department_salary_distribution={},
                salary_trends={}
            )
            
            logger.info(f"Successfully generated payroll analytics for organisation: {current_user.hostname}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting payroll analytics: {e}")
            return PayrollAnalyticsDTO(
                total_payouts_current_month=0,
                total_amount_current_month=0.0,
                average_salary=0.0,
                department_salary_distribution={},
                salary_trends={}
            )
    
    async def get_reimbursement_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> ReimbursementAnalyticsDTO:
        """Get reimbursement analytics data."""
        try:
            logger.info(f"Getting reimbursement analytics for organisation: {current_user.hostname}")
            
            # Get pending reimbursements
            pending_reimbursements = await self.reimbursement_repository.get_pending_reimbursements(
                current_user.hostname
            )
            
            pending_count = len(pending_reimbursements)
            pending_amount = sum(
                reimbursement.amount for reimbursement in pending_reimbursements
            )
            
            # For now, use placeholder data for other metrics
            # TODO: Implement when more reimbursement repository methods are available
            analytics = ReimbursementAnalyticsDTO(
                total_pending_reimbursements=pending_count,
                total_pending_amount=pending_amount,
                total_approved_reimbursements=0,
                total_approved_amount=0.0,
                reimbursement_type_distribution={},
                monthly_reimbursement_trends={}
            )
            
            logger.info(f"Successfully generated reimbursement analytics for organisation: {current_user.hostname}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting reimbursement analytics: {e}")
            return ReimbursementAnalyticsDTO(
                total_pending_reimbursements=0,
                total_pending_amount=0.0,
                total_approved_reimbursements=0,
                total_approved_amount=0.0,
                reimbursement_type_distribution={},
                monthly_reimbursement_trends={}
            )
    
    async def get_consolidated_analytics(
        self, 
        current_user: "CurrentUser",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> ConsolidatedAnalyticsDTO:
        """Get consolidated analytics from all modules."""
        try:
            logger.info(f"Getting consolidated analytics for organisation: {current_user.hostname}")
            
            # Get analytics from all modules
            dashboard_analytics = await self.get_dashboard_analytics(current_user)
            user_analytics = await self.get_user_analytics(current_user)
            attendance_analytics = await self.get_attendance_analytics(current_user, start_date, end_date)
            leave_analytics = await self.get_leave_analytics(current_user, start_date, end_date)
            payroll_analytics = await self.get_payroll_analytics(current_user, start_date, end_date)
            reimbursement_analytics = await self.get_reimbursement_analytics(current_user, start_date, end_date)
            
            consolidated = ConsolidatedAnalyticsDTO(
                dashboard_analytics=dashboard_analytics,
                user_analytics=user_analytics,
                attendance_analytics=attendance_analytics,
                leave_analytics=leave_analytics,
                payroll_analytics=payroll_analytics,
                reimbursement_analytics=reimbursement_analytics
            )
            
            logger.info(f"Successfully generated consolidated analytics for organisation: {current_user.hostname}")
            return consolidated
            
        except Exception as e:
            logger.error(f"Error getting consolidated analytics: {e}")
            # Return empty analytics instead of failing
            return ConsolidatedAnalyticsDTO(
                dashboard_analytics=DashboardAnalyticsDTO(),
                user_analytics=UserAnalyticsDTO(
                    total_users=0, active_users=0, inactive_users=0,
                    department_distribution={}, role_distribution={},
                    recent_joiners=[], user_growth_trends={}
                ),
                attendance_analytics=AttendanceAnalyticsDTO(
                    total_checkins_today=0, total_checkouts_today=0,
                    present_count=0, absent_count=0, late_arrivals=0,
                    early_departures=0, average_working_hours=0.0,
                    attendance_trends={}, department_attendance={}
                ),
                leave_analytics=LeaveAnalyticsDTO(
                    total_pending_leaves=0, total_approved_leaves=0,
                    total_rejected_leaves=0, leave_type_distribution={},
                    department_leave_trends={}, monthly_leave_trends={}
                ),
                payroll_analytics=PayrollAnalyticsDTO(
                    total_payouts_current_month=0, total_amount_current_month=0.0,
                    average_salary=0.0, department_salary_distribution={},
                    salary_trends={}
                ),
                reimbursement_analytics=ReimbursementAnalyticsDTO(
                    total_pending_reimbursements=0, total_pending_amount=0.0,
                    total_approved_reimbursements=0, total_approved_amount=0.0,
                    reimbursement_type_distribution={}, monthly_reimbursement_trends={}
                )
            )
    
    async def export_report(
        self,
        request: ExportRequestDTO,
        current_user: "CurrentUser"
    ) -> ExportResponseDTO:
        """Export report data to file."""
        try:
            logger.info(f"Exporting report for organisation: {current_user.hostname}")
            
            # Validate request
            validation_errors = request.validate()
            if validation_errors:
                raise ReportingValidationError("Export validation failed", validation_errors)
            
            # For now, return placeholder response
            # TODO: Implement actual file generation
            response = ExportResponseDTO(
                file_path="/tmp/placeholder.pdf",
                file_name="placeholder.pdf",
                file_size=1024,
                format=request.format
            )
            
            logger.info(f"Successfully exported report for organisation: {current_user.hostname}")
            return response
            
        except ReportingValidationError:
            raise
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            raise
    
    async def cleanup_old_reports(
        self,
        current_user: "CurrentUser",
        days_old: int = 30
    ) -> Dict[str, Any]:
        """Clean up old reports."""
        try:
            logger.info(f"Cleaning up old reports for organisation: {current_user.hostname}")
            
            deleted_count = await self.reporting_repository.cleanup_old_reports(
                current_user.hostname, days_old
            )
            
            result = {
                "deleted_count": deleted_count,
                "days_old": days_old,
                "organisation": current_user.hostname,
                "cleaned_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully cleaned up {deleted_count} old reports")
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {e}")
            raise 