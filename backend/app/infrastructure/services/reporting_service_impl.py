"""
Reporting Service Implementation
Concrete implementation of reporting service
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, timedelta

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
            recent_joiners = [
                {
                    "employee_id": user.employee_id.value,
                    "name": user.name,
                    "department": user.department,
                    "date_of_joining": user.date_of_joining
                }
                for user in users 
                if user.created_at and user.created_at >= datetime.utcnow() - timedelta(days=30)
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
        """Get payroll analytics data from taxation records."""
        try:
            logger.info(f"Getting payroll analytics for organisation: {current_user.hostname}")
            
            # Get current month/year for default filtering
            from datetime import datetime, date
            current_date = datetime.now()
            
            # For now, we'll get all taxation records and aggregate payroll data
            # This would be optimized in production with proper indexes and aggregation pipelines
            
            # Get organization ID from hostname
            organization_id = current_user.hostname
            
            # Initialize aggregation variables
            total_payouts = 0
            total_gross_amount = 0.0
            total_net_amount = 0.0
            total_deductions = 0.0
            total_tds = 0.0
            employee_salaries = []
            employee_tds_amounts = []
            department_breakdown = {}
            salary_trends = {}
            tds_trends = {}
            department_tds_breakdown = {}
            
            try:
                # Import taxation repository to get records
                from app.config.dependency_container import DependencyContainer
                from app.domain.value_objects.tax_year import TaxYear
                
                container = DependencyContainer()
                taxation_repository = container.get_salary_package_repository()
                
                # Get current tax year
                current_tax_year = str(TaxYear.current())
                
                # Get all taxation records for current tax year
                taxation_records = await taxation_repository.get_by_tax_year(
                    tax_year=current_tax_year,
                    organization_id=organization_id,
                    limit=1000  # Increase limit for analytics
                )
                
                logger.info(f"Found {len(taxation_records)} taxation records for analytics")
                
                # Process each taxation record
                for record in taxation_records:
                    # Check if record has monthly payroll data
                    if hasattr(record, 'monthly_payroll') and record.monthly_payroll:
                        payroll = record.monthly_payroll
                        
                        # Aggregate totals
                        total_payouts += 1
                        total_gross_amount += payroll.gross_salary
                        total_net_amount += payroll.net_salary
                        total_deductions += payroll.total_deductions
                        
                        # Aggregate TDS data
                        payroll_tds = getattr(payroll, 'tds', 0.0)
                        total_tds += payroll_tds
                        
                        # Store individual amounts for average calculations
                        employee_salaries.append(payroll.gross_salary)
                        employee_tds_amounts.append(payroll_tds)
                        
                        # Department breakdown (we'll need to get department from user data)
                        # For now, using a placeholder
                        dept_name = "General"  # Would be fetched from user repository
                        if dept_name not in department_breakdown:
                            department_breakdown[dept_name] = {
                                "count": 0,
                                "total_gross": 0.0,
                                "total_net": 0.0,
                                "average_gross": 0.0
                            }
                        
                        if dept_name not in department_tds_breakdown:
                            department_tds_breakdown[dept_name] = {
                                "count": 0,
                                "total_tds": 0.0,
                                "average_tds": 0.0
                            }
                        
                        department_breakdown[dept_name]["count"] += 1
                        department_breakdown[dept_name]["total_gross"] += payroll.gross_salary
                        department_breakdown[dept_name]["total_net"] += payroll.net_salary
                        
                        department_tds_breakdown[dept_name]["count"] += 1
                        department_tds_breakdown[dept_name]["total_tds"] += payroll_tds
                    
                    # Fallback to salary income if no monthly payroll
                    elif hasattr(record, 'salary_income') and record.salary_income:
                        salary_income = record.salary_income
                        
                        # Calculate monthly equivalent
                        annual_gross = salary_income.calculate_gross_salary()
                        monthly_gross = annual_gross.to_float() / 12
                        
                        # Estimate monthly net (assuming 20% deductions)
                        monthly_net = monthly_gross * 0.8
                        monthly_deductions = monthly_gross * 0.2
                        
                        # Estimate monthly TDS from annual tax liability if available
                        monthly_tds = 0.0
                        if hasattr(record, 'annual_tax_liability') and record.annual_tax_liability:
                            try:
                                annual_tax = float(record.annual_tax_liability)
                                monthly_tds = annual_tax / 12
                            except (ValueError, TypeError):
                                monthly_tds = 0.0
                        else:
                            # Fallback: estimate TDS as 10% of monthly gross (rough estimate)
                            monthly_tds = monthly_gross * 0.1
                        
                        # Aggregate totals
                        total_payouts += 1
                        total_gross_amount += monthly_gross
                        total_net_amount += monthly_net
                        total_deductions += monthly_deductions
                        total_tds += monthly_tds
                        
                        # Store individual amounts for average calculations
                        employee_salaries.append(monthly_gross)
                        employee_tds_amounts.append(monthly_tds)
                
                # Calculate department averages
                for dept_data in department_breakdown.values():
                    if dept_data["count"] > 0:
                        dept_data["average_gross"] = dept_data["total_gross"] / dept_data["count"]
                
                # Calculate department TDS averages
                for dept_name, dept_tds_data in department_tds_breakdown.items():
                    if dept_tds_data["count"] > 0:
                        dept_tds_data["average_tds"] = dept_tds_data["total_tds"] / dept_tds_data["count"]
                
                # Generate monthly trends (simplified - would be more sophisticated in production)
                current_month = current_date.strftime("%Y-%m")
                salary_trends = {
                    current_month: {
                        "total_payouts": round(total_payouts, 0),
                        "total_amount": round(total_gross_amount, 0),
                        "average_salary": round(sum(employee_salaries) / len(employee_salaries) if employee_salaries else 0.0, 0)
                    }
                }
                
                # Generate TDS trends
                tds_trends = {
                    current_month: {
                        "total_tds": round(total_tds, 0),
                        "average_tds": round(sum(employee_tds_amounts) / len(employee_tds_amounts) if employee_tds_amounts else 0.0, 0),
                        "tds_percentage": round((total_tds / total_gross_amount * 100) if total_gross_amount > 0 else 0.0, 2)
                    }
                }
                
                logger.info(f"Processed payroll analytics: {total_payouts} payouts, ₹{total_gross_amount:.2f} total, ₹{total_tds:.2f} TDS")
                
            except Exception as e:
                logger.warning(f"Error processing taxation records for payroll analytics: {e}")
                # Return empty data if taxation processing fails
                pass
            
            # Calculate average salary and TDS
            average_salary = sum(employee_salaries) / len(employee_salaries) if employee_salaries else 0.0
            average_tds = sum(employee_tds_amounts) / len(employee_tds_amounts) if employee_tds_amounts else 0.0
            
            analytics = PayrollAnalyticsDTO(
                total_payouts_current_month=round(total_payouts, 0),
                total_amount_current_month=round(total_gross_amount, 0),
                average_salary=round(average_salary, 0),
                department_salary_distribution=department_breakdown,
                salary_trends=salary_trends,
                
                # TDS Analytics
                total_tds_current_month=round(total_tds, 0),
                average_tds_per_employee=round(average_tds, 0),
                tds_trends=tds_trends,
                department_tds_distribution=department_tds_breakdown
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
                salary_trends={},
                total_tds_current_month=0,
                average_tds_per_employee=0.0,
                tds_trends={},
                department_tds_distribution={}
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
            
            # Parse dates or use defaults
            if start_date and end_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                # Default to last 30 days
                end_dt = datetime.utcnow()
                start_dt = end_dt - timedelta(days=30)
            
            # Get pending reimbursements with timespan
            pending_reimbursements = await self.reimbursement_repository.get_pending_reimbursements_by_timespan(
                current_user.hostname, start_dt, end_dt
            )
            
            # Get approved reimbursements with timespan
            approved_reimbursements = await self.reimbursement_repository.get_approved_reimbursements_by_timespan(
                current_user.hostname, start_dt, end_dt
            )
            
            # Calculate statistics
            pending_count = len(pending_reimbursements)
            pending_amount = float(sum(
                reimbursement.amount for reimbursement in pending_reimbursements
            ))
            
            approved_count = len(approved_reimbursements)
            approved_amount = float(sum(
                reimbursement.amount for reimbursement in approved_reimbursements
            ))
            
            # Create type distribution
            type_distribution = {}
            for reimbursement in pending_reimbursements + approved_reimbursements:
                category = reimbursement.reimbursement_type.category_name
                if category not in type_distribution:
                    type_distribution[category] = {"count": 0, "amount": 0.0}
                type_distribution[category]["count"] += 1
                type_distribution[category]["amount"] += float(reimbursement.amount)
            
            # Create monthly trends (simplified)
            monthly_trends = {}
            current_month = end_dt.strftime("%Y-%m")
            monthly_trends[current_month] = {
                "pending": {"count": pending_count, "amount": float(pending_amount)},
                "approved": {"count": approved_count, "amount": float(approved_amount)}
            }
            
            analytics = ReimbursementAnalyticsDTO(
                total_pending_reimbursements=pending_count,
                total_pending_amount=pending_amount,
                total_approved_reimbursements=approved_count,
                total_approved_amount=approved_amount,
                reimbursement_type_distribution=type_distribution,
                monthly_reimbursement_trends=monthly_trends
            )
            
            logger.info(f"Successfully generated reimbursement analytics: {pending_count} pending, {approved_count} approved")
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
                    salary_trends={},
                    total_tds_current_month=0,
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