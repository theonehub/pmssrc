"""
Reporting Controller
Handles HTTP requests for reporting operations
"""

import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

from app.application.interfaces.services.reporting_service import ReportingService
from app.application.dto.reporting_dto import (
    CreateReportRequestDTO, UpdateReportRequestDTO, ReportSearchFiltersDTO,
    ReportResponseDTO, ReportListResponseDTO, DashboardAnalyticsDTO,
    UserAnalyticsDTO, AttendanceAnalyticsDTO, LeaveAnalyticsDTO,
    PayrollAnalyticsDTO, ReimbursementAnalyticsDTO, ConsolidatedAnalyticsDTO,
    ExportRequestDTO, ExportResponseDTO, ReportingValidationError,
    ReportingNotFoundError, ReportingBusinessRuleError, ReportingConflictError
)
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class ReportingController:
    """
    Controller for reporting operations.
    
    Handles HTTP requests and delegates to service layer.
    Follows SOLID principles:
    - SRP: Only handles HTTP concerns
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with other controllers
    - ISP: Focused interface for reporting HTTP operations
    - DIP: Depends on service abstraction
    """
    
    def __init__(self, reporting_service: ReportingService):
        """Initialize controller with reporting service."""
        self.reporting_service = reporting_service
    
    async def create_report(
        self, 
        request: CreateReportRequestDTO, 
        current_user: CurrentUser
    ) -> ReportResponseDTO:
        """Create a new report."""
        try:
            logger.info(f"Creating report '{request.name}' for user: {current_user.employee_id}")
            
            result = await self.reporting_service.create_report(request, current_user)
            
            logger.info(f"Successfully created report: {result.id}")
            return result
            
        except ReportingValidationError as e:
            logger.warning(f"Validation error creating report: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": str(e),
                    "errors": e.errors,
                    "type": "validation_error"
                }
            )
        except ReportingBusinessRuleError as e:
            logger.warning(f"Business rule error creating report: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": str(e),
                    "rule": e.rule,
                    "type": "business_rule_error"
                }
            )
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error creating report",
                    "type": "internal_error"
                }
            )
    
    async def get_report_by_id(
        self, 
        report_id: str, 
        current_user: CurrentUser
    ) -> ReportResponseDTO:
        """Get report by ID."""
        try:
            logger.info(f"Getting report {report_id} for user: {current_user.employee_id}")
            
            result = await self.reporting_service.get_report_by_id(report_id, current_user)
            
            if not result:
                raise ReportingNotFoundError(report_id)
            
            logger.info(f"Successfully retrieved report: {report_id}")
            return result
            
        except ReportingNotFoundError as e:
            logger.warning(f"Report not found: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": str(e),
                    "report_id": e.report_id,
                    "type": "not_found_error"
                }
            )
        except Exception as e:
            logger.error(f"Error getting report {report_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error getting report",
                    "type": "internal_error"
                }
            )
    
    async def list_reports(
        self, 
        filters: ReportSearchFiltersDTO, 
        current_user: CurrentUser
    ) -> ReportListResponseDTO:
        """List reports with filters and pagination."""
        try:
            logger.info(f"Listing reports for user: {current_user.employee_id}")
            
            result = await self.reporting_service.list_reports(filters, current_user)
            
            logger.info(f"Successfully listed {len(result.reports)} reports")
            return result
            
        except ReportingValidationError as e:
            logger.warning(f"Validation error listing reports: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": str(e),
                    "errors": e.errors,
                    "type": "validation_error"
                }
            )
        except Exception as e:
            logger.error(f"Error listing reports: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error listing reports",
                    "type": "internal_error"
                }
            )
    
    async def update_report(
        self,
        report_id: str,
        request: UpdateReportRequestDTO,
        current_user: CurrentUser
    ) -> ReportResponseDTO:
        """Update an existing report."""
        try:
            logger.info(f"Updating report {report_id} for user: {current_user.employee_id}")
            
            result = await self.reporting_service.update_report(report_id, request, current_user)
            
            logger.info(f"Successfully updated report: {report_id}")
            return result
            
        except ReportingValidationError as e:
            logger.warning(f"Validation error updating report: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": str(e),
                    "errors": e.errors,
                    "type": "validation_error"
                }
            )
        except ReportingNotFoundError as e:
            logger.warning(f"Report not found for update: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": str(e),
                    "report_id": e.report_id,
                    "type": "not_found_error"
                }
            )
        except Exception as e:
            logger.error(f"Error updating report {report_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error updating report",
                    "type": "internal_error"
                }
            )
    
    async def delete_report(
        self,
        report_id: str,
        current_user: CurrentUser
    ) -> Dict[str, Any]:
        """Delete a report."""
        try:
            logger.info(f"Deleting report {report_id} for user: {current_user.employee_id}")
            
            success = await self.reporting_service.delete_report(report_id, current_user)
            
            if success:
                logger.info(f"Successfully deleted report: {report_id}")
                return {
                    "message": "Report deleted successfully",
                    "report_id": report_id,
                    "deleted": True
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "message": "Failed to delete report",
                        "type": "deletion_error"
                    }
                )
            
        except ReportingNotFoundError as e:
            logger.warning(f"Report not found for deletion: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": str(e),
                    "report_id": e.report_id,
                    "type": "not_found_error"
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting report {report_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error deleting report",
                    "type": "internal_error"
                }
            )
    
    async def get_dashboard_analytics(
        self, 
        current_user: CurrentUser
    ) -> DashboardAnalyticsDTO:
        """Get consolidated dashboard analytics."""
        try:
            logger.info(f"Getting dashboard analytics for user: {current_user.employee_id}")
            
            result = await self.reporting_service.get_dashboard_analytics(current_user)
            
            logger.info(f"Successfully retrieved dashboard analytics")
            return result
            
        except Exception as e:
            logger.error(f"Error getting dashboard analytics: {e}")
            # Return empty analytics instead of failing
            return DashboardAnalyticsDTO()
    
    async def get_user_analytics(
        self, 
        current_user: CurrentUser
    ) -> UserAnalyticsDTO:
        """Get user analytics data."""
        try:
            logger.info(f"Getting user analytics for user: {current_user.employee_id}")
            
            result = await self.reporting_service.get_user_analytics(current_user)
            
            logger.info(f"Successfully retrieved user analytics")
            return result
            
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
        current_user: CurrentUser,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> AttendanceAnalyticsDTO:
        """Get attendance analytics data."""
        try:
            logger.info(f"Getting attendance analytics for user: {current_user.employee_id}")
            
            result = await self.reporting_service.get_attendance_analytics(
                current_user, start_date, end_date
            )
            
            logger.info(f"Successfully retrieved attendance analytics")
            return result
            
        except Exception as e:
            logger.error(f"Error getting attendance analytics: {e}")
            # Return empty analytics instead of failing
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
        current_user: CurrentUser,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> LeaveAnalyticsDTO:
        """Get leave analytics data."""
        try:
            logger.info(f"Getting leave analytics for user: {current_user.employee_id}")
            
            result = await self.reporting_service.get_leave_analytics(
                current_user, start_date, end_date
            )
            
            logger.info(f"Successfully retrieved leave analytics")
            return result
            
        except Exception as e:
            logger.error(f"Error getting leave analytics: {e}")
            # Return empty analytics instead of failing
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
        current_user: CurrentUser,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> PayrollAnalyticsDTO:
        """Get payroll analytics data."""
        try:
            logger.info(f"Getting payroll analytics for user: {current_user.employee_id}")
            
            result = await self.reporting_service.get_payroll_analytics(
                current_user, start_date, end_date
            )
            
            logger.info(f"Successfully retrieved payroll analytics")
            return result
            
        except Exception as e:
            logger.error(f"Error getting payroll analytics: {e}")
            # Return empty analytics instead of failing
            return PayrollAnalyticsDTO(
                total_payouts_current_month=0,
                total_amount_current_month=0.0,
                average_salary=0.0,
                department_salary_distribution={},
                salary_trends={},
                total_tds_current_month=0.0,
                average_tds_per_employee=0.0,
                tds_trends={},
                department_tds_distribution={}
            )
    
    async def get_reimbursement_analytics(
        self, 
        current_user: CurrentUser,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> ReimbursementAnalyticsDTO:
        """Get reimbursement analytics data."""
        try:
            logger.info(f"Getting reimbursement analytics for user: {current_user.employee_id}")
            
            result = await self.reporting_service.get_reimbursement_analytics(
                current_user, start_date, end_date
            )
            
            logger.info(f"Successfully retrieved reimbursement analytics")
            return result
            
        except Exception as e:
            logger.error(f"Error getting reimbursement analytics: {e}")
            # Return empty analytics instead of failing
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
        current_user: CurrentUser,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> ConsolidatedAnalyticsDTO:
        """Get consolidated analytics from all modules."""
        try:
            logger.info(f"Getting consolidated analytics for user: {current_user.employee_id}")
            
            result = await self.reporting_service.get_consolidated_analytics(
                current_user, start_date, end_date
            )
            
            logger.info(f"Successfully retrieved consolidated analytics")
            return result
            
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
                    salary_trends={},
                    total_tds_current_month=0.0,
                    average_tds_per_employee=0.0,
                    tds_trends={},
                    department_tds_distribution={}
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
        current_user: CurrentUser
    ) -> ExportResponseDTO:
        """Export report data to file."""
        try:
            logger.info(f"Exporting report for user: {current_user.employee_id}")
            
            result = await self.reporting_service.export_report(request, current_user)
            
            logger.info(f"Successfully exported report")
            return result
            
        except ReportingValidationError as e:
            logger.warning(f"Validation error exporting report: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": str(e),
                    "errors": e.errors,
                    "type": "validation_error"
                }
            )
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error exporting report",
                    "type": "internal_error"
                }
            )
    
    async def cleanup_old_reports(
        self,
        current_user: CurrentUser,
        days_old: int = 30
    ) -> Dict[str, Any]:
        """Clean up old reports."""
        try:
            logger.info(f"Cleaning up old reports for user: {current_user.employee_id}")
            
            result = await self.reporting_service.cleanup_old_reports(current_user, days_old)
            
            logger.info(f"Successfully cleaned up old reports")
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error cleaning up reports",
                    "type": "internal_error"
                }
            ) 