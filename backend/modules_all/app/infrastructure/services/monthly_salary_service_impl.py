"""
Monthly Salary Service Implementation
Implementation of monthly salary business operations
"""

import logging
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from app.application.interfaces.services.monthly_salary_service import MonthlySalaryService
from app.application.interfaces.repositories.monthly_salary_repository import MonthlySalaryRepository
from app.application.interfaces.repositories.user_repository import UserRepository
from app.application.interfaces.repositories.taxation_repository import TaxationRepository
from app.application.use_cases.monthly_salary.get_monthly_salary_use_case import GetMonthlySalaryUseCase
from app.application.use_cases.monthly_salary.get_monthly_salaries_for_period_use_case import GetMonthlySalariesForPeriodUseCase
from app.application.dto.monthly_salary_dto import (
    MonthlySalaryResponseDTO,
    MonthlySalaryListResponseDTO,
    MonthlySalaryFilterDTO,
    MonthlySalaryComputeRequestDTO,
    MonthlySalaryBulkComputeRequestDTO,
    MonthlySalaryBulkComputeResponseDTO,
    MonthlySalaryStatusUpdateRequestDTO,
    MonthlySalaryPaymentRequestDTO,
    MonthlySalarySummaryDTO
)
from app.domain.services.taxation.tax_calculation_service import TaxCalculationService
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.entities.monthly_salary import ProcessingStatus

if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class MonthlySalaryServiceImpl(MonthlySalaryService):
    """Implementation of monthly salary service."""
    
    def __init__(
        self,
        monthly_salary_repository: MonthlySalaryRepository,
        user_repository: UserRepository,
        taxation_repository: TaxationRepository,
        tax_calculation_service: TaxCalculationService
    ):
        """
        Initialize service with dependencies.
        
        Args:
            monthly_salary_repository: Monthly salary repository
            user_repository: User repository
            taxation_repository: Taxation repository
            tax_calculation_service: Tax calculation service
        """
        self.monthly_salary_repository = monthly_salary_repository
        self.user_repository = user_repository
        self.taxation_repository = taxation_repository
        self.tax_calculation_service = tax_calculation_service
        
        # Initialize use cases
        self._get_monthly_salary_use_case = GetMonthlySalaryUseCase(
            monthly_salary_repository=monthly_salary_repository,
            user_repository=user_repository,
            taxation_repository=taxation_repository,
            tax_calculation_service=tax_calculation_service
        )
        
        self._get_monthly_salaries_for_period_use_case = GetMonthlySalariesForPeriodUseCase(
            monthly_salary_repository=monthly_salary_repository,
            user_repository=user_repository
        )
    
    async def get_monthly_salary(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        current_user: "CurrentUser"
    ) -> Optional[MonthlySalaryResponseDTO]:
        """Get monthly salary for an employee."""
        try:
            logger.info(f"Getting monthly salary for employee {employee_id}, {month}/{year}")
            
            return await self._get_monthly_salary_use_case.execute(
                employee_id=employee_id,
                month=month,
                year=year,
                current_user=current_user
            )
            
        except Exception as e:
            logger.error(f"Error getting monthly salary for {employee_id}: {e}")
            raise
    
    async def get_monthly_salaries_for_period(
        self, 
        month: int, 
        year: int, 
        current_user: "CurrentUser",
        filters: Optional[MonthlySalaryFilterDTO] = None
    ) -> MonthlySalaryListResponseDTO:
        """Get all monthly salaries for a period."""
        try:
            logger.info(f"Getting monthly salaries for period {month}/{year}")
            
            return await self._get_monthly_salaries_for_period_use_case.execute(
                month=month,
                year=year,
                current_user=current_user,
                filters=filters
            )
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries for period {month}/{year}: {e}")
            raise
    
    async def compute_monthly_salary(
        self, 
        request: MonthlySalaryComputeRequestDTO, 
        current_user: "CurrentUser"
    ) -> MonthlySalaryResponseDTO:
        """Compute monthly salary for an employee."""
        try:
            logger.info(f"Computing monthly salary for employee {request.employee_id}, {request.month}/{request.year}")
            
            employee_id_obj = EmployeeId(request.employee_id)
            hostname = current_user.hostname
            
            # Check if already computed and force_recompute is False
            if not request.force_recompute:
                existing = await self.monthly_salary_repository.get_by_employee_month_year(
                    employee_id_obj, request.month, request.year, hostname
                )
                if existing and existing.status.value in [ProcessingStatus.COMPUTED, ProcessingStatus.APPROVED, ProcessingStatus.PAID]:
                    logger.info(f"Monthly salary already computed for {request.employee_id}")
                    # Return existing computed salary
                    user = await self.user_repository.get_by_id(employee_id_obj, hostname)
                    return self._convert_entity_to_dto(existing, user)
            
            # Get employee details
            user = await self.user_repository.get_by_id(employee_id_obj, hostname)
            if not user:
                raise ValueError(f"Employee not found: {request.employee_id}")
            
            # Get taxation record
            taxation_record = await self.taxation_repository.get_by_user_and_year(
                employee_id_obj, request.tax_year, hostname
            )
            
            if not taxation_record:
                logger.error(f"No taxation record found for employee {request.employee_id}, tax year {request.tax_year}")
            
            # Calculate tax if not already calculated
            if not taxation_record.calculation_result:
                calculation_result = await self.tax_calculation_service.calculate_comprehensive_tax(taxation_record)
                taxation_record.update_calculation_result(calculation_result)
            else:
                calculation_result = taxation_record.calculation_result
            
            # Create monthly payout projection
            monthly_projection = self.tax_calculation_service._create_monthly_payout_from_taxation_record(
                taxation_record, calculation_result
            )
            
            # Create or update monthly salary entity
            from app.domain.entities.monthly_salary import MonthlySalary
            
            monthly_salary = MonthlySalary.from_taxation_projection(
                employee_id=employee_id_obj,
                month=request.month,
                year=request.year,
                tax_year=request.tax_year,
                organization_id=current_user.hostname,
                monthly_projection=monthly_projection,
                created_by=request.computed_by or current_user.employee_id
            )
            
            # Mark as computed
            monthly_salary.mark_as_computed(request.computed_by or current_user.employee_id)
            
            # Save to repository
            saved_monthly_salary = await self.monthly_salary_repository.save(monthly_salary, hostname)
            
            logger.info(f"Successfully computed monthly salary for {request.employee_id}")
            
            return self._convert_entity_to_dto(saved_monthly_salary, user)
            
        except Exception as e:
            logger.error(f"Error computing monthly salary for {request.employee_id}: {e}")
            raise
    
    async def bulk_compute_monthly_salaries(
        self, 
        request: MonthlySalaryBulkComputeRequestDTO, 
        current_user: "CurrentUser"
    ) -> MonthlySalaryBulkComputeResponseDTO:
        """Bulk compute monthly salaries."""
        try:
            logger.info(f"Bulk computing monthly salaries for {request.month}/{request.year}")
            
            hostname = current_user.hostname
            
            # Get list of employees to process
            if request.employee_ids:
                employee_ids = request.employee_ids
            else:
                # Get all active employees in the organization
                users = await self.user_repository.get_active_users(hostname)
                employee_ids = [str(user.employee_id) for user in users]
            
            # Initialize counters
            total_requested = len(employee_ids)
            successful = 0
            failed = 0
            skipped = 0
            errors = []
            
            # Process each employee
            for employee_id in employee_ids:
                try:
                    # Check if already computed and not force_recompute
                    if not request.force_recompute:
                        existing = await self.monthly_salary_repository.get_by_employee_month_year(
                            EmployeeId(employee_id), request.month, request.year, hostname
                        )
                        if existing and existing.status.value in [ProcessingStatus.COMPUTED, ProcessingStatus.APPROVED, ProcessingStatus.PAID]:
                            skipped += 1
                            continue
                    
                    # Create compute request for individual employee
                    individual_request = MonthlySalaryComputeRequestDTO(
                        employee_id=employee_id,
                        month=request.month,
                        year=request.year,
                        tax_year=request.tax_year,
                        force_recompute=request.force_recompute,
                        computed_by=request.computed_by
                    )
                    
                    # Compute monthly salary
                    await self.compute_monthly_salary(individual_request, current_user)
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    errors.append({
                        "employee_id": employee_id,
                        "error": str(e)
                    })
                    logger.error(f"Error computing monthly salary for {employee_id}: {e}")
            
            # Get summary statistics
            summary = await self.monthly_salary_repository.get_summary_by_month_year(
                request.month, request.year, hostname
            )
            
            logger.info(f"Bulk computation completed: {successful} successful, {failed} failed, {skipped} skipped")
            
            return MonthlySalaryBulkComputeResponseDTO(
                total_requested=total_requested,
                successful=successful,
                failed=failed,
                skipped=skipped,
                errors=errors,
                computation_summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error in bulk compute: {e}")
            raise
    
    async def update_monthly_salary_status(
        self, 
        request: MonthlySalaryStatusUpdateRequestDTO, 
        current_user: "CurrentUser"
    ) -> MonthlySalaryResponseDTO:
        """Update monthly salary status."""
        try:
            logger.info(f"Updating status for {request.employee_id}, {request.month}/{request.year} to {request.status}")
            
            employee_id_obj = EmployeeId(request.employee_id)
            hostname = current_user.hostname
            
            # Get existing monthly salary
            monthly_salary = await self.monthly_salary_repository.get_by_employee_month_year(
                employee_id_obj, request.month, request.year, hostname
            )
            
            if not monthly_salary:
                raise ValueError(f"Monthly salary not found for {request.employee_id}, {request.month}/{request.year}")
            
            # Update status based on the requested status
            updated_by = request.updated_by or current_user.employee_id
            
            if request.status == ProcessingStatus.APPROVED:
                monthly_salary.approve_salary(
                    approved_by=updated_by,
                    remarks=request.notes
                )
            elif request.status == ProcessingStatus.REJECTED:
                monthly_salary.reject_salary(
                    rejected_by=updated_by,
                    reason=request.notes
                )
            elif request.status == ProcessingStatus.SALARY_PAID:
                monthly_salary.mark_salary_as_paid(
                    paid_by=updated_by,
                    payment_notes=request.notes
                )
            elif request.status == ProcessingStatus.TDS_PAID:
                monthly_salary.mark_tds_as_paid(
                    paid_by=updated_by,
                    payment_notes=request.notes
                )
            elif request.status == ProcessingStatus.PAID:
                monthly_salary.mark_as_paid(
                    paid_by=updated_by,
                    payment_notes=request.notes
                )
            elif request.status == ProcessingStatus.COMPUTED:
                monthly_salary.mark_as_computed(
                    computed_by=updated_by,
                    notes=request.notes
                )
            else:
                # For other statuses, update directly
                monthly_salary.status = ProcessingStatus(request.status)
                monthly_salary.updated_at = datetime.utcnow()
                monthly_salary.updated_by = updated_by
                if request.notes:
                    monthly_salary.notes = request.notes
            
            # Save updated entity
            saved_monthly_salary = await self.monthly_salary_repository.save(monthly_salary, hostname)
            
            # Get employee details for response
            user = await self.user_repository.get_by_id(employee_id_obj, hostname)
            
            logger.info(f"Successfully updated status for {request.employee_id}")
            
            return self._convert_entity_to_dto(saved_monthly_salary, user)
            
        except Exception as e:
            logger.error(f"Error updating status for {request.employee_id}: {e}")
            raise
    
    async def mark_salary_payment(
        self, 
        request: MonthlySalaryPaymentRequestDTO, 
        current_user: "CurrentUser"
    ) -> MonthlySalaryResponseDTO:
        """Mark salary payment (salary, TDS, or both)."""
        try:
            logger.info(f"Marking {request.payment_type} payment for {request.employee_id}, {request.month}/{request.year}")
            
            employee_id_obj = EmployeeId(request.employee_id)
            hostname = current_user.hostname
            
            # Get existing monthly salary
            monthly_salary = await self.monthly_salary_repository.get_by_employee_month_year(
                employee_id_obj, request.month, request.year, hostname
            )
            
            if not monthly_salary:
                raise ValueError(f"Monthly salary not found for {request.employee_id}, {request.month}/{request.year}")
            
            # Handle payment based on type
            paid_by = request.paid_by or current_user.employee_id
            
            if request.payment_type == "salary":
                monthly_salary.mark_salary_as_paid(
                    paid_by=paid_by,
                    payment_reference=request.payment_reference,
                    payment_notes=request.payment_notes
                )
            elif request.payment_type == "tds":
                monthly_salary.mark_tds_as_paid(
                    paid_by=paid_by,
                    payment_reference=request.payment_reference,
                    payment_notes=request.payment_notes
                )
            elif request.payment_type == "both":
                monthly_salary.mark_as_paid(
                    paid_by=paid_by,
                    payment_notes=request.payment_notes
                )
                # Set payment references for both
                if request.payment_reference:
                    monthly_salary.salary_payment_reference = request.payment_reference
                    monthly_salary.tds_payment_reference = request.payment_reference
            else:
                raise ValueError(f"Invalid payment type: {request.payment_type}")
            
            # Save updated entity
            saved_monthly_salary = await self.monthly_salary_repository.save(monthly_salary, hostname)
            
            # Get employee details for response
            user = await self.user_repository.get_by_id(employee_id_obj, hostname)
            
            logger.info(f"Successfully marked {request.payment_type} payment for {request.employee_id}")
            
            return self._convert_entity_to_dto(saved_monthly_salary, user)
            
        except Exception as e:
            logger.error(f"Error marking payment for {request.employee_id}: {e}")
            raise
    
    async def get_monthly_salary_summary(
        self, 
        month: int, 
        year: int, 
        current_user: "CurrentUser"
    ) -> MonthlySalarySummaryDTO:
        """Get monthly salary summary for a period."""
        try:
            logger.info(f"Getting summary for {month}/{year}")
            
            hostname = current_user.hostname
            
            # Get summary from repository
            summary = await self.monthly_salary_repository.get_summary_by_month_year(
                month, year, hostname
            )
            
            # Determine tax year
            tax_year = self._get_tax_year(month, year)
            
            return MonthlySalarySummaryDTO(
                month=month,
                year=year,
                tax_year=tax_year,
                total_employees=summary.get("total_employees", 0),
                computed_count=summary.get("computed_count", 0),
                pending_count=summary.get("pending_count", 0),
                approved_count=summary.get("approved_count", 0),
                paid_count=summary.get("paid_count", 0),
                total_gross_payroll=summary.get("total_gross_payroll", 0.0),
                total_net_payroll=summary.get("total_net_payroll", 0.0),
                total_deductions=summary.get("total_deductions", 0.0),
                total_tds=summary.get("total_tds", 0.0),
                computation_completion_rate=summary.get("computation_completion_rate", 0.0),
                last_computed_at=None,  # Can be enhanced later
                next_processing_date=None  # Can be enhanced later
            )
            
        except Exception as e:
            logger.error(f"Error getting summary for {month}/{year}: {e}")
            raise
    
    async def delete_monthly_salary(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        current_user: "CurrentUser"
    ) -> bool:
        """Delete monthly salary record."""
        try:
            logger.info(f"Deleting monthly salary for {employee_id}, {month}/{year}")
            
            employee_id_obj = EmployeeId(employee_id)
            hostname = current_user.hostname
            
            # Check if record exists and can be deleted
            existing = await self.monthly_salary_repository.get_by_employee_month_year(
                employee_id_obj, month, year, hostname
            )
            
            if not existing:
                return False
            
            # Check if status allows deletion (e.g., not paid)
            if existing.status.value == ProcessingStatus.PAID:
                raise ValueError("Cannot delete paid salary record")
            
            # Delete the record
            deleted = await self.monthly_salary_repository.delete_by_employee_month_year(
                employee_id_obj, month, year, hostname
            )
            
            logger.info(f"Successfully deleted monthly salary for {employee_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting monthly salary for {employee_id}: {e}")
            raise
    
    def _convert_entity_to_dto(self, monthly_salary, user) -> MonthlySalaryResponseDTO:
        """Convert monthly salary entity to DTO with employee details."""
        return MonthlySalaryResponseDTO(
            employee_id=str(monthly_salary.employee_id),
            month=monthly_salary.month,
            year=monthly_salary.year,
            tax_year=monthly_salary.tax_year,
            
            # Employee info
            employee_name=user.name if user else "Unknown",
            employee_email=user.email if user else None,
            department=user.department if user else None,
            designation=user.designation if user else None,
            
            # Salary components
            basic_salary=monthly_salary.basic_salary.to_float(),
            da=monthly_salary.da.to_float(),
            hra=monthly_salary.hra.to_float(),
            special_allowance=monthly_salary.special_allowance.to_float(),
            bonus=monthly_salary.bonus.to_float(),
            commission=monthly_salary.commission.to_float(),
            
            # Deductions
            epf_employee=monthly_salary.epf_employee.to_float(),
            esi_employee=monthly_salary.esi_employee.to_float(),
            professional_tax=monthly_salary.professional_tax.to_float(),
            tds=monthly_salary.tds.to_float(),
            advance_deduction=monthly_salary.advance_deduction.to_float(),
            loan_deduction=monthly_salary.loan_deduction.to_float(),
            other_deductions=monthly_salary.other_deductions.to_float(),
            
            # Calculated totals
            gross_salary=monthly_salary.gross_salary.to_float(),
            total_deductions=monthly_salary.total_deductions.to_float(),
            net_salary=monthly_salary.net_salary.to_float(),
            
            # Annual projections
            annual_gross_salary=monthly_salary.annual_gross_salary.to_float(),
            annual_tax_liability=monthly_salary.annual_tax_liability.to_float(),
            
            # Tax details
            tax_regime=monthly_salary.tax_regime,
            tax_exemptions=monthly_salary.tax_exemptions.to_float(),
            standard_deduction=monthly_salary.standard_deduction.to_float(),
            
            # Working days
            total_days_in_month=monthly_salary.total_days_in_month,
            working_days_in_period=monthly_salary.working_days_in_period,
            lwp_days=monthly_salary.lwp_days,
            effective_working_days=monthly_salary.effective_working_days,
            
            # Processing details
            status=monthly_salary.status.value,
            computation_date=monthly_salary.computation_date,
            notes=monthly_salary.notes,
            remarks=monthly_salary.remarks,
            
            # Payment tracking
            salary_payment_date=monthly_salary.salary_payment_date,
            tds_payment_date=monthly_salary.tds_payment_date,
            salary_payment_reference=monthly_salary.salary_payment_reference,
            tds_payment_reference=monthly_salary.tds_payment_reference,
            salary_paid_by=monthly_salary.salary_paid_by,
            tds_paid_by=monthly_salary.tds_paid_by,
            
            # Payment status helpers
            is_salary_paid=monthly_salary.is_salary_paid(),
            is_tds_paid=monthly_salary.is_tds_paid(),
            is_fully_paid=monthly_salary.is_fully_paid(),
            
            # Audit fields
            created_at=monthly_salary.created_at,
            updated_at=monthly_salary.updated_at,
            created_by=monthly_salary.created_by,
            updated_by=monthly_salary.updated_by
        )
    
    def _get_tax_year(self, month: int, year: int) -> str:
        """
        Determine tax year from month and year.
        Indian tax year runs from April to March.
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            str: Tax year in format 'YYYY-YY'
        """
        if month >= 4:  # April onwards
            return f"{year}-{str(year + 1)[2:]}"
        else:  # January to March
            return f"{year - 1}-{str(year)[2:]}" 