"""
Unified Taxation Commands
Comprehensive application layer commands for all taxation operations including
basic taxation records, enhanced calculations, mid-year scenarios, and comparisons
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from decimal import Decimal
import logging

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.value_objects.employment_period import EmploymentPeriod
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.periodic_salary_income import PeriodicSalaryIncome, PeriodicSalaryData
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.taxation_record import TaxationRecord
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.monthly_payroll import AnnualPayrollWithLWP
from app.domain.services.taxation.tax_calculation_service import TaxCalculationService, TaxCalculationResult
from app.application.interfaces.repositories.taxation_repository import TaxationRepository
from app.domain.exceptions.taxation_exceptions import TaxationRecordNotFoundError, TaxationValidationError
from app.application.dto.taxation_dto import (
    EnhancedTaxCalculationRequestDTO, PeriodicTaxCalculationResponseDTO,
    ScenarioComparisonRequestDTO, ScenarioComparisonResponseDTO,
    MidYearJoinerDTO, MidYearIncrementDTO, SurchargeBreakdownDTO
)


# =============================================================================
# Basic Taxation Record Commands
# =============================================================================

@dataclass
class CreateTaxationRecordCommand:
    """Command to create new taxation record with comprehensive income support."""
    employee_id: str
    organization_id: str
    tax_year: str
    
    # Core income (required for backward compatibility)
    salary_income: SalaryIncome
    deductions: TaxDeductions
    
    regime: str
    age: int
    
    # Comprehensive income components (optional)
    perquisites: Optional['Perquisites'] = None
    house_property_income: Optional['HousePropertyIncome'] = None
    capital_gains_income: Optional['CapitalGainsIncome'] = None
    retirement_benefits: Optional['RetirementBenefits'] = None
    other_income: Optional['OtherIncome'] = None
    monthly_payroll: Optional['AnnualPayrollWithLWP'] = None


@dataclass
class CreateTaxationRecordResponse:
    """Response for creating taxation record."""
    taxation_id: str
    employee_id: str
    tax_year: str
    regime: str
    status: str
    message: str
    created_at: datetime


class CreateTaxationRecordCommandHandler:
    """Handler for creating taxation records."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self.taxation_repository = taxation_repository
    
    async def handle(self, command: CreateTaxationRecordCommand, organization_id: str) -> CreateTaxationRecordResponse:
        """
        Handle taxation record creation.
        
        Args:
            command: Creation command
            
        Returns:
            CreateTaxationRecordResponse: Creation result
        """
        
        logger = logging.getLogger(__name__)
        
        logger.info(f"Starting taxation record creation for user {command.employee_id}")
        
        # Parse and validate inputs
        employee_id = EmployeeId.from_string(command.employee_id)
        tax_year = TaxYear.from_string(command.tax_year)
        regime = TaxRegime.from_string(command.regime)
        
        logger.info(f"Parsed inputs - employee_id: {employee_id}, tax_year: {tax_year}, regime: {regime}")
        
        # Check if record already exists
        existing_record = await self.taxation_repository.get_by_user_and_year(
            employee_id, tax_year, command.organization_id
        )
        
        if existing_record:
            raise TaxationValidationError(
                f"Taxation record already exists for user {command.employee_id} in {command.tax_year}"
            )
        
        logger.info(f"No existing record found, proceeding with creation")
        logger.info(f"Salary income type: {type(command.salary_income)}")
        logger.info(f"Salary income basic_salary: {command.salary_income.basic_salary}")
        logger.info(f"Salary income hra_provided: {command.salary_income.hra_provided}")
        logger.info(f"Salary income hra_city_type: {command.salary_income.hra_city_type}")
        
        # Create default entities for optional components
        logger.info("Creating default Perquisites entity...")
        default_perquisites = command.perquisites or Perquisites()
        logger.info("✅ Perquisites entity created successfully")
        
        logger.info("Creating default HousePropertyIncome entity...")
        default_house_property = command.house_property_income or HousePropertyIncome(
            property_type=PropertyType.SELF_OCCUPIED,
            address="",
            annual_rent_received=Money.zero(),
            municipal_taxes_paid=Money.zero(),
            home_loan_interest=Money.zero(),
            pre_construction_interest=Money.zero()
        )
        logger.info("✅ HousePropertyIncome entity created successfully")
        
        logger.info("Creating default CapitalGainsIncome entity...")
        default_capital_gains = command.capital_gains_income or CapitalGainsIncome(
            asset_type="equity",
            purchase_date=date(2020, 1, 1),
            sale_date=date(2023, 1, 1),
            purchase_price=Money.zero(),
            sale_price=Money.zero()
        )
        logger.info("✅ CapitalGainsIncome entity created successfully")
        
        logger.info("Creating default RetirementBenefits entity...")
        default_retirement_benefits = command.retirement_benefits or RetirementBenefits()
        logger.info("✅ RetirementBenefits entity created successfully")
        
        logger.info("Creating default OtherIncome entity...")
        default_other_income = command.other_income or OtherIncome()
        logger.info("✅ OtherIncome entity created successfully")
        
        # Create new taxation record with comprehensive income support
        logger.info("Creating TaxationRecord entity...")
        try:
            taxation_record = TaxationRecord(
                employee_id=command.employee_id,
                tax_year=command.tax_year,
                salary_income=command.salary_income,
                perquisites=command.perquisites,
                house_property_income=command.house_property_income,
                capital_gains_income=command.capital_gains_income,
                retirement_benefits=command.retirement_benefits,
                other_income=command.other_income,
                deductions=command.deductions,
                regime=TaxRegime.from_string(command.regime),
                age=command.age
            )
            logger.info("✅ TaxationRecord entity created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create TaxationRecord entity: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            raise
        
        # Save to repository
        logger.info("Saving taxation record to repository...")
        saved_record = await self.taxation_repository.save(taxation_record, organization_id)
        logger.info("✅ Taxation record saved successfully")
        
        return CreateTaxationRecordResponse(
            taxation_id=f"{saved_record.employee_id}_{saved_record.tax_year.start_year}",  # Generate ID from employee and year
            employee_id=command.employee_id,
            tax_year=command.tax_year,
            regime=command.regime,
            status="created",
            message="Taxation record created successfully",
            created_at=datetime.utcnow()  # Use current time since entity may not have created_at
        )


@dataclass
class UpdateSalaryIncomeCommand:
    """Command to update salary income."""
    taxation_id: str
    organization_id: str
    salary_income: SalaryIncome


class UpdateSalaryIncomeCommandHandler:
    """Handler for updating salary income."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self.taxation_repository = taxation_repository
    
    async def handle(self, command: UpdateSalaryIncomeCommand) -> None:
        """Handle salary income update."""
        
        # Get existing record
        taxation_record = await self.taxation_repository.get_by_id(
            command.taxation_id, command.organization_id
        )
        
        if not taxation_record:
            raise TaxationRecordNotFoundError(f"Taxation record {command.taxation_id} not found")
        
        # Update salary income
        taxation_record.update_salary(command.salary_income)
        
        # Save updated record
        await self.taxation_repository.save(taxation_record, command.organization_id)


@dataclass
class UpdateDeductionsCommand:
    """Command to update tax deductions."""
    taxation_id: str
    organization_id: str
    deductions: TaxDeductions


class UpdateDeductionsCommandHandler:
    """Handler for updating tax deductions."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self.taxation_repository = taxation_repository
    
    async def handle(self, command: UpdateDeductionsCommand) -> None:
        """Handle deductions update."""
        
        # Get existing record
        taxation_record = await self.taxation_repository.get_by_id(
            command.taxation_id, command.organization_id
        )
        
        if not taxation_record:
            raise TaxationRecordNotFoundError(f"Taxation record {command.taxation_id} not found")
        
        # Update deductions
        taxation_record.update_deductions(command.deductions)
        
        # Save updated record
        await self.taxation_repository.save(taxation_record, command.organization_id)


@dataclass
class ChangeRegimeCommand:
    """Command to change tax regime."""
    taxation_id: str
    organization_id: str
    new_regime: str


class ChangeRegimeCommandHandler:
    """Handler for changing tax regime."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self.taxation_repository = taxation_repository
    
    async def handle(self, command: ChangeRegimeCommand) -> None:
        """Handle regime change."""
        
        # Get existing record
        taxation_record = await self.taxation_repository.get_by_id(
            command.taxation_id, command.organization_id
        )
        
        if not taxation_record:
            raise TaxationRecordNotFoundError(f"Taxation record {command.taxation_id} not found")
        
        # Parse new regime
        new_regime = TaxRegime.from_string(command.new_regime)
        
        # Change regime
        taxation_record.change_regime(new_regime)
        
        # Save updated record
        await self.taxation_repository.save(taxation_record, command.organization_id)


@dataclass
class CalculateTaxCommand:
    """Command to calculate tax."""
    taxation_id: str
    organization_id: str
    force_recalculate: bool = False


@dataclass
class CalculateTaxResponse:
    """Response for tax calculation."""
    taxation_id: str
    employee_id: str
    tax_year: str
    regime: str
    total_tax_liability: float
    effective_tax_rate: str
    monthly_tax_liability: float
    calculation_breakdown: dict
    calculated_at: datetime


class CalculateTaxCommandHandler:
    """Handler for tax calculation."""
    
    def __init__(self, 
                 taxation_repository: TaxationRepository,
                 tax_calculation_service: TaxCalculationService):
        self.taxation_repository = taxation_repository
        self.tax_calculation_service = tax_calculation_service
    
    async def handle(self, command: CalculateTaxCommand) -> CalculateTaxResponse:
        """Handle tax calculation."""
        
        # Get taxation record
        taxation_record = await self.taxation_repository.get_by_id(
            command.taxation_id, command.organization_id
        )
        
        if not taxation_record:
            raise TaxationRecordNotFoundError(f"Taxation record {command.taxation_id} not found")
        
        # Calculate tax if needed
        if not taxation_record.is_calculation_valid() or command.force_recalculate:
            calculation_result = taxation_record.calculate_tax(self.tax_calculation_service)
            
            # Save updated record
            await self.taxation_repository.save(taxation_record, command.organization_id)
        else:
            calculation_result = taxation_record.calculation_result
        
        return CalculateTaxResponse(
            taxation_id=command.taxation_id,
            employee_id=str(taxation_record.employee_id),
            tax_year=str(taxation_record.tax_year),
            regime=taxation_record.regime.regime_type.value,
            total_tax_liability=calculation_result.total_tax_liability.to_float(),
            effective_tax_rate=f"{calculation_result.effective_tax_rate:.2f}%",
            monthly_tax_liability=calculation_result.monthly_tax_liability.to_float(),
            calculation_breakdown=calculation_result.calculation_breakdown,
            calculated_at=taxation_record.last_calculated_at
        )


@dataclass
class FinalizeRecordCommand:
    """Command to finalize tax record."""
    taxation_id: str
    organization_id: str


class FinalizeRecordCommandHandler:
    """Handler for finalizing tax record."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self.taxation_repository = taxation_repository
    
    async def handle(self, command: FinalizeRecordCommand) -> None:
        """Handle record finalization."""
        
        # Get taxation record
        taxation_record = await self.taxation_repository.get_by_id(
            command.taxation_id, command.organization_id
        )
        
        if not taxation_record:
            raise TaxationRecordNotFoundError(f"Taxation record {command.taxation_id} not found")
        
        # Finalize record
        taxation_record.finalize_record()
        
        # Save updated record
        await self.taxation_repository.save(taxation_record, command.organization_id)


@dataclass
class ReopenRecordCommand:
    """Command to reopen finalized tax record."""
    taxation_id: str
    organization_id: str


class ReopenRecordCommandHandler:
    """Handler for reopening tax record."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self.taxation_repository = taxation_repository
    
    async def handle(self, command: ReopenRecordCommand) -> None:
        """Handle record reopening."""
        
        # Get taxation record
        taxation_record = await self.taxation_repository.get_by_id(
            command.taxation_id, command.organization_id
        )
        
        if not taxation_record:
            raise TaxationRecordNotFoundError(f"Taxation record {command.taxation_id} not found")
        
        # Reopen record
        taxation_record.reopen_record()
        
        # Save updated record
        await self.taxation_repository.save(taxation_record, command.organization_id)


@dataclass
class DeleteTaxationRecordCommand:
    """Command to delete taxation record."""
    taxation_id: str
    organization_id: str


class DeleteTaxationRecordCommandHandler:
    """Handler for deleting taxation record."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self.taxation_repository = taxation_repository
    
    async def handle(self, command: DeleteTaxationRecordCommand) -> None:
        """Handle record deletion."""
        
        # Get taxation record
        taxation_record = await self.taxation_repository.get_by_id(
            command.taxation_id, command.organization_id
        )
        
        if not taxation_record:
            raise TaxationRecordNotFoundError(f"Taxation record {command.taxation_id} not found")
        
        # Check if record can be deleted
        if taxation_record.is_final:
            raise TaxationValidationError("Cannot delete finalized tax record")
        
        # Delete record
        await self.taxation_repository.delete(command.taxation_id, command.organization_id)


# =============================================================================
# Enhanced Tax Calculation Commands
# =============================================================================

class EnhancedTaxCalculationCommand:
    """Command handler for enhanced tax calculations with periodic salary and mid-year scenarios."""
    
    def __init__(self, tax_calculation_service: TaxCalculationService):
        self.tax_calculation_service = tax_calculation_service
    
    def handle(self, request: EnhancedTaxCalculationRequestDTO) -> PeriodicTaxCalculationResponseDTO:
        """
        Handle enhanced tax calculation request.
        
        Args:
            request: Enhanced tax calculation request
            
        Returns:
            PeriodicTaxCalculationResponseDTO: Enhanced tax calculation response
        """
        
        # Parse tax year and regime
        tax_year = TaxYear.from_string(request.tax_year)
        regime = TaxRegime.old_regime() if request.regime_type.lower() == "old" else TaxRegime.new_regime()
        
        # Build periodic salary income
        periodic_salary = self._build_periodic_salary(request.salary_income, tax_year)
        
        # Build deductions
        deductions = self._build_deductions(request, regime)
        
        # Calculate enhanced tax
        result = self.tax_calculation_service.calculate_periodic_tax(
            periodic_salary=periodic_salary,
            deductions=deductions,
            regime=regime,
            tax_year=tax_year,
            age=request.age
        )
        
        # Convert to response DTO
        return self._convert_to_response_dto(result)
    
    def _build_periodic_salary(self, salary_dto, tax_year: TaxYear) -> PeriodicSalaryIncome:
        """
        Build periodic salary income from DTO.
        
        Args:
            salary_dto: Salary income DTO
            tax_year: Tax year
            
        Returns:
            PeriodicSalaryIncome: Periodic salary income entity
        """
        if not salary_dto or not salary_dto.periods:
            raise ValueError("Salary income periods are required")
        
        periods = []
        for period_dto in salary_dto.periods:
            # Build employment period
            employment_period = EmploymentPeriod(
                start_date=period_dto.period.start_date,
                end_date=period_dto.period.end_date,
                description=period_dto.period.description
            )
            
            # Build salary income
            current_tax_year = TaxYear.current()
            effective_from = datetime.combine(current_tax_year.get_start_date(), datetime.min.time())
            effective_till = datetime.combine(current_tax_year.get_end_date(), datetime.min.time())
            
            salary_income = SalaryIncome(
                effective_from=effective_from,
                effective_till=effective_till,
                basic_salary=Money.from_decimal(period_dto.basic_salary),
                dearness_allowance=Money.from_decimal(period_dto.dearness_allowance),
                hra_provided=Money.from_decimal(period_dto.hra_provided),
                hra_city_type=period_dto.hra_city_type,
                actual_rent_paid=Money.from_decimal(period_dto.actual_rent_paid),
                special_allowance=Money.from_decimal(period_dto.special_allowance),
                bonus=Money.from_decimal(period_dto.bonus),
                commission=Money.from_decimal(period_dto.commission)
            )
            
            periods.append(PeriodicSalaryData(
                period=employment_period,
                salary_income=salary_income
            ))
        
        return PeriodicSalaryIncome(periods=periods)
    
    def _build_deductions(self, request: EnhancedTaxCalculationRequestDTO, regime: TaxRegime) -> TaxDeductions:
        """
        Build tax deductions from request.
        
        Args:
            request: Tax calculation request
            regime: Tax regime
            
        Returns:
            TaxDeductions: Tax deductions entity
        """
        return TaxDeductions(
            section_80c_investments=Money.from_decimal(request.section_80c_investments),
            section_80d_health_insurance=Money.from_decimal(request.section_80d_health_insurance),
            section_80d_parents_health_insurance=Money.from_decimal(request.section_80d_parents_health_insurance),
            section_80e_education_loan=Money.from_decimal(request.section_80e_education_loan),
            section_80g_donations=Money.from_decimal(request.section_80g_donations),
            section_80tta_savings_interest=Money.from_decimal(request.section_80tta_savings_interest),
            section_80ccd1b_nps=Money.from_decimal(request.section_80ccd1b_nps)
        )
    
    def _convert_to_response_dto(self, result) -> PeriodicTaxCalculationResponseDTO:
        """
        Convert calculation result to response DTO.
        
        Args:
            result: Periodic tax calculation result
            
        Returns:
            PeriodicTaxCalculationResponseDTO: Response DTO
        """
        return PeriodicTaxCalculationResponseDTO(
            # Basic tax results
            gross_income=result.basic_result.gross_income.to_float(),
            total_exemptions=result.basic_result.total_exemptions.to_float(),
            total_deductions=result.basic_result.total_deductions.to_float(),
            taxable_income=result.basic_result.taxable_income.to_float(),
            tax_before_rebate=result.basic_result.tax_before_rebate.to_float(),
            rebate_87a=result.basic_result.rebate_87a.to_float(),
            tax_after_rebate=result.basic_result.tax_after_rebate.to_float(),
            surcharge=result.basic_result.surcharge.to_float(),
            cess=result.basic_result.cess.to_float(),
            total_tax_liability=result.basic_result.total_tax_liability.to_float(),
            effective_tax_rate=float(result.basic_result.effective_tax_rate),
            
            # Enhanced details
            employment_periods=result.employment_periods,
            total_employment_days=result.total_employment_days,
            is_mid_year_scenario=result.is_mid_year_scenario,
            
            # Detailed breakdowns
            period_wise_income=result.period_wise_income,
            surcharge_breakdown=SurchargeBreakdownDTO(
                applicable=result.surcharge_breakdown.applicable,
                rate=float(result.surcharge_breakdown.rate),
                rate_description=result.surcharge_breakdown.rate_description,
                base_amount=result.surcharge_breakdown.base_amount.to_float(),
                surcharge_amount=result.surcharge_breakdown.surcharge_amount.to_float(),
                income_slab=result.surcharge_breakdown.income_slab,
                marginal_relief_applicable=result.surcharge_breakdown.marginal_relief_applicable,
                marginal_relief_amount=result.surcharge_breakdown.marginal_relief_amount.to_float(),
                effective_surcharge=result.surcharge_breakdown.effective_surcharge.to_float()
            ),
            
            # Analysis and projections
            full_year_projection=result.full_year_projection,
            mid_year_impact=result.mid_year_impact,
            optimization_suggestions=result.optimization_suggestions,
            
            # Metadata
            regime_used=result.basic_result.regime_used.regime_type.value,
            taxpayer_age=result.basic_result.taxpayer_age,
            calculation_breakdown=result.basic_result.calculation_breakdown
        )


# =============================================================================
# Mid-Year Scenario Commands
# =============================================================================

class MidYearJoinerCommand:
    """Command handler for mid-year joiner scenarios."""
    
    def __init__(self, tax_calculation_service: TaxCalculationService):
        self.tax_calculation_service = tax_calculation_service
    
    def handle(self, request: MidYearJoinerDTO, tax_year_str: str, regime_type: str, 
              age: int, deductions_data: Dict[str, float]) -> PeriodicTaxCalculationResponseDTO:
        """
        Handle mid-year joiner calculation.
        
        Args:
            request: Mid-year joiner request
            tax_year_str: Tax year string
            regime_type: Tax regime type
            age: Taxpayer age
            deductions_data: Deductions data
            
        Returns:
            PeriodicTaxCalculationResponseDTO: Tax calculation response
        """
        
        # Parse inputs
        tax_year = TaxYear.from_string(tax_year_str)
        regime = TaxRegime.old_regime() if regime_type.lower() == "old" else TaxRegime.new_regime()
        
        # Build salary income
        current_tax_year = TaxYear.current()
        effective_from = datetime.combine(current_tax_year.get_start_date(), datetime.min.time())
        effective_till = datetime.combine(current_tax_year.get_end_date(), datetime.min.time())
        
        salary_income = SalaryIncome(
            effective_from=effective_from,
            effective_till=effective_till,
            basic_salary=Money.from_decimal(request.salary_details.basic_salary),
            dearness_allowance=Money.from_decimal(request.salary_details.dearness_allowance),
            hra_provided=Money.from_decimal(request.salary_details.hra_provided),
            hra_city_type=request.salary_details.hra_city_type,
            actual_rent_paid=Money.from_decimal(request.salary_details.actual_rent_paid),
            special_allowance=Money.from_decimal(request.salary_details.special_allowance),
            bonus=Money.from_decimal(request.salary_details.bonus),
            commission=Money.from_decimal(request.salary_details.commission)
        )
        
        # Create periodic salary for mid-year joiner
        periodic_salary = PeriodicSalaryIncome.create_mid_year_joiner(salary_income, request.joining_date)
        
        # Build deductions
        deductions = TaxDeductions(
            section_80c_investments=Money.from_float(deductions_data.get('section_80c_investments', 0)),
            section_80d_health_insurance=Money.from_float(deductions_data.get('section_80d_health_insurance', 0)),
            section_80d_parents_health_insurance=Money.from_float(deductions_data.get('section_80d_parents_health_insurance', 0)),
            section_80e_education_loan=Money.from_float(deductions_data.get('section_80e_education_loan', 0)),
            section_80g_donations=Money.from_float(deductions_data.get('section_80g_donations', 0)),
            section_80tta_savings_interest=Money.from_float(deductions_data.get('section_80tta_savings_interest', 0)),
            section_80ccd1b_nps=Money.from_float(deductions_data.get('section_80ccd1b_nps', 0))
        )
        
        # Calculate tax
        result = self.tax_calculation_service.calculate_periodic_tax(
            periodic_salary=periodic_salary,
            deductions=deductions,
            regime=regime,
            tax_year=tax_year,
            age=age
        )
        
        # Convert to response
        command = EnhancedTaxCalculationCommand(self.tax_calculation_service)
        return command._convert_to_response_dto(result)


class MidYearIncrementCommand:
    """Command handler for mid-year increment scenarios."""
    
    def __init__(self, tax_calculation_service: TaxCalculationService):
        self.tax_calculation_service = tax_calculation_service
    
    def handle(self, request: MidYearIncrementDTO, tax_year_str: str, regime_type: str,
              age: int, deductions_data: Dict[str, float]) -> PeriodicTaxCalculationResponseDTO:
        """
        Handle mid-year increment calculation.
        
        Args:
            request: Mid-year increment request
            tax_year_str: Tax year string
            regime_type: Tax regime type
            age: Taxpayer age
            deductions_data: Deductions data
            
        Returns:
            PeriodicTaxCalculationResponseDTO: Tax calculation response
        """
        
        # Parse inputs
        tax_year = TaxYear.from_string(tax_year_str)
        regime = TaxRegime.old_regime() if regime_type.lower() == "old" else TaxRegime.new_regime()
        
        # Build pre-increment salary
        current_tax_year = TaxYear.current()
        effective_from = datetime.combine(current_tax_year.get_start_date(), datetime.min.time())
        effective_till = datetime.combine(current_tax_year.get_end_date(), datetime.min.time())
        
        pre_increment_salary = SalaryIncome(
            effective_from=effective_from,
            effective_till=effective_till,
            basic_salary=Money.from_decimal(request.pre_increment_salary.basic_salary),
            dearness_allowance=Money.from_decimal(request.pre_increment_salary.dearness_allowance),
            hra_provided=Money.from_decimal(request.pre_increment_salary.hra_provided),
            hra_city_type=request.pre_increment_salary.hra_city_type,
            actual_rent_paid=Money.from_decimal(request.pre_increment_salary.actual_rent_paid),
            bonus=Money.from_decimal(request.pre_increment_salary.bonus),
            commission=Money.from_decimal(request.pre_increment_salary.commission),
        )
        
        # Build post-increment salary
        post_increment_salary = SalaryIncome(
            effective_from=effective_from,
            effective_till=effective_till,
            basic_salary=Money.from_decimal(request.post_increment_salary.basic_salary),
            dearness_allowance=Money.from_decimal(request.post_increment_salary.dearness_allowance),
            hra_provided=Money.from_decimal(request.post_increment_salary.hra_provided),
            hra_city_type=request.post_increment_salary.hra_city_type,
            actual_rent_paid=Money.from_decimal(request.post_increment_salary.actual_rent_paid),
            special_allowance=Money.from_decimal(request.post_increment_salary.special_allowance),
            bonus=Money.from_decimal(request.post_increment_salary.bonus),
            commission=Money.from_decimal(request.post_increment_salary.commission),
        )
        
        # Create periodic salary with increment
        periodic_salary = PeriodicSalaryIncome.create_with_increment(
            initial_salary=pre_increment_salary,
            increment_salary=post_increment_salary,
            increment_date=request.increment_date,
            tax_year=tax_year
        )
        
        # Build deductions
        deductions = TaxDeductions(
            section_80c_investments=Money.from_float(deductions_data.get('section_80c_investments', 0)),
            section_80d_health_insurance=Money.from_float(deductions_data.get('section_80d_health_insurance', 0)),
            section_80d_parents_health_insurance=Money.from_float(deductions_data.get('section_80d_parents_health_insurance', 0)),
            section_80e_education_loan=Money.from_float(deductions_data.get('section_80e_education_loan', 0)),
            section_80g_donations=Money.from_float(deductions_data.get('section_80g_donations', 0)),
            section_80tta_savings_interest=Money.from_float(deductions_data.get('section_80tta_savings_interest', 0)),
            section_80ccd1b_nps=Money.from_float(deductions_data.get('section_80ccd1b_nps', 0))
        )
        
        # Calculate tax
        result = self.tax_calculation_service.calculate_periodic_tax(
            periodic_salary=periodic_salary,
            deductions=deductions,
            regime=regime,
            tax_year=tax_year,
            age=age
        )
        
        # Convert to response
        command = EnhancedTaxCalculationCommand(self.tax_calculation_service)
        return command._convert_to_response_dto(result)


# =============================================================================
# Scenario Comparison Commands
# =============================================================================

class ScenarioComparisonCommand:
    """Command handler for scenario comparisons."""
    
    def __init__(self, tax_calculation_service: TaxCalculationService):
        self.tax_calculation_service = tax_calculation_service
    
    def handle(self, request: ScenarioComparisonRequestDTO) -> ScenarioComparisonResponseDTO:
        """
        Handle scenario comparison request.
        
        Args:
            request: Scenario comparison request
            
        Returns:
            ScenarioComparisonResponseDTO: Comparison response
        """
        
        # Get base calculation
        base_command = EnhancedTaxCalculationCommand(self.tax_calculation_service)
        base_result = base_command.handle(request.base_request)
        
        # Initialize comparison results
        full_year_current_comparison = None
        full_year_highest_comparison = None
        regime_comparison = None
        
        # Perform comparisons as requested
        if request.compare_full_year_at_current:
            full_year_current_comparison = self._compare_full_year_at_current(request.base_request)
        
        if request.compare_full_year_at_highest:
            full_year_highest_comparison = self._compare_full_year_at_highest(request.base_request)
        
        if request.compare_different_regime:
            regime_comparison = self._compare_different_regime(request.base_request, base_command)
        
        # Generate recommendations
        recommendations = self._generate_comparison_recommendations(
            base_result, full_year_current_comparison, full_year_highest_comparison, regime_comparison
        )
        
        # Determine best scenario
        best_scenario = self._determine_best_scenario(
            base_result, full_year_current_comparison, full_year_highest_comparison, regime_comparison
        )
        
        return ScenarioComparisonResponseDTO(
            base_calculation=base_result,
            full_year_current_comparison=full_year_current_comparison,
            full_year_highest_comparison=full_year_highest_comparison,
            regime_comparison=regime_comparison,
            recommendations=recommendations,
            best_scenario=best_scenario
        )
    
    def _compare_full_year_at_current(self, base_request: EnhancedTaxCalculationRequestDTO) -> Dict[str, Any]:
        """Compare with full year at current salary."""
        # Implementation would involve creating a full-year scenario
        # with current salary and comparing results
        return {"comparison": "full_year_at_current", "details": "Implementation needed"}
    
    def _compare_full_year_at_highest(self, base_request: EnhancedTaxCalculationRequestDTO) -> Dict[str, Any]:
        """Compare with full year at highest salary."""
        # Implementation would involve creating a full-year scenario
        # with highest salary and comparing results
        return {"comparison": "full_year_at_highest", "details": "Implementation needed"}
    
    def _compare_different_regime(self, base_request: EnhancedTaxCalculationRequestDTO,
                                 base_command: EnhancedTaxCalculationCommand) -> Dict[str, Any]:
        """Compare with different tax regime."""
        # Create request with different regime
        different_regime_request = base_request.copy()
        different_regime_request.regime_type = "new" if base_request.regime_type == "old" else "old"
        
        # Calculate with different regime
        different_result = base_command.handle(different_regime_request)
        
        return {
            "different_regime_result": different_result,
            "tax_difference": different_result.total_tax_liability - base_request.salary_income,  # Simplified
            "regime_used": different_result.regime_used
        }
    
    def _generate_comparison_recommendations(self, base_result, current_comp, highest_comp, regime_comp) -> List[str]:
        """Generate recommendations based on comparisons."""
        recommendations = []
        
        if base_result.is_mid_year_scenario:
            recommendations.append("Consider the tax impact of mid-year changes when planning future increments")
        
        if regime_comp:
            recommendations.append("Compare both tax regimes to choose the optimal one for your situation")
        
        recommendations.extend(base_result.optimization_suggestions)
        
        return recommendations
    
    def _determine_best_scenario(self, base_result, current_comp, highest_comp, regime_comp) -> Dict[str, Any]:
        """Determine the best scenario from comparisons."""
        return {
            "best_scenario": "Current calculation",
            "reason": "Based on actual employment periods and chosen regime",
            "potential_savings": 0.0
        } 