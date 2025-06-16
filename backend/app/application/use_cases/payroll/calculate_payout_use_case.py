"""
Calculate Payout Use Case
Core business logic for payout calculation
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal

from app.application.dto.payroll_dto import (
    PayoutCalculationRequestDTO,
    PayoutResponseDTO,
    SalaryComponentsResponseDTO,
    DeductionComponentsResponseDTO,
    AttendanceInfoResponseDTO,
    TaxInfoResponseDTO
)
from app.application.interfaces.repositories.payout_repository import (
    PayoutQueryRepository,
    PayoutCommandRepository
)
from app.domain.events.payroll_events import PayoutCalculated, PayoutStatusChanged
from app.domain.value_objects.payroll_value_objects import (
    Money, SalaryComponents, DeductionComponents, 
    AttendanceInfo, TaxInfo, PayPeriod, PayoutSummary
)
from app.domain.entities.taxation.payout import PayoutCreate, PayoutStatus
from app.infrastructure.services.employee_leave_legacy_service import get_employee_attendance

logger = logging.getLogger(__name__)


class CalculatePayoutUseCase:
    """
    Use case for calculating employee payout
    Handles salary calculation, deductions, taxes, and attendance adjustments
    """
    
    def __init__(
        self,
        payout_query_repo: PayoutQueryRepository,
        payout_command_repo: PayoutCommandRepository,
    ):
        """
        Initialize the use case with required dependencies
        
        Args:
            payout_query_repo: Payout query repository
            payout_command_repo: Payout command repository
        """
        self.payout_query_repo = payout_query_repo
        self.payout_command_repo = payout_command_repo
    
    async def execute(
        self, 
        request: PayoutCalculationRequestDTO,
        hostname: str,
        created_by: str
    ) -> PayoutResponseDTO:
        """
        Execute payout calculation
        
        Args:
            request: Payout calculation request
            hostname: Organisation hostname
            created_by: User initiating the calculation
            
        Returns:
            Calculated payout response
            
        Raises:
            ValidationError: If request data is invalid
            BusinessRuleViolationError: If business rules are violated
            TaxCalculationError: If tax calculation fails
        """
        try:
            logger.info(f"Starting payout calculation for employee {request.employee_id}, "
                       f"month {request.month}/{request.year}")
            
            # Step 1: Check for existing payout (if not forcing recalculation)
            if not request.force_recalculate:
                existing_payout = await self._check_existing_payout(
                    request.employee_id, request.month, request.year, hostname
                )
                if existing_payout:
                    logger.info(f"Returning existing payout for {request.employee_id}")
                    return self._convert_to_response_dto(existing_payout)
            
            # Step 2: Get employee salary data (with overrides if provided)
            salary_components = await self._get_salary_components(
                request.employee_id, hostname, request.override_salary
            )
            
            # Step 3: Get attendance information and calculate working ratios
            attendance_info = await self._get_attendance_info(
                request.employee_id, request.month, request.year, hostname
            )
            
            # Step 4: Calculate earnings based on attendance
            adjusted_salary = self._calculate_attendance_adjusted_salary(
                salary_components, attendance_info
            )
            
            # Step 5: Calculate tax information
            tax_info = await self._calculate_tax_info(
                request.employee_id, hostname, adjusted_salary
            )
            
            # Step 6: Calculate statutory deductions (EPF, ESI, etc.)
            deduction_components = self._calculate_deductions(
                adjusted_salary, tax_info, attendance_info
            )
            
            # Step 7: Calculate employer contributions
            employer_contributions = self._calculate_employer_contributions(
                adjusted_salary, attendance_info
            )
            
            # Step 8: Create payout summary
            payout_summary = self._create_payout_summary(
                adjusted_salary, deduction_components, employer_contributions
            )
            
            # Step 9: Create pay period
            pay_period = self._create_pay_period(request.month, request.year)
            
            # Step 10: Create and save payout record
            payout_record = await self._create_payout_record(
                request.employee_id,
                pay_period,
                adjusted_salary,
                deduction_components,
                attendance_info,
                tax_info,
                payout_summary,
                hostname,
                created_by
            )
            
            # Step 11: Emit domain event
            await self._emit_payout_calculated_event(
                payout_record, adjusted_salary, payout_summary
            )
            
            logger.info(f"Payout calculation completed for employee {request.employee_id}")
            return self._convert_to_response_dto(payout_record)
            
        except Exception as e:
            logger.error(f"Payout calculation failed for {request.employee_id}: {str(e)}")
            raise
    
    async def _check_existing_payout(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        hostname: str
    ) -> Optional[Any]:
        """Check if payout already exists for the period"""
        payouts = await self.payout_query_repo.get_employee_payouts(
            employee_id, hostname, year, month
        )
        return payouts[0] if payouts else None
    
    async def _get_salary_components(
        self, 
        employee_id: str, 
        hostname: str, 
        override_salary: Optional[Dict[str, float]]
    ) -> SalaryComponents:
        """Get employee salary components with optional overrides"""
        # Get taxation data which contains salary information
        taxation_data = await self.taxation_service.get_taxation_data_legacy(
            employee_id, hostname
        )
        
        salary_data = taxation_data.get("salary", {})
        
        # Apply overrides if provided
        if override_salary:
            salary_data.update(override_salary)
        
        # Convert to value objects with proper validation
        return SalaryComponents(
            basic=Money(Decimal(str(salary_data.get("basic_salary", 0)))),
            dearness_allowance=Money(Decimal(str(salary_data.get("dearness_allowance", 0)))),
            hra=Money(Decimal(str(salary_data.get("hra", 0)))),
            special_allowance=Money(Decimal(str(salary_data.get("special_allowance", 0)))),
            bonus=Money(Decimal(str(salary_data.get("bonus", 0)))),
            commission=Money(Decimal(str(salary_data.get("commission", 0)))),
            transport_allowance=Money(Decimal(str(salary_data.get("transport_allowance", 0)))),
            medical_allowance=Money(Decimal(str(salary_data.get("medical_allowance", 0)))),
            other_allowances=Money(Decimal(str(salary_data.get("other_allowances", 0))))
        )
    
    async def _get_attendance_info(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        hostname: str
    ) -> AttendanceInfo:
        """Get attendance information for the employee"""
        # Use legacy attendance service for now
        try:
            attendance_data = get_employee_attendance(employee_id, month, year, hostname)
            
            return AttendanceInfo(
                total_days_in_month=attendance_data.get("total_days", 30),
                working_days_in_period=attendance_data.get("working_days", 30),
                lwp_days=attendance_data.get("lwp_days", 0),
                overtime_hours=attendance_data.get("overtime_hours", 0.0)
            )
            
        except Exception as e:
            logger.warning(f"Failed to get attendance data: {e}. Using defaults.")
            # Return default attendance if service fails
            import calendar
            total_days = calendar.monthrange(year, month)[1]
            return AttendanceInfo(
                total_days_in_month=total_days,
                working_days_in_period=total_days,
                lwp_days=0,
                overtime_hours=0.0
            )
    
    def _calculate_attendance_adjusted_salary(
        self, 
        salary_components: SalaryComponents, 
        attendance_info: AttendanceInfo
    ) -> SalaryComponents:
        """Calculate salary adjusted for attendance and LWP"""
        working_ratio = attendance_info.effective_working_ratio()
        
        if working_ratio >= 1.0:
            return salary_components  # No adjustment needed
        
        # Adjust all salary components based on effective working ratio
        return SalaryComponents(
            basic=salary_components.basic.multiply(working_ratio),
            dearness_allowance=salary_components.dearness_allowance.multiply(working_ratio),
            hra=salary_components.hra.multiply(working_ratio),
            special_allowance=salary_components.special_allowance.multiply(working_ratio),
            bonus=salary_components.bonus.multiply(working_ratio),
            commission=salary_components.commission.multiply(working_ratio),
            transport_allowance=salary_components.transport_allowance.multiply(working_ratio),
            medical_allowance=salary_components.medical_allowance.multiply(working_ratio),
            other_allowances=salary_components.other_allowances.multiply(working_ratio)
        )
    
    async def _calculate_tax_info(
        self, 
        employee_id: str, 
        hostname: str, 
        salary_components: SalaryComponents
    ) -> TaxInfo:
        """Calculate tax information using taxation service"""
        try:
            # Use taxation service to calculate tax
            current_year = datetime.now().year
            tax_year = f"{current_year}-{current_year + 1}"
            
            tax_result = await self.taxation_service.get_taxation_data_legacy(
                employee_id, hostname
            )
            
            tax_data = tax_result.get("tax_calculation", {})
            
            return TaxInfo(
                regime=tax_data.get("regime", "new"),
                annual_tax_liability=Money(Decimal(str(tax_data.get("annual_tax", 0)))),
                monthly_tds=Money(Decimal(str(tax_data.get("monthly_tds", 0)))),
                exemptions_claimed=Money(Decimal(str(tax_data.get("exemptions", 0)))),
                standard_deduction=Money(Decimal(str(tax_data.get("standard_deduction", 0)))),
                section_80c_claimed=Money(Decimal(str(tax_data.get("section_80c", 0))))
            )
            
        except Exception as e:
            logger.warning(f"Tax calculation failed: {e}. Using minimal tax.")
            # Return minimal tax info if calculation fails
            return TaxInfo(
                regime="new",
                annual_tax_liability=Money(Decimal("0")),
                monthly_tds=Money(Decimal("0"))
            )
    
    def _calculate_deductions(
        self, 
        salary_components: SalaryComponents, 
        tax_info: TaxInfo, 
        attendance_info: AttendanceInfo
    ) -> DeductionComponents:
        """Calculate all deductions"""
        # EPF calculation (12% of basic + DA, capped at 1800)
        epf_base = salary_components.basic_plus_da()
        epf_employee = Money(min(Decimal("1800"), epf_base.amount * Decimal("0.12")))
        
        # ESI calculation (0.75% of gross, if gross <= 21000)
        gross_salary = salary_components.total_earnings()
        esi_employee = Money(Decimal("0"))
        if gross_salary.amount <= Decimal("21000"):
            esi_employee = gross_salary.multiply(0.0075)
        
        # Professional Tax (state-dependent, using Karnataka rates as default)
        professional_tax = Money(Decimal("200"))  # Simplified calculation
        
        # TDS from tax calculation
        tds = tax_info.monthly_tds
        
        return DeductionComponents(
            epf_employee=epf_employee,
            esi_employee=esi_employee,
            professional_tax=professional_tax,
            tds=tds
        )
    
    def _calculate_employer_contributions(
        self, 
        salary_components: SalaryComponents, 
        attendance_info: AttendanceInfo
    ) -> Money:
        """Calculate total employer contributions"""
        # EPF employer contribution (12% of basic + DA, capped at 1800)
        epf_base = salary_components.basic_plus_da()
        epf_employer = Money(min(Decimal("1800"), epf_base.amount * Decimal("0.12")))
        
        # ESI employer contribution (3.25% of gross, if gross <= 21000)
        gross_salary = salary_components.total_earnings()
        esi_employer = Money(Decimal("0"))
        if gross_salary.amount <= Decimal("21000"):
            esi_employer = gross_salary.multiply(0.0325)
        
        return epf_employer.add(esi_employer)
    
    def _create_payout_summary(
        self, 
        salary_components: SalaryComponents, 
        deduction_components: DeductionComponents, 
        employer_contributions: Money
    ) -> PayoutSummary:
        """Create payout summary with all calculations"""
        gross_earnings = salary_components.total_earnings()
        total_deductions = deduction_components.total_deductions()
        net_pay = gross_earnings.subtract(total_deductions)
        
        return PayoutSummary(
            gross_earnings=gross_earnings,
            total_deductions=total_deductions,
            net_pay=net_pay,
            employer_contributions=employer_contributions
        )
    
    def _create_pay_period(self, month: int, year: int) -> PayPeriod:
        """Create pay period for the month"""
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        
        return PayPeriod(
            start_date=date(year, month, 1),
            end_date=date(year, month, last_day),
            month=month,
            year=year
        )
    
    async def _create_payout_record(
        self,
        employee_id: str,
        pay_period: PayPeriod,
        salary_components: SalaryComponents,
        deduction_components: DeductionComponents,
        attendance_info: AttendanceInfo,
        tax_info: TaxInfo,
        payout_summary: PayoutSummary,
        hostname: str,
        created_by: str
    ) -> Any:
        """Create and save payout record"""
        payout_data = PayoutCreate(
            employee_id=employee_id,
            pay_period_start=pay_period.start_date,
            pay_period_end=pay_period.end_date,
            payout_date=pay_period.end_date,
            gross_salary=payout_summary.gross_earnings.to_float(),
            net_salary=payout_summary.net_pay.to_float(),
            total_deductions=payout_summary.total_deductions.to_float(),
            status=PayoutStatus.CALCULATED,
            salary_breakdown=salary_components.to_dict(),
            deduction_breakdown=deduction_components.to_dict(),
            attendance_data={
                "total_days": attendance_info.total_days_in_month,
                "working_days": attendance_info.working_days_in_period,
                "lwp_days": attendance_info.lwp_days,
                "overtime_hours": attendance_info.overtime_hours
            },
            tax_data=tax_info.to_dict(),
            created_by=created_by
        )
        
        return await self.payout_command_repo.create_payout(payout_data, hostname)
    
    async def _emit_payout_calculated_event(
        self, 
        payout_record: Any, 
        salary_components: SalaryComponents, 
        payout_summary: PayoutSummary
    ) -> None:
        """Emit domain event for payout calculation"""
        event = PayoutCalculated(
            payout_id=payout_record.id,
            employee_id=payout_record.employee_id,
            pay_period_start=payout_record.pay_period_start,
            pay_period_end=payout_record.pay_period_end,
            gross_salary=payout_summary.gross_earnings.to_float(),
            net_salary=payout_summary.net_pay.to_float(),
            total_deductions=payout_summary.total_deductions.to_float(),
            calculation_method="automated",
            occurred_at=datetime.now()
        )
        
        # In a real implementation, this would be published to an event bus
        logger.info(f"Domain event emitted: PayoutCalculated for {payout_record.employee_id}")
    
    def _convert_to_response_dto(self, payout_record: Any) -> PayoutResponseDTO:
        """Convert payout record to response DTO"""
        return PayoutResponseDTO(
            id=payout_record.id,
            employee_id=payout_record.employee_id,
            pay_period_start=payout_record.pay_period_start,
            pay_period_end=payout_record.pay_period_end,
            payout_date=payout_record.payout_date,
            salary_components=SalaryComponentsResponseDTO(**payout_record.salary_breakdown),
            deduction_components=DeductionComponentsResponseDTO(**payout_record.deduction_breakdown),
            attendance_info=AttendanceInfoResponseDTO(**payout_record.attendance_data),
            tax_info=TaxInfoResponseDTO(**payout_record.tax_data),
            gross_salary=payout_record.gross_salary,
            total_deductions=payout_record.total_deductions,
            net_salary=payout_record.net_salary,
            status=payout_record.status,
            notes=payout_record.notes,
            created_at=payout_record.created_at,
            updated_at=payout_record.updated_at
        ) 