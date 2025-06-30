"""
Unified Taxation Controller
Production-ready controller for all taxation operations and comprehensive income calculations
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal

# Import all DTOs from both controllers
from app.application.dto.taxation_dto import (
    # Basic DTOs
    UpdateSalaryIncomeRequest,
    UpdateDeductionsRequest,
    UpdateResponse,
    
    # Comprehensive DTOs
    PerquisitesDTO,
    HousePropertyIncomeDTO,
    CapitalGainsIncomeDTO,
    RetirementBenefitsDTO,
    OtherIncomeDTO,

    ErrorResponse,
    
    # Employee Selection DTOs
    EmployeeSelectionQuery,
    EmployeeSelectionResponse,
    
    # Individual Component Update DTOs
    UpdateSalaryComponentRequest,
    UpdatePerquisitesComponentRequest,
    UpdateDeductionsComponentRequest,
    UpdateHousePropertyComponentRequest,
    UpdateCapitalGainsComponentRequest,
    UpdateRetirementBenefitsComponentRequest,
    UpdateOtherIncomeComponentRequest,
    UpdateMonthlyPayrollComponentRequest,
    UpdateRegimeComponentRequest,
    ComponentUpdateResponse,
    ComponentResponse,
    TaxationRecordStatusResponse,
    FlatRetirementBenefitsDTO,
)

# Import domain entities and value objects
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.deductions import (
    DeductionSection80C, DeductionSection80D, DeductionSection80E, 
    DeductionSection80G, DeductionSection80TTA_TTB, OtherDeductions
)
from app.domain.entities.taxation.perquisites import (
    Perquisites, AccommodationPerquisite, CarPerquisite, AccommodationType,
    CityPopulation, CarUseType, AssetType, MedicalReimbursement, LTAPerquisite,
    InterestFreeConcessionalLoan, ESOPPerquisite, UtilitiesPerquisite,
    FreeEducationPerquisite, MovableAssetUsage, MovableAssetTransfer,
    LunchRefreshmentPerquisite, GiftVoucherPerquisite, MonetaryBenefitsPerquisite,
    ClubExpensesPerquisite, DomesticHelpPerquisite
)
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.domain.entities.taxation.retirement_benefits import (
    RetirementBenefits, LeaveEncashment, Gratuity, VRS, Pension, RetrenchmentCompensation
)
from app.domain.entities.taxation.other_income import OtherIncome, InterestIncome
from app.domain.entities.taxation.taxation_record import SalaryPackageRecord

# Import services
from app.domain.services.taxation.tax_calculation_service import (
    TaxCalculationService, TaxCalculationInput, TaxCalculationResult
)
from app.application.use_cases.taxation.get_employees_for_selection_use_case import GetEmployeesForSelectionUseCase

logger = logging.getLogger(__name__)


class UnifiedTaxationController:
    """
    Unified production-ready controller for all taxation operations.
    
    Combines basic taxation record management with comprehensive calculations
    including all income types:
    - Basic taxation record CRUD operations
    - Salary income (simple and periodic)
    - Perquisites (all 15+ types)
    - House property income
    - Capital gains
    - Retirement benefits  
    - Other income sources
    - Monthly payroll with LWP
    - Enhanced tax calculations and analytics
    - Mid-year scenarios (joiners, increments)
    - Scenario comparisons and planning
    """
    
    def __init__(self,
                 user_repository,
                 salary_package_repository):
                 
        self.user_repository = user_repository
        self.salary_package_repository = salary_package_repository
        self.get_employees_for_selection_use_case = GetEmployeesForSelectionUseCase(user_repository, salary_package_repository)
    
    # =============================================================================
    # EMPLOYEE SELECTION OPERATIONS
    # =============================================================================
    
    async def get_employees_for_selection(
        self,
        query: EmployeeSelectionQuery,
        current_user
    ) -> EmployeeSelectionResponse:
        """
        Get employees for taxation selection.
        
        This method leverages the user service to fetch employee data
        and enriches it with tax record information for admin selection interface.
        
        Args:
            query: Query parameters for filtering and pagination
            current_user: Current authenticated user with organization context
            
        Returns:
            Employee selection response with enriched data
        """
        
        logger.info(f"Getting employees for selection with query: {query}")
        
        try:
            # Execute the use case to get employees
            response = await self.get_employees_for_selection_use_case.execute(
                query, current_user
            )
            
            logger.info(f"Retrieved {len(response.employees)} employees for selection")
            return response
            
        except Exception as e:
            logger.error(f"Error getting employees for selection: {str(e)}")
            raise
    
    # =============================================================================
    # COMPONENT-SPECIFIC CALCULATION METHODS
    # =============================================================================
    
    async def calculate_perquisites_only(self,
                                       perquisites: PerquisitesDTO,
                                       regime_type: str,
                                       organization_id: str) -> Dict[str, Any]:
        """Calculate only perquisites tax impact."""
        try:
            # Convert DTO to entity
            perquisites_entity = self._convert_perquisites_dto_to_entity(perquisites)
            regime = TaxRegime(TaxRegimeType.OLD if regime_type.lower() == "old" else TaxRegimeType.NEW)
            
            # Calculate perquisites
            total_perquisites = perquisites_entity.calculate_total_perquisites(regime)
            breakdown = perquisites_entity.get_perquisites_breakdown(regime)
            
            return {
                "total_perquisites_value": total_perquisites.to_float(),
                "perquisites_breakdown": breakdown,
                "regime_used": regime_type,
                "perquisites_applicable": regime.regime_type == TaxRegimeType.OLD
            }
            
        except Exception as e:
            logger.error(f"Error calculating perquisites for org {organization_id}: {str(e)}")
            raise
    
    async def calculate_house_property_income_only(self,
                                          house_property_income: HousePropertyIncomeDTO,
                                          regime_type: str,
                                          organization_id: str) -> Dict[str, Any]:
        """Calculate only house property income."""
        try:
            # Convert DTO to entity
            house_property_entity = self._convert_house_property_income_dto_to_entity(house_property_income)
            regime = TaxRegime(TaxRegimeType.OLD if regime_type.lower() == "old" else TaxRegimeType.NEW)
            
            # Calculate house property income
            net_income = house_property_entity.calculate_net_income_from_house_property_income(regime)
            breakdown = house_property_entity.get_house_property_income_breakdown(regime)
            
            return {
                "net_house_property_income": net_income.to_float(),
                "house_property_income_breakdown": breakdown,
                "regime_used": regime_type
            }
            
        except Exception as e:
            logger.error(f"Error calculating house property for org {organization_id}: {str(e)}")
            raise
    
    async def calculate_capital_gains_only(self,
                                         capital_gains: CapitalGainsIncomeDTO,
                                         regime_type: str,
                                         organization_id: str) -> Dict[str, Any]:
        """Calculate only capital gains tax."""
        try:
            # Convert DTO to entity
            capital_gains_entity = self._convert_capital_gains_dto_to_entity(capital_gains)
            regime = TaxRegime(TaxRegimeType.OLD if regime_type.lower() == "old" else TaxRegimeType.NEW)
            
            # Calculate capital gains
            total_tax = capital_gains_entity.calculate_total_capital_gains_tax()
            breakdown = capital_gains_entity.get_capital_gains_breakdown(regime)
            
            return {
                "total_capital_gains_tax": total_tax.to_float(),
                "capital_gains_breakdown": breakdown,
                "regime_used": regime_type
            }
            
        except Exception as e:
            logger.error(f"Error calculating capital gains for org {organization_id}: {str(e)}")
            raise
    
    async def calculate_retirement_benefits_only(self,
                                               retirement_benefits: RetirementBenefitsDTO,
                                               regime_type: str,
                                               organization_id: str) -> Dict[str, Any]:
        """Calculate only retirement benefits tax."""
        try:
            # Convert DTO to entity
            retirement_entity = self._convert_retirement_benefits_dto_to_entity(retirement_benefits)
            regime = TaxRegime(TaxRegimeType.OLD if regime_type.lower() == "old" else TaxRegimeType.NEW)
            
            # Calculate retirement benefits
            total_income = retirement_entity.calculate_total_retirement_income(regime)
            breakdown = retirement_entity.get_retirement_benefits_breakdown(regime)
            
            return {
                "total_retirement_income": total_income.to_float(),
                "retirement_benefits_breakdown": breakdown,
                "regime_used": regime_type
            }
            
        except Exception as e:
            logger.error(f"Error calculating retirement benefits for org {organization_id}: {str(e)}")
            raise
    
    # =============================================================================
    # DTO TO DOMAIN ENTITY CONVERSION METHODS
    # =============================================================================
    
    def _create_default_salary_income(self):
        """Create default salary income entity."""
        from app.domain.entities.taxation.salary_income import SalaryIncome, SpecificAllowances
        from app.domain.value_objects.money import Money
        from datetime import datetime
        from app.domain.value_objects.tax_year import TaxYear
        
        current_tax_year = TaxYear.current()
        effective_from = datetime.combine(current_tax_year.get_start_date(), datetime.min.time())
        effective_till = datetime.combine(current_tax_year.get_end_date(), datetime.min.time())
        
        return SalaryIncome(
            effective_from=effective_from,
            effective_till=effective_till,
            basic_salary=Money.zero(),
            dearness_allowance=Money.zero(),
            hra_provided=Money.zero(),
            special_allowance=Money.zero(),
            bonus=Money.zero(),
            commission=Money.zero(),
            arrears=Money.zero(),
            specific_allowances=SpecificAllowances()
        )
    
    def _create_default_perquisites(self):
        """Create default perquisites entity."""
        from app.domain.entities.taxation.perquisites import Perquisites
        
        return Perquisites()
    
    def _create_default_house_property_income(self):
        """Create default house property income entity."""
        from app.domain.entities.taxation.house_property_income import HousePropertyIncome, PropertyType
        from app.domain.value_objects.money import Money
        
        return HousePropertyIncome(
            property_type=PropertyType.SELF_OCCUPIED,
            address="",
            annual_rent_received=Money.zero(),
            municipal_taxes_paid=Money.zero(),
            home_loan_interest=Money.zero(),
            pre_construction_interest=Money.zero()
        )
    
    def _create_default_capital_gains(self):
        """Create default capital gains entity."""
        from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
        from app.domain.value_objects.money import Money
        
        return CapitalGainsIncome(
            stcg_111a_equity_stt=Money.zero(),
            stcg_other_assets=Money.zero(),
            ltcg_112a_equity_stt=Money.zero(),
            ltcg_other_assets=Money.zero(),
            ltcg_debt_mf=Money.zero()
        )
    
    def _create_default_retirement_benefits(self):
        """Create default retirement benefits entity."""
        from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
        
        return RetirementBenefits()
    
    def _create_default_other_income(self):
        """Create default other income entity."""
        from app.domain.entities.taxation.other_income import OtherIncome, InterestIncome
        from app.domain.value_objects.money import Money
        
        # Create default interest income
        default_interest_income = InterestIncome(
            savings_account_interest=Money.zero(),
            fixed_deposit_interest=Money.zero(),
            recurring_deposit_interest=Money.zero(),
            post_office_interest=Money.zero()
        )
        
        return OtherIncome(
            interest_income=default_interest_income,
            dividend_income=Money.zero(),
            gifts_received=Money.zero(),
            business_professional_income=Money.zero(),
            other_miscellaneous_income=Money.zero()
        )
    
    def _create_default_deductions(self):
        """Create default tax deductions entity."""
        from app.domain.entities.taxation.deductions import TaxDeductions
        
        return TaxDeductions()
    
    def _convert_salary_dto_to_entity(self, salary_dto) -> SalaryIncome:
        """Convert salary DTO to domain entity."""
        from datetime import datetime
        
        # Handle effective dates - convert from date to datetime if provided
        # If not provided, use default values for the current tax year
        if hasattr(salary_dto, 'effective_from') and salary_dto.effective_from:
            effective_from = datetime.combine(salary_dto.effective_from, datetime.min.time())
        else:
            # Default to start of current tax year
            from app.domain.value_objects.tax_year import TaxYear
            current_tax_year = TaxYear.current()
            effective_from = datetime.combine(current_tax_year.get_start_date(), datetime.min.time())
        
        if hasattr(salary_dto, 'effective_till') and salary_dto.effective_till:
            effective_till = datetime.combine(salary_dto.effective_till, datetime.min.time())
        else:
            # Default to end of current tax year
            from app.domain.value_objects.tax_year import TaxYear
            current_tax_year = TaxYear.current()
            effective_till = datetime.combine(current_tax_year.get_end_date(), datetime.min.time())
        
        # Create SpecificAllowances from DTO fields
        from app.domain.entities.taxation.salary_income import SpecificAllowances
        specific_allowances = SpecificAllowances(
            hills_allowance=Money.from_decimal(getattr(salary_dto, 'hills_high_altd_allowance', 0)),
            hills_exemption_limit=Money.from_decimal(getattr(salary_dto, 'hills_high_altd_exemption_limit', 0)),
            border_allowance=Money.from_decimal(getattr(salary_dto, 'border_remote_allowance', 0)),
            border_exemption_limit=Money.from_decimal(getattr(salary_dto, 'border_remote_exemption_limit', 0)),
            transport_employee_allowance=Money.from_decimal(getattr(salary_dto, 'transport_employee_allowance', 0)),
            children_education_allowance=Money.from_decimal(getattr(salary_dto, 'children_education_allowance', 0)),
            children_count=getattr(salary_dto, 'children_education_count', 0),
            children_education_months=getattr(salary_dto, 'children_education_months', 12),
            hostel_allowance=Money.from_decimal(getattr(salary_dto, 'hostel_allowance', 0)),
            hostel_count=getattr(salary_dto, 'hostel_count', 0),
            hostel_months=getattr(salary_dto, 'hostel_months', 12),
            disabled_transport_allowance=Money.from_decimal(getattr(salary_dto, 'disabled_transport_allowance', 0)),
            transport_months=getattr(salary_dto, 'transport_months', 12),
            underground_mines_allowance=Money.from_decimal(getattr(salary_dto, 'underground_mines_allowance', 0)),
            mine_work_months=getattr(salary_dto, 'underground_mines_months', 0),
            government_entertainment_allowance=Money.from_decimal(getattr(salary_dto, 'govt_employee_entertainment_allowance', 0)),
            city_compensatory_allowance=Money.from_decimal(getattr(salary_dto, 'city_compensatory_allowance', 0)),
            rural_allowance=Money.from_decimal(getattr(salary_dto, 'rural_allowance', 0)),
            proctorship_allowance=Money.from_decimal(getattr(salary_dto, 'proctorship_allowance', 0)),
            wardenship_allowance=Money.from_decimal(getattr(salary_dto, 'wardenship_allowance', 0)),
            project_allowance=Money.from_decimal(getattr(salary_dto, 'project_allowance', 0)),
            deputation_allowance=Money.from_decimal(getattr(salary_dto, 'deputation_allowance', 0)),
            overtime_allowance=Money.from_decimal(getattr(salary_dto, 'overtime_allowance', 0)),
            interim_relief=Money.from_decimal(getattr(salary_dto, 'interim_relief', 0)),
            tiffin_allowance=Money.from_decimal(getattr(salary_dto, 'tiffin_allowance', 0)),
            fixed_medical_allowance=Money.from_decimal(getattr(salary_dto, 'fixed_medical_allowance', 0)),
            servant_allowance=Money.from_decimal(getattr(salary_dto, 'servant_allowance', 0)),
            any_other_allowance=Money.from_decimal(getattr(salary_dto, 'any_other_allowance', 0)),
            any_other_allowance_exemption=Money.from_decimal(getattr(salary_dto, 'any_other_allowance_exemption', 0)),
            govt_employees_outside_india_allowance=Money.from_decimal(getattr(salary_dto, 'govt_employees_outside_india_allowance', 0)),
            supreme_high_court_judges_allowance=Money.from_decimal(getattr(salary_dto, 'supreme_high_court_judges_allowance', 0)),
            judge_compensatory_allowance=Money.from_decimal(getattr(salary_dto, 'judge_compensatory_allowance', 0)),
            section_10_14_special_allowances=Money.from_decimal(getattr(salary_dto, 'section_10_14_special_allowances', 0)),
            travel_on_tour_allowance=Money.from_decimal(getattr(salary_dto, 'travel_on_tour_allowance', 0)),
            tour_daily_charge_allowance=Money.from_decimal(getattr(salary_dto, 'tour_daily_charge_allowance', 0)),
            conveyance_in_performace_of_duties=Money.from_decimal(getattr(salary_dto, 'conveyance_in_performace_of_duties', 0)),
            helper_in_performace_of_duties=Money.from_decimal(getattr(salary_dto, 'helper_in_performace_of_duties', 0)),
            academic_research=Money.from_decimal(getattr(salary_dto, 'academic_research', 0)),
            uniform_allowance=Money.from_decimal(getattr(salary_dto, 'uniform_allowance', 0))
        )
        
        return SalaryIncome(
            effective_from=effective_from,
            effective_till=effective_till,
            basic_salary=Money.from_decimal(salary_dto.basic_salary),
            dearness_allowance=Money.from_decimal(salary_dto.dearness_allowance),
            hra_provided=Money.from_decimal(salary_dto.hra_provided),
            special_allowance=Money.from_decimal(salary_dto.special_allowance),
            # Optional components with defaults
            bonus=Money.from_decimal(getattr(salary_dto, 'bonus', 0)),
            commission=Money.from_decimal(getattr(salary_dto, 'commission', 0)),
            arrears=Money.from_decimal(getattr(salary_dto, 'arrears', 0)),
            specific_allowances=specific_allowances
        )
    
    def _convert_deductions_dto_to_entity(self, deductions_dto) -> TaxDeductions:
        """Convert deductions DTO to domain entity."""
        
        # Initialize with default values
        deductions = TaxDeductions()
        
        if not deductions_dto:
            logger.debug("Deductions DTO is None or empty, returning default deductions")
            return deductions

        try:
            # Handle both nested DTO structure and flat dictionary structure from frontend
            if hasattr(deductions_dto, 'dict'):
                # If it's a Pydantic model, convert to dict
                deductions_data = deductions_dto.dict()
            elif isinstance(deductions_dto, dict):
                # If it's already a dictionary (from frontend)
                deductions_data = deductions_dto
            else:
                # If it's an object with attributes
                deductions_data = deductions_dto.__dict__ if hasattr(deductions_dto, '__dict__') else {}
            
            logger.info(f"Processing deductions data: {type(deductions_data)} with keys: {list(deductions_data.keys()) if isinstance(deductions_data, dict) else 'N/A'}")
            logger.debug(f"Full deductions data received: {deductions_data}")
        except Exception as e:
            logger.error(f"Error processing deductions DTO structure: {str(e)}")
            return deductions

        # Helper function to safely get values
        def safe_get(data, key, default=0):
            if isinstance(data, dict):
                return data.get(key, default)
            return getattr(data, key, default) if hasattr(data, key) else default
        
        # Helper function to safely convert values to Money
        def safe_money_from_value(value, default=0):
            """Safely convert a value to Money, handling various edge cases."""
            import decimal
            try:
                # Handle None or empty values
                if value is None or value == "":
                    return Money.from_decimal(default)
                
                # Handle string values that might be invalid
                if isinstance(value, str):
                    # Strip whitespace and handle common invalid values
                    value = value.strip()
                    if value.lower() in ['null', 'undefined', 'nan', 'none', '']:
                        return Money.from_decimal(default)
                
                # Try to convert to float first, then to decimal
                if isinstance(value, (int, float)):
                    return Money.from_decimal(float(value))
                elif isinstance(value, str):
                    return Money.from_decimal(float(value))
                else:
                    # For any other type, try direct conversion
                    return Money.from_decimal(value)
                    
            except (ValueError, TypeError, decimal.InvalidOperation, decimal.ConversionSyntax) as e:
                logger.warning(f"Failed to convert value '{value}' to Money, using default {default}: {str(e)}")
                return Money.from_decimal(default)

        # Map Section 80C fields - handle both nested and flat structures
        try:
            section_80c_data = safe_get(deductions_data, 'section_80c', {})
            section_80c_keys = [
                'life_insurance_premium', 'epf_contribution', 'ppf_contribution', 
                'nsc_investment', 'tax_saving_fd', 'elss_investment', 'home_loan_principal',
                'tuition_fees', 'ulip_premium', 'sukanya_samriddhi', 'stamp_duty_property',
                'senior_citizen_savings', 'other_80c_investments'
            ]
            
            if section_80c_data or any(key in deductions_data for key in section_80c_keys):
                logger.debug(f"Processing Section 80C data. Nested: {section_80c_data}, Flat keys present: {[k for k in section_80c_keys if k in deductions_data]}")
                
                # Handle nested structure
                if section_80c_data:
                    deductions.section_80c.life_insurance_premium = safe_money_from_value(safe_get(section_80c_data, 'life_insurance_premium', 0))
                    deductions.section_80c.epf_contribution = safe_money_from_value(safe_get(section_80c_data, 'epf_contribution', 0))
                    deductions.section_80c.ppf_contribution = safe_money_from_value(safe_get(section_80c_data, 'ppf_contribution', 0))
                    deductions.section_80c.nsc_investment = safe_money_from_value(safe_get(section_80c_data, 'nsc_investment', 0))
                    deductions.section_80c.tax_saving_fd = safe_money_from_value(safe_get(section_80c_data, 'tax_saving_fd', 0))
                    deductions.section_80c.elss_investment = safe_money_from_value(safe_get(section_80c_data, 'elss_investment', 0))
                    deductions.section_80c.home_loan_principal = safe_money_from_value(safe_get(section_80c_data, 'home_loan_principal', 0))
                    deductions.section_80c.tuition_fees = safe_money_from_value(safe_get(section_80c_data, 'tuition_fees', 0))
                    deductions.section_80c.ulip_premium = safe_money_from_value(safe_get(section_80c_data, 'ulip_premium', 0))
                    deductions.section_80c.sukanya_samriddhi = safe_money_from_value(safe_get(section_80c_data, 'sukanya_samriddhi', 0))
                    deductions.section_80c.stamp_duty_property = safe_money_from_value(safe_get(section_80c_data, 'stamp_duty_property', 0))
                    deductions.section_80c.senior_citizen_savings = safe_money_from_value(safe_get(section_80c_data, 'senior_citizen_savings', 0))
                    deductions.section_80c.other_80c_investments = safe_money_from_value(safe_get(section_80c_data, 'other_80c_investments', 0))
                else:
                    # Handle flat structure (from frontend)
                    deductions.section_80c.life_insurance_premium = safe_money_from_value(safe_get(deductions_data, 'life_insurance_premium', 0))
                    deductions.section_80c.epf_contribution = safe_money_from_value(safe_get(deductions_data, 'epf_contribution', 0))
                    deductions.section_80c.ppf_contribution = safe_money_from_value(safe_get(deductions_data, 'ppf_contribution', 0))
                    deductions.section_80c.nsc_investment = safe_money_from_value(safe_get(deductions_data, 'nsc_investment', 0))
                    deductions.section_80c.tax_saving_fd = safe_money_from_value(safe_get(deductions_data, 'tax_saving_fd', 0))
                    deductions.section_80c.elss_investment = safe_money_from_value(safe_get(deductions_data, 'elss_investment', 0))
                    deductions.section_80c.home_loan_principal = safe_money_from_value(safe_get(deductions_data, 'home_loan_principal', 0))
                    deductions.section_80c.tuition_fees = safe_money_from_value(safe_get(deductions_data, 'tuition_fees', 0))
                    deductions.section_80c.ulip_premium = safe_money_from_value(safe_get(deductions_data, 'ulip_premium', 0))
                    deductions.section_80c.sukanya_samriddhi = safe_money_from_value(safe_get(deductions_data, 'sukanya_samriddhi', 0))
                    deductions.section_80c.stamp_duty_property = safe_money_from_value(safe_get(deductions_data, 'stamp_duty_property', 0))
                    deductions.section_80c.senior_citizen_savings = safe_money_from_value(safe_get(deductions_data, 'senior_citizen_savings', 0))
                    deductions.section_80c.other_80c_investments = safe_money_from_value(safe_get(deductions_data, 'other_80c_investments', 0))
                
                logger.debug(f"Section 80C total after conversion: {deductions.section_80c.calculate_total_investment()}")
        except Exception as e:
            logger.error(f"Error processing Section 80C deductions: {str(e)}")

        # Map Section 80D fields - handle both nested and flat structures
        try:
            section_80d_data = safe_get(deductions_data, 'section_80d', {})
            section_80d_keys = ['self_family_premium', 'parent_premium', 'preventive_health_checkup']
            
            if section_80d_data or any(key in deductions_data for key in section_80d_keys):
                logger.debug(f"Processing Section 80D data. Nested: {section_80d_data}, Flat keys present: {[k for k in section_80d_keys if k in deductions_data]}")
                
                # Handle nested structure
                if section_80d_data:
                    deductions.section_80d.self_family_premium = safe_money_from_value(safe_get(section_80d_data, 'self_family_premium', 0))
                    deductions.section_80d.parent_premium = safe_money_from_value(safe_get(section_80d_data, 'parent_premium', 0))
                    deductions.section_80d.preventive_health_checkup = safe_money_from_value(safe_get(section_80d_data, 'preventive_health_checkup', 0))
                    deductions.section_80d.parent_age = safe_get(section_80d_data, 'parent_age', 55)
                else:
                    # Handle flat structure (from frontend)
                    deductions.section_80d.self_family_premium = safe_money_from_value(safe_get(deductions_data, 'self_family_premium', 0))
                    deductions.section_80d.parent_premium = safe_money_from_value(safe_get(deductions_data, 'parent_premium', 0))
                    deductions.section_80d.preventive_health_checkup = safe_money_from_value(safe_get(deductions_data, 'preventive_health_checkup', 0))
                
                logger.debug(f"Section 80D total after conversion: {deductions.section_80d.self_family_premium.add(deductions.section_80d.parent_premium).add(deductions.section_80d.preventive_health_checkup)}")
        except Exception as e:
            logger.error(f"Error processing Section 80D deductions: {str(e)}")

        # Map HRA Exemption fields - handle both nested and flat structures
        try:
            hra_exemption_data = safe_get(deductions_data, 'hra_exemption', {})
            hra_keys = ['actual_rent_paid', 'hra_city_type']
            
            if hra_exemption_data or any(key in deductions_data for key in hra_keys):
                logger.debug(f"Processing HRA exemption data. Nested: {hra_exemption_data}, Flat keys present: {[k for k in hra_keys if k in deductions_data]}")
                
                from app.domain.entities.taxation.deductions import HRAExemption
                if hra_exemption_data:
                    actual_rent_paid = safe_get(hra_exemption_data, 'actual_rent_paid', 0)
                    hra_city_type = safe_get(hra_exemption_data, 'hra_city_type', 'non_metro')
                else:
                    # Handle flat structure (from frontend)
                    actual_rent_paid = safe_get(deductions_data, 'actual_rent_paid', 0)
                    hra_city_type = safe_get(deductions_data, 'hra_city_type', 'non_metro')
                
                deductions.hra_exemption = HRAExemption(
                    actual_rent_paid=safe_money_from_value(actual_rent_paid),
                    hra_city_type=hra_city_type
                )
                logger.debug(f"HRA exemption created with actual_rent_paid: {actual_rent_paid}, city_type: {hra_city_type}")
        except Exception as e:
            logger.error(f"Error processing HRA exemption deductions: {str(e)}")

        # Map Other Deductions fields - handle both nested and flat structures
        try:
            other_deductions_data = safe_get(deductions_data, 'other_deductions', {})
            other_deduction_keys = [
                'education_loan_interest', 'charitable_donations', 'savings_interest', 
                'nps_contribution', 'other_deductions', 'ev_loan_interest', 'political_party_contribution',
                'savings_account_interest', 'deposit_interest_senior', 'additional_nps_50k',
                'donation_100_percent_without_limit', 'donation_50_percent_without_limit',
                'donation_100_percent_with_limit', 'donation_50_percent_with_limit'
            ]
            
            # Check if we have any other deduction data (either nested or flat)
            has_nested_data = other_deductions_data and isinstance(other_deductions_data, dict) and len(other_deductions_data) > 0
            has_flat_data = any(key in deductions_data for key in other_deduction_keys)
            
            if has_nested_data or has_flat_data:
                logger.debug(f"Processing other deductions data. Nested: {other_deductions_data}, Flat keys present: {[k for k in other_deduction_keys if k in deductions_data]}")
                
                # Handle nested structure
                if has_nested_data:
                    deductions.other_deductions.education_loan_interest = safe_money_from_value(safe_get(other_deductions_data, 'education_loan_interest', 0))
                    deductions.other_deductions.charitable_donations = safe_money_from_value(safe_get(other_deductions_data, 'charitable_donations', 0))
                    deductions.other_deductions.savings_interest = safe_money_from_value(safe_get(other_deductions_data, 'savings_interest', 0))
                    deductions.other_deductions.nps_contribution = safe_money_from_value(safe_get(other_deductions_data, 'nps_contribution', 0))
                    deductions.other_deductions.other_deductions = safe_money_from_value(safe_get(other_deductions_data, 'other_deductions', 0))
                else:
                    # Handle flat structure (from frontend) - map field names correctly
                    deductions.other_deductions.education_loan_interest = safe_money_from_value(safe_get(deductions_data, 'education_loan_interest', 0))
                    
                    # Map donation fields from frontend to backend
                    donation_100_percent_wo_limit = safe_money_from_value(safe_get(deductions_data, 'donation_100_percent_without_limit', 0))
                    donation_50_percent_wo_limit = safe_money_from_value(safe_get(deductions_data, 'donation_50_percent_without_limit', 0))
                    donation_100_percent_w_limit = safe_money_from_value(safe_get(deductions_data, 'donation_100_percent_with_limit', 0))
                    donation_50_percent_w_limit = safe_money_from_value(safe_get(deductions_data, 'donation_50_percent_with_limit', 0))
                    political_party_contribution = safe_money_from_value(safe_get(deductions_data, 'political_party_contribution', 0))
                    
                    # Sum all donations for charitable_donations
                    total_donations = (
                        donation_100_percent_wo_limit.amount + 
                        donation_50_percent_wo_limit.amount + 
                        donation_100_percent_w_limit.amount + 
                        donation_50_percent_w_limit.amount + 
                        political_party_contribution.amount
                    )
                    deductions.other_deductions.charitable_donations = Money.from_decimal(total_donations)
                    
                    # Map savings interest (frontend field name is different)
                    deductions.other_deductions.savings_interest = safe_money_from_value(safe_get(deductions_data, 'savings_account_interest', 0))
                    
                    # Map NPS contribution (frontend field name is different)
                    deductions.other_deductions.nps_contribution = safe_money_from_value(safe_get(deductions_data, 'additional_nps_50k', 0))
                    
                    # Map other deductions
                    deductions.other_deductions.other_deductions = safe_money_from_value(safe_get(deductions_data, 'other_deductions', 0))
                
                # Use the correct method name for total calculation
                logger.debug(f"Other deductions total after conversion: {deductions.other_deductions.calculate_total()}")
        except Exception as e:
            logger.error(f"Error processing other deductions: {str(e)}")

        # Log final deductions total
        try:
            from app.domain.value_objects.taxation.tax_regime import TaxRegime, TaxRegimeType
            regime = TaxRegime(TaxRegimeType.NEW)  # Default to new regime for calculation
            total_deductions = deductions.calculate_total_deductions(regime)
            logger.info(f"Final deductions total after conversion: {total_deductions}")
        except Exception as e:
            logger.error(f"Error calculating total deductions: {str(e)}")
        
        return deductions
    
    def _convert_comprehensive_deductions_dto_to_entity(self, comp_deductions_dto) -> TaxDeductions:
        """Convert comprehensive deductions DTO to entity."""
        # Add defensive check for None input
        if comp_deductions_dto is None:
            logger.warning("Received None for comprehensive deductions DTO, creating default deductions")
            return self._create_default_deductions()
        
        # This method would handle the comprehensive deductions conversion
        # For now, we'll use the existing deductions conversion logic
        return self._convert_deductions_dto_to_entity(comp_deductions_dto)
    
    def _convert_perquisites_dto_to_entity(self, perquisites_dto) -> Perquisites:
        """Convert perquisites DTO to entity."""
        from app.domain.entities.taxation.perquisites import (
            AccommodationPerquisite, CarPerquisite, MedicalReimbursement, 
            LTAPerquisite, InterestFreeConcessionalLoan, ESOPPerquisite,
            UtilitiesPerquisite, FreeEducationPerquisite, MovableAssetUsage,
            LunchRefreshmentPerquisite, GiftVoucherPerquisite, 
            MonetaryBenefitsPerquisite, ClubExpensesPerquisite, DomesticHelpPerquisite,
            AccommodationType, CityPopulation, CarUseType, AssetType
        )
        
        # Helper function to safely convert to Money
        def safe_money_from_value(value, default=0):
            if value is None:
                return Money.from_decimal(Decimal(str(default)))
            return Money.from_decimal(Decimal(str(value)))
        
        # Convert accommodation perquisite
        accommodation = AccommodationPerquisite(
            accommodation_type=AccommodationType(perquisites_dto.accommodation_type),
            city_population=CityPopulation(perquisites_dto.city_population),
            license_fees=safe_money_from_value(perquisites_dto.license_fees),
            employee_rent_payment=safe_money_from_value(perquisites_dto.employee_rent_payment),
            rent_paid_by_employer=safe_money_from_value(perquisites_dto.rent_paid_by_employer),
            hotel_charges=safe_money_from_value(perquisites_dto.hotel_charges),
            stay_days=perquisites_dto.stay_days,
            furniture_cost=safe_money_from_value(perquisites_dto.furniture_cost),
            furniture_employee_payment=safe_money_from_value(perquisites_dto.furniture_employee_payment),
            is_furniture_owned_by_employer=perquisites_dto.is_furniture_owned_by_employer
        )
        # Note: basic_salary and dearness_allowance are not fields of AccommodationPerquisite; use them at calculation time if needed.
        
        # Convert car perquisite
        car = CarPerquisite(
            car_use_type=CarUseType(perquisites_dto.car_use_type),
            engine_capacity_cc=perquisites_dto.engine_capacity_cc,
            months_used=perquisites_dto.months_used,
            car_cost_to_employer=safe_money_from_value(perquisites_dto.car_cost_to_employer),
            other_vehicle_cost=safe_money_from_value(perquisites_dto.other_vehicle_cost),
            has_expense_reimbursement=perquisites_dto.has_expense_reimbursement,
            driver_provided=perquisites_dto.driver_provided
        )
        
        # Convert medical reimbursement
        medical_reimbursement = MedicalReimbursement(
            medical_reimbursement_amount=safe_money_from_value(perquisites_dto.medical_reimbursement_amount),
            is_overseas_treatment=perquisites_dto.is_overseas_treatment
        )
        
        # Convert LTA
        lta = LTAPerquisite(
            lta_amount_claimed=safe_money_from_value(perquisites_dto.lta_amount_claimed),
            lta_claimed_count=perquisites_dto.lta_claimed_count,
            public_transport_cost=safe_money_from_value(perquisites_dto.public_transport_cost)
        )
        
        # Convert interest free loan
        interest_free_loan = InterestFreeConcessionalLoan(
            loan_amount=safe_money_from_value(perquisites_dto.loan_amount),
            outstanding_amount=safe_money_from_value(perquisites_dto.loan_amount),  # Assuming same as loan amount
            company_interest_rate=Decimal(str(perquisites_dto.interest_rate_charged)),
            sbi_interest_rate=Decimal(str(perquisites_dto.sbi_rate)),
            loan_months=perquisites_dto.asset_usage_months  # Using asset_usage_months as loan_months
        )
        
        # Convert ESOP
        esop = ESOPPerquisite(
            shares_exercised=perquisites_dto.esop_shares_exercised,
            exercise_price=safe_money_from_value(perquisites_dto.esop_exercise_value),
            allotment_price=safe_money_from_value(perquisites_dto.esop_fair_market_value)
        )
        
        # Convert utilities
        utilities = UtilitiesPerquisite(
            gas_paid_by_employer=safe_money_from_value(perquisites_dto.gas_electricity_water_amount),
            electricity_paid_by_employer=Money.zero(),
            water_paid_by_employer=Money.zero(),
            gas_paid_by_employee=Money.zero(),
            electricity_paid_by_employee=Money.zero(),
            water_paid_by_employee=Money.zero(),
            is_gas_manufactured_by_employer=False,
            is_electricity_manufactured_by_employer=False,
            is_water_manufactured_by_employer=False
        )
        
        # Convert free education
        free_education = FreeEducationPerquisite(
            monthly_expenses_child1=safe_money_from_value(perquisites_dto.free_education_amount if perquisites_dto.is_children_education else 0),
            monthly_expenses_child2=Money.zero(),
            months_child1=12 if perquisites_dto.is_children_education else 0,
            months_child2=0,
            employer_maintained_1st_child=perquisites_dto.is_children_education,
            employer_maintained_2nd_child=False
        )
        
        # Convert movable asset usage
        movable_asset_usage = MovableAssetUsage(
            asset_type=AssetType("Others"),
            asset_value=safe_money_from_value(perquisites_dto.movable_asset_value),
            employee_payment=Money.zero(),
            is_employer_owned=True
        )
        
        # Convert lunch refreshment
        lunch_refreshment = LunchRefreshmentPerquisite(
            employer_cost=safe_money_from_value(perquisites_dto.lunch_refreshment_amount),
            employee_payment=Money.zero(),
            meal_days_per_year=365
        )
        
        # Convert domestic help
        domestic_help = DomesticHelpPerquisite(
            domestic_help_paid_by_employer=safe_money_from_value(perquisites_dto.domestic_help_amount),
            domestic_help_paid_by_employee=Money.zero()
        )
        
        # Convert gift voucher
        gift_voucher = GiftVoucherPerquisite(
            gift_voucher_amount=Money.zero()
        )
        
        # Convert monetary benefits
        monetary_benefits = MonetaryBenefitsPerquisite(
            monetary_amount_paid_by_employer=Money.zero(),
            expenditure_for_official_purpose=Money.zero(),
            amount_paid_by_employee=Money.zero()
        )
        
        # Convert club expenses
        club_expenses = ClubExpensesPerquisite(
            club_expenses_paid_by_employer=Money.zero(),
            club_expenses_paid_by_employee=Money.zero(),
            club_expenses_for_official_purpose=Money.zero()
        )
        
        return Perquisites(
            accommodation=accommodation,
            car=car,
            medical_reimbursement=medical_reimbursement,
            lta=lta,
            interest_free_loan=interest_free_loan,
            esop=esop,
            utilities=utilities,
            free_education=free_education,
            movable_asset_usage=movable_asset_usage,
            movable_asset_transfer=None,  # Not in flat structure
            lunch_refreshment=lunch_refreshment,
            gift_voucher=gift_voucher,
            monetary_benefits=monetary_benefits,
            club_expenses=club_expenses,
            domestic_help=domestic_help
        )
    
    def _convert_house_property_income_dto_to_entity(self, house_property_income_dto) -> HousePropertyIncome:
        """Convert house property DTO to entity."""
        from app.domain.entities.taxation.house_property_income import PropertyType
        
        # Map property type to enum
        property_type_mapping = {
            "Self-Occupied": PropertyType.SELF_OCCUPIED,
            "Let-Out": PropertyType.LET_OUT
        }
        property_type = property_type_mapping.get(house_property_income_dto.property_type, PropertyType.SELF_OCCUPIED)
        
        return HousePropertyIncome(
            property_type=property_type,
            address=getattr(house_property_income_dto, 'address', ''),
            annual_rent_received=Money.from_decimal(house_property_income_dto.annual_rent_received),
            municipal_taxes_paid=Money.from_decimal(house_property_income_dto.municipal_taxes_paid),
            home_loan_interest=Money.from_decimal(house_property_income_dto.home_loan_interest),
            pre_construction_interest=Money.from_decimal(house_property_income_dto.pre_construction_interest)
        )
    
    def _convert_capital_gains_dto_to_entity(self, capital_gains_dto) -> CapitalGainsIncome:
        """Convert capital gains DTO to entity."""
        return CapitalGainsIncome(
            stcg_111a_equity_stt=Money.from_decimal(capital_gains_dto.stcg_111a_equity_stt),
            stcg_other_assets=Money.from_decimal(capital_gains_dto.stcg_other_assets),
            stcg_debt_mf=Money.from_decimal(capital_gains_dto.stcg_debt_mf),
            ltcg_112a_equity_stt=Money.from_decimal(capital_gains_dto.ltcg_112a_equity_stt),
            ltcg_other_assets=Money.from_decimal(capital_gains_dto.ltcg_other_assets),
            ltcg_debt_mf=Money.from_decimal(capital_gains_dto.ltcg_debt_mf)
        )
    
    def _convert_retirement_benefits_dto_to_entity(self, retirement_dto) -> RetirementBenefits:
        """Convert retirement benefits DTO to entity."""
        # Handle flat structure (from frontend)
        if hasattr(retirement_dto, 'gratuity_amount'):
            # Convert flat structure to nested structure first
            flat_dto = FlatRetirementBenefitsDTO(
                gratuity_amount=retirement_dto.gratuity_amount,
                leave_encashment_amount=retirement_dto.leave_encashment_amount,
                vrs_amount=retirement_dto.vrs_amount,
                pension_amount=retirement_dto.pension_amount,
                commuted_pension_amount=retirement_dto.commuted_pension_amount,
                other_retirement_benefits=retirement_dto.other_retirement_benefits
            )
            retirement_dto = flat_dto.to_nested_structure()
        
        # Convert leave encashment
        leave_encashment = None
        if retirement_dto.leave_encashment:
            le_dto = retirement_dto.leave_encashment
            leave_encashment = LeaveEncashment(
                leave_encashment_amount=Money.from_decimal(le_dto.leave_encashment_amount),
                average_monthly_salary=Money.from_decimal(le_dto.average_monthly_salary),
                leave_days_encashed=le_dto.leave_days_encashed,
                is_govt_employee=le_dto.is_govt_employee,
                during_employment=le_dto.during_employment
            )
        
        # Convert gratuity
        gratuity = None
        if retirement_dto.gratuity:
            gr_dto = retirement_dto.gratuity
            gratuity = Gratuity(
                gratuity_amount=Money.from_decimal(gr_dto.gratuity_amount),
                monthly_salary=Money.from_decimal(gr_dto.monthly_salary),
                service_years=Decimal(str(gr_dto.service_years)),
                is_govt_employee=gr_dto.is_govt_employee
            )
        
        # Convert VRS
        vrs = None
        if retirement_dto.vrs:
            vrs_dto = retirement_dto.vrs
            vrs = VRS(
                vrs_amount=Money.from_decimal(vrs_dto.vrs_amount),
                monthly_salary=Money.from_decimal(vrs_dto.monthly_salary),
                age=vrs_dto.age,
                service_years=Decimal(str(vrs_dto.service_years))
            )
        
        # Convert pension
        pension = None
        if retirement_dto.pension:
            pen_dto = retirement_dto.pension
            pension = Pension(
                regular_pension=Money.from_decimal(pen_dto.regular_pension),
                commuted_pension=Money.from_decimal(pen_dto.commuted_pension),
                total_pension=Money.from_decimal(pen_dto.total_pension),
                is_govt_employee=pen_dto.is_govt_employee,
                gratuity_received=pen_dto.gratuity_received
            )
        
        # Convert retrenchment compensation
        retrenchment_compensation = None
        if retirement_dto.retrenchment_compensation:
            rc_dto = retirement_dto.retrenchment_compensation
            retrenchment_compensation = RetrenchmentCompensation(
                retrenchment_amount=Money.from_decimal(rc_dto.retrenchment_amount),
                monthly_salary=Money.from_decimal(rc_dto.monthly_salary),
                service_years=Decimal(str(rc_dto.service_years))
            )
        
        return RetirementBenefits(
            leave_encashment=leave_encashment,
            gratuity=gratuity,
            vrs=vrs,
            pension=pension,
            retrenchment_compensation=retrenchment_compensation
        )
    
    def _convert_other_income_dto_to_entity(self, other_income_dto) -> OtherIncome:
        """Convert other income DTO to entity."""
        # Convert interest income
        interest_income = None
        if other_income_dto.interest_income:
            int_dto = other_income_dto.interest_income
            # Handle field name mapping between frontend and backend
            # Frontend uses: savings_interest, fd_interest, rd_interest, post_office_interest
            # Backend expects: savings_account_interest, fixed_deposit_interest, recurring_deposit_interest, post_office_interest
            
            # Get values with fallback to handle both naming conventions
            savings_interest = getattr(int_dto, 'savings_account_interest', None)
            if savings_interest is None:
                savings_interest = getattr(int_dto, 'savings_interest', 0)
            
            fd_interest = getattr(int_dto, 'fixed_deposit_interest', None)
            if fd_interest is None:
                fd_interest = getattr(int_dto, 'fd_interest', 0)
            
            rd_interest = getattr(int_dto, 'recurring_deposit_interest', None)
            if rd_interest is None:
                rd_interest = getattr(int_dto, 'rd_interest', 0)
            
            post_office_interest = getattr(int_dto, 'post_office_interest', 0)
            
            interest_income = InterestIncome(
                savings_account_interest=Money.from_decimal(savings_interest),
                fixed_deposit_interest=Money.from_decimal(fd_interest),
                recurring_deposit_interest=Money.from_decimal(rd_interest),
                post_office_interest=Money.from_decimal(post_office_interest)
            )
        
        # Convert house property income if present
        house_property_income = None
        if hasattr(other_income_dto, 'house_property_income') and other_income_dto.house_property_income:
            house_property_income = self._convert_house_property_income_dto_to_entity(other_income_dto.house_property_income)
        
        # Convert capital gains income if present
        capital_gains_income = None
        if hasattr(other_income_dto, 'capital_gains_income') and other_income_dto.capital_gains_income:
            capital_gains_income = self._convert_capital_gains_dto_to_entity(other_income_dto.capital_gains_income)
        
        return OtherIncome(
            interest_income=interest_income,
            house_property_income=house_property_income,
            capital_gains_income=capital_gains_income,
            dividend_income=Money.from_decimal(other_income_dto.dividend_income),
            gifts_received=Money.from_decimal(other_income_dto.gifts_received),
            business_professional_income=Money.from_decimal(other_income_dto.business_professional_income),
            other_miscellaneous_income=Money.from_decimal(other_income_dto.other_miscellaneous_income)
        )
    
    async def _get_or_create_salary_package_record(
        self,
        employee_id: str,
        tax_year: str,
        organization_id: str,
        salary_income: SalaryIncome = None
    ) -> Tuple[SalaryPackageRecord, bool]:
        """Get existing salary package record or create a new one with defaults."""
        
        # Try to get existing record
        salary_package_record = await self.salary_package_repository.get_salary_package_record(
            employee_id, tax_year, organization_id
        )
        
        if salary_package_record:
            return salary_package_record, True
        
        # Create new record with defaults
        employee_id_vo = EmployeeId(employee_id)
        tax_year_vo = TaxYear.from_string(tax_year)
        
        # Create default salary income
        if salary_income:
            default_salary_income = salary_income
        else:
            # Use tax year boundaries for effective dates
            tax_year_start = tax_year_vo.get_start_date()
            tax_year_end = tax_year_vo.get_end_date()
            effective_from = datetime.combine(tax_year_start, datetime.min.time())
            effective_till = datetime.combine(tax_year_end, datetime.min.time())
            
            default_salary_income = SalaryIncome(
                effective_from=effective_from,
                effective_till=effective_till,
                basic_salary=Money.zero(),
                dearness_allowance=Money.zero(),
                hra_provided=Money.zero(),
                special_allowance=Money.zero(),
                bonus=Money.zero(),
                commission=Money.zero()
            )
        
        # Create default deductions
        default_deductions = TaxDeductions(
            section_80c=DeductionSection80C(),
            section_80d=DeductionSection80D(),
            section_80e=DeductionSection80E(),
            section_80g=DeductionSection80G(),
            section_80tta_ttb=DeductionSection80TTA_TTB(),
            other_deductions=OtherDeductions()
        )
        
        # Create default perquisites
        default_perquisites = self._create_default_perquisites()
        
        # Create default retirement benefits
        default_retirement_benefits = self._create_default_retirement_benefits()
        
        # Create default other income
        default_other_income = self._create_default_other_income()
        
        # Create new salary package record with correct parameters
        salary_package_record = SalaryPackageRecord(
            employee_id=employee_id_vo,
            tax_year=tax_year_vo,
            age=25,  # Default age
            regime=TaxRegime.old_regime(),  # Default to old regime
            salary_incomes=[default_salary_income],
            deductions=default_deductions,
            perquisites=default_perquisites,  # Add default perquisites
            retirement_benefits=default_retirement_benefits,  # Add default retirement benefits
            other_income=default_other_income,  # Add default other income
            organization_id=organization_id
        )
        
        return salary_package_record, False
    
    # =============================================================================
    # INDIVIDUAL COMPONENT UPDATE METHODS
    # =============================================================================
    
    async def update_salary_component(
        self,
        request: "UpdateSalaryComponentRequest",
        organization_id: str
    ) -> "ComponentUpdateResponse":
        """Update salary component individually using SalaryPackageRecord."""
        
        try:
            # Convert DTO to entity
            salary_income = self._convert_salary_dto_to_entity(request.salary_income)

            # Get or create salary package record
            salary_package_record, found_record = await self._get_or_create_salary_package_record(
                request.employee_id, request.tax_year, organization_id, salary_income
            )
            
            # Handle different modes: new revision vs update existing
            if request.force_new_revision:
                if found_record:
                    # Force create new salary revision (always add new entry)
                    salary_package_record.add_salary_income(salary_income)
            else:
                # Update mode: update existing or create first entry
                if not salary_package_record.salary_incomes:
                    # If no salary incomes exist, add the first one
                    salary_package_record.add_salary_income(salary_income)
                else:
                    # If salary incomes exist, update the latest one
                    salary_package_record.update_latest_salary_income(salary_income)
            
            salary_package_record.updated_at = datetime.utcnow()
            
            # Save to database using salary package repository
            await self.salary_package_repository.save(salary_package_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=salary_package_record.salary_package_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="salary_income",
                status="success",
                message="New salary revision created successfully" if request.force_new_revision else "Salary component updated successfully",
                updated_at=salary_package_record.updated_at,
                notes=request.notes
            )
            
        except Exception as e:
            logger.error(f"Failed to update salary component: {str(e)}")
            raise
    
    async def update_perquisites_component(
        self,
        request: "UpdatePerquisitesComponentRequest",
        organization_id: str
    ) -> "ComponentUpdateResponse":
        """Update perquisites component individually using SalaryPackageRecord."""
        
        try:
            # Convert DTO to entity
            perquisites = self._convert_perquisites_dto_to_entity(request.perquisites)
            
            # Get or create salary package record (it should ideally be present)
            salary_package_record, found_record = await self._get_or_create_salary_package_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            if not found_record:
                logger.warning(f"Salary package record not found for employee {request.employee_id} in {request.tax_year}, created new one")
            
            # Update perquisites in salary package record
            salary_package_record.perquisites = perquisites
            salary_package_record.updated_at = datetime.utcnow()
            
            # Save to database using salary package repository
            await self.salary_package_repository.save(salary_package_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=salary_package_record.salary_package_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="perquisites",
                status="success",
                message="Perquisites component updated successfully",
                updated_at=salary_package_record.updated_at,
                notes=request.notes
            )
            
        except Exception as e:
            logger.error(f"Failed to update perquisites component: {str(e)}")
            raise
    
    async def update_deductions_component(
        self,
        request: "UpdateDeductionsComponentRequest",
        organization_id: str
    ) -> "ComponentUpdateResponse":
        """Update deductions component individually using SalaryPackageRecord."""
        
        try:
            logger.info(f"Starting deductions component update for employee {request.employee_id}, tax_year {request.tax_year}")
            logger.info(f"Deductions data received: {request.deductions}")
            logger.debug(f"Full request data: {request}")
            
            # Convert DTO to entity
            if request.deductions is None:
                logger.info("No deductions data provided, creating default deductions")
                deductions = self._create_default_deductions()
            else:
                logger.info("Converting deductions DTO to entity")
                deductions = self._convert_comprehensive_deductions_dto_to_entity(request.deductions)
                logger.debug(f"Converted deductions entity - Section 80C total: {deductions.section_80c.calculate_total_investment()}")

            # Get or create salary package record (it should ideally be present)
            logger.info(f"Getting or creating salary package record for employee {request.employee_id}")
            salary_package_record, found_record = await self._get_or_create_salary_package_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            if not found_record:
                logger.warning(f"Salary package record not found for employee {request.employee_id} in {request.tax_year}, created new one")
            else:
                logger.info(f"Found existing salary package record with ID: {salary_package_record.salary_package_id}")

            # Log existing deductions before update
            existing_deductions_total = salary_package_record.deductions.calculate_total_deductions(salary_package_record.regime)
            logger.info(f"Existing deductions total before update: {existing_deductions_total}")
            
            # Update deductions using the salary package record's method
            logger.info("Updating deductions on salary package record")
            salary_package_record.update_deductions(deductions)
            salary_package_record.updated_at = datetime.utcnow()
            
            # Log new deductions after update
            new_deductions_total = salary_package_record.deductions.calculate_total_deductions(salary_package_record.regime) 
            logger.info(f"New deductions total after update: {new_deductions_total}")
            
            # Save to database using salary package repository
            logger.info(f"Saving salary package record to database for organization {organization_id}")
            saved_record = await self.salary_package_repository.save(salary_package_record, organization_id)
            logger.info(f"Successfully saved salary package record. Returned record ID: {saved_record.salary_package_id}")
            
            # Verify the save by attempting to read back
            logger.info("Verifying save operation by reading back the record")
            verification_record = await self.salary_package_repository.get_salary_package_record(
                request.employee_id, request.tax_year, organization_id
            )
            if verification_record:
                verify_deductions_total = verification_record.deductions.calculate_total_deductions(verification_record.regime)
                logger.info(f"Verification successful - Deductions total in database: {verify_deductions_total}")
                if verify_deductions_total != new_deductions_total:
                    logger.error(f"MISMATCH: Expected {new_deductions_total}, but found {verify_deductions_total} in database")
            else:
                logger.error("VERIFICATION FAILED: Could not read back the saved record from database")
            
            return ComponentUpdateResponse(
                taxation_id=salary_package_record.salary_package_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="deductions",
                status="success",
                message="Deductions component updated successfully",
                updated_at=salary_package_record.updated_at,
                notes=request.notes
            )
            
        except Exception as e:
            logger.error(f"Failed to update deductions component: {str(e)}")
            raise
    
    async def update_house_property_component(
        self,
        request: "UpdateHousePropertyComponentRequest",
        organization_id: str
    ) -> "ComponentUpdateResponse":
        """Update house property component individually using SalaryPackageRecord."""
        
        try:
            # Convert DTO to entity
            house_property_income = self._convert_house_property_income_dto_to_entity(request.house_property_income)
            
            # Get or create salary package record (it should ideally be present)
            salary_package_record, found_record = await self._get_or_create_salary_package_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            if not found_record:
                logger.warning(f"Salary package record not found for employee {request.employee_id} in {request.tax_year}, created new one")
            
            # Create or update other_income
            if not salary_package_record.other_income:
                salary_package_record.other_income = self._create_default_other_income()
            
            # Update house property in other income
            salary_package_record.other_income.house_property_income = house_property_income
            salary_package_record.updated_at = datetime.utcnow()
            
            # Save to database using salary package repository
            await self.salary_package_repository.save(salary_package_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=salary_package_record.salary_package_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="house_property_income",
                status="success",
                message="House property component updated successfully",
                updated_at=salary_package_record.updated_at,
                notes=request.notes
            )
            
        except Exception as e:
            logger.error(f"Failed to update house property component: {str(e)}")
            raise
    
    async def update_capital_gains_component(
        self,
        request: "UpdateCapitalGainsComponentRequest",
        organization_id: str
    ) -> "ComponentUpdateResponse":
        """Update capital gains component individually using SalaryPackageRecord."""
        
        try:
            # Convert DTO to entity
            capital_gains = self._convert_capital_gains_dto_to_entity(request.capital_gains_income)
            
            # Get or create salary package record (it should ideally be present)
            salary_package_record, found_record = await self._get_or_create_salary_package_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            if not found_record:
                logger.warning(f"Salary package record not found for employee {request.employee_id} in {request.tax_year}, created new one")
            
            # Create or update other_income
            if not salary_package_record.other_income:
                salary_package_record.other_income = self._create_default_other_income()
            
            # Update capital gains in other income
            salary_package_record.other_income.capital_gains_income = capital_gains
            salary_package_record.updated_at = datetime.utcnow()
            
            # Save to database using salary package repository
            await self.salary_package_repository.save(salary_package_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=salary_package_record.salary_package_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="capital_gains_income",
                status="success",
                message="Capital gains component updated successfully",
                updated_at=salary_package_record.updated_at,
                notes=request.notes
            )
            
        except Exception as e:
            logger.error(f"Failed to update capital gains component: {str(e)}")
            raise
    
    async def update_retirement_benefits_component(
        self,
        request: "UpdateRetirementBenefitsComponentRequest",
        organization_id: str
    ) -> "ComponentUpdateResponse":
        """Update retirement benefits component individually using SalaryPackageRecord."""
        
        try:
            # Convert DTO to entity
            retirement_benefits = self._convert_retirement_benefits_dto_to_entity(request.retirement_benefits)
            
            # Get or create salary package record (it should ideally be present)
            salary_package_record, found_record = await self._get_or_create_salary_package_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            if not found_record:
                logger.warning(f"Salary package record not found for employee {request.employee_id} in {request.tax_year}, created new one")
            
            # Update retirement benefits in salary package record
            salary_package_record.retirement_benefits = retirement_benefits
            salary_package_record.updated_at = datetime.utcnow()
            
            # Save to database using salary package repository
            await self.salary_package_repository.save(salary_package_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=salary_package_record.salary_package_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="retirement_benefits",
                status="success",
                message="Retirement benefits component updated successfully",
                updated_at=salary_package_record.updated_at,
                notes=request.notes
            )
            
        except Exception as e:
            logger.error(f"Failed to update retirement benefits component: {str(e)}")
            raise
    
    async def update_other_income_component(
        self,
        request: "UpdateOtherIncomeComponentRequest",
        organization_id: str
    ) -> "ComponentUpdateResponse":
        """Update other income component individually using SalaryPackageRecord."""
        
        try:
            # Convert DTO to entity
            other_income = self._convert_other_income_dto_to_entity(request.other_income)
            
            # Get or create salary package record (it should ideally be present)
            salary_package_record, found_record = await self._get_or_create_salary_package_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            if not found_record:
                logger.warning(f"Salary package record not found for employee {request.employee_id} in {request.tax_year}, created new one")
            
            # Update other income in salary package record
            salary_package_record.other_income = other_income
            salary_package_record.updated_at = datetime.utcnow()
            
            # Save to database using salary package repository
            await self.salary_package_repository.save(salary_package_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=salary_package_record.salary_package_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="other_income",
                status="success",
                message="Other income component updated successfully",
                updated_at=salary_package_record.updated_at,
                notes=request.notes
            )
            
        except Exception as e:
            logger.error(f"Failed to update other income component: {str(e)}")
            raise
    
    async def update_monthly_payroll_component(
        self,
        request: "UpdateMonthlyPayrollComponentRequest",
        organization_id: str
    ) -> "ComponentUpdateResponse":
        """Update monthly payroll component individually."""
        
        try:
            # Get or create taxation record
            taxation_record = await self._get_or_create_taxation_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            # Convert DTO to entity
            monthly_payroll = self._convert_monthly_payroll_dto_to_entity(request.monthly_payroll)
            
            # Update the record
            taxation_record.monthly_payroll = monthly_payroll
            taxation_record.updated_at = datetime.utcnow()
            
            # Save to database
            await self.taxation_repository.save(taxation_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=taxation_record.taxation_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="monthly_payroll",
                status="success",
                message="Monthly payroll component updated successfully",
                updated_at=taxation_record.updated_at,
                notes=request.notes
            )
            
        except Exception as e:
            logger.error(f"Failed to update monthly payroll component: {str(e)}")
            raise
    
    async def update_regime_component(
        self,
        request: "UpdateRegimeComponentRequest",
        organization_id: str
    ) -> "ComponentUpdateResponse":
        """Update tax regime component individually."""
        
        try:
            # Get or create taxation record
            taxation_record = await self._get_or_create_taxation_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            # Update regime and age
            regime_type = TaxRegimeType(request.regime_type)
            taxation_record.regime = TaxRegime(regime_type)
            taxation_record.age = request.age
            taxation_record.updated_at = datetime.utcnow()
            
            # Save to database
            await self.taxation_repository.save(taxation_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=taxation_record.taxation_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="regime",
                status="success",
                message="Tax regime component updated successfully",
                updated_at=taxation_record.updated_at,
                notes=request.notes
            )
            
        except Exception as e:
            logger.error(f"Failed to update regime component: {str(e)}")
            raise
    
    async def get_component(
        self,
        employee_id: str,
        tax_year: str,
        component_type: str,
        organization_id: str
    ) -> "ComponentResponse":
        """Get a specific component from salary package record."""
        
        try:
            # Get or create salary package record instead of taxation record
            salary_package_record, found_record = await self._get_or_create_salary_package_record(
                employee_id, tax_year, organization_id
            )
            
            # Extract component data based on type
            component_data = self._extract_component_data_from_salary_package(salary_package_record, component_type)
            
            return ComponentResponse(
                taxation_id=salary_package_record.salary_package_id,
                employee_id=employee_id,
                tax_year=tax_year,
                component_type=component_type,
                component_data=component_data,
                last_updated=salary_package_record.updated_at,
                notes=None  # Could be enhanced to store component-specific notes
            )
            
        except Exception as e:
            logger.error(f"Failed to get component {component_type}: {str(e)}")
            raise
    
    async def get_taxation_record_status(
        self,
        employee_id: str,
        tax_year: str,
        organization_id: str
    ) -> "TaxationRecordStatusResponse":
        """Get status of all components in a taxation record."""
        
        try:
            # Get taxation record
            taxation_record = await self.taxation_repository.get_taxation_record(
                employee_id, tax_year, organization_id
            )
            
            if not taxation_record:
                raise ValueError(f"Taxation record not found for employee {employee_id} and tax year {tax_year}")
            
            # Build components status
            components_status = self._build_components_status(taxation_record)
            
            # Determine overall status
            overall_status = self._determine_overall_status(components_status)
            
            return TaxationRecordStatusResponse(
                taxation_id=taxation_record.taxation_id,
                employee_id=employee_id,
                tax_year=tax_year,
                regime_type=taxation_record.regime.regime_type.value,
                age=taxation_record.age,
                components_status=components_status,
                overall_status=overall_status,
                last_updated=taxation_record.updated_at,
                is_final=taxation_record.is_final
            )
            
        except Exception as e:
            logger.error(f"Failed to get taxation record status: {str(e)}")
            raise
    
    def _extract_component_data_from_salary_package(self, salary_package_record: SalaryPackageRecord, component_type: str) -> Dict[str, Any]:
        """Extract component data from salary package record."""
        
        # Handle frontend component type aliases
        component_type_mapping = {
            "salary": "salary_income",
            "house_property_income": "house_property_income",
            "capital_gains": "capital_gains_income",
            "retirement_benefits": "retirement_benefits",
            "other_income": "other_income",
            "monthly_payroll": "monthly_payroll"
        }
        
        # Map frontend component type to backend component type
        mapped_component_type = component_type_mapping.get(component_type, component_type)
        
        if mapped_component_type == "salary_income":
            # For salary package record, we use the latest salary income
            latest_salary = salary_package_record.get_latest_salary_income()
            return self._serialize_salary_income_with_history(salary_package_record)
        elif mapped_component_type == "perquisites":
            return self._serialize_perquisites(salary_package_record.perquisites) if salary_package_record.perquisites else {}
        elif mapped_component_type == "deductions":
            return self._serialize_deductions(salary_package_record.deductions)
        elif mapped_component_type == "house_property_income":
            if salary_package_record.other_income and salary_package_record.other_income.house_property_income:
                return self._serialize_house_property_income(salary_package_record.other_income.house_property_income)
            return {}
        elif mapped_component_type == "capital_gains_income":
            if salary_package_record.other_income and salary_package_record.other_income.capital_gains_income:
                return self._serialize_capital_gains_income(salary_package_record.other_income.capital_gains_income)
            return {}
        elif mapped_component_type == "retirement_benefits":
            return self._serialize_retirement_benefits(salary_package_record.retirement_benefits) if salary_package_record.retirement_benefits else {}
        elif mapped_component_type == "other_income":
            return self._serialize_other_income(salary_package_record.other_income) if salary_package_record.other_income else {}
        elif mapped_component_type == "monthly_payroll":
            # Monthly payroll is not supported in salary package record, return empty
            return {}
        elif mapped_component_type == "regime":
            return {
                "regime_type": salary_package_record.regime.regime_type.value,
                "age": salary_package_record.age
            }
        else:
            raise ValueError(f"Unknown component type: {component_type}")
    
    def _serialize_salary_income_with_history(self, salary_package_record: SalaryPackageRecord) -> Dict[str, Any]:
        """Serialize salary income with history from salary package record."""
        latest_salary = salary_package_record.get_latest_salary_income()
        
        # Get basic salary serialization
        salary_data = self._serialize_salary_income(latest_salary)
        
        # Add salary history information
        salary_data["salary_history"] = [
            {
                "index": i,
                "gross_salary": salary.calculate_gross_salary().to_float(),
                "basic_salary": salary.basic_salary.to_float(),
                "special_allowance": salary.special_allowance.to_float(),
                "hra_provided": salary.hra_provided.to_float(),
                "bonus": salary.bonus.to_float(),
                "commission": salary.commission.to_float()
            }
            for i, salary in enumerate(salary_package_record.salary_incomes)
        ]
        
        salary_data["salary_incomes_count"] = len(salary_package_record.salary_incomes)
        salary_data["is_latest"] = True
        
        return salary_data
    
    def _determine_overall_status(self, components_status: Dict[str, Dict[str, Any]]) -> str:
        """Determine overall status based on component statuses."""
        
        required_components = ["salary", "deductions", "regime"]
        optional_components = ["perquisites", "house_property_income", "capital-gains", 
                             "retirement-benefits", "other-income", "monthly-payroll"]
        
        # Check required components
        for component in required_components:
            if component not in components_status or components_status[component]["status"] != "complete":
                return "incomplete"
        
        # Count optional components with data
        optional_with_data = sum(
            1 for component in optional_components
            if component in components_status and components_status[component]["status"] == "complete"
        )
        
        if optional_with_data == 0:
            return "basic_complete"
        elif optional_with_data >= 3:
            return "comprehensive_complete"
        else:
            return "partial_complete"
    
    # Serialization helper methods for components
    def _serialize_salary_income(self, salary_income: SalaryIncome) -> Dict[str, Any]:
        """Serialize salary income to dict."""
        if not salary_income:
            return {}
        
        # Base salary components
        result = {
            "basic_salary": float(salary_income.basic_salary.amount),
            "dearness_allowance": float(salary_income.dearness_allowance.amount),
            "hra_provided": float(salary_income.hra_provided.amount),
            "special_allowance": float(salary_income.special_allowance.amount),
            "bonus": float(salary_income.bonus.amount),
            "commission": float(salary_income.commission.amount),
            # HRA details are now in deductions module, not salary
            "hra_city_type": "metro",  # Default value for frontend compatibility
            "actual_rent_paid": 0.0,   # Default value for frontend compatibility
        }
        
        # Add specific allowances if available
        if salary_income.specific_allowances:
            specific_allowances_data = {
                "city_compensatory_allowance": float(salary_income.specific_allowances.city_compensatory_allowance.amount),
                "rural_allowance": float(salary_income.specific_allowances.rural_allowance.amount),
                "proctorship_allowance": float(salary_income.specific_allowances.proctorship_allowance.amount),
                "wardenship_allowance": float(salary_income.specific_allowances.wardenship_allowance.amount),
                "project_allowance": float(salary_income.specific_allowances.project_allowance.amount),
                "deputation_allowance": float(salary_income.specific_allowances.deputation_allowance.amount),
                "interim_relief": float(salary_income.specific_allowances.interim_relief.amount),
                "tiffin_allowance": float(salary_income.specific_allowances.tiffin_allowance.amount),
                "overtime_allowance": float(salary_income.specific_allowances.overtime_allowance.amount),
                "servant_allowance": float(salary_income.specific_allowances.servant_allowance.amount),
                "hills_high_altd_allowance": float(salary_income.specific_allowances.hills_allowance.amount),
                "border_remote_allowance": float(salary_income.specific_allowances.border_allowance.amount),
                "transport_employee_allowance": float(salary_income.specific_allowances.transport_employee_allowance.amount),
                "children_education_allowance": float(salary_income.specific_allowances.children_education_allowance.amount),
                "hostel_allowance": float(salary_income.specific_allowances.hostel_allowance.amount),
                "underground_mines_allowance": float(salary_income.specific_allowances.underground_mines_allowance.amount),
                "govt_employee_entertainment_allowance": float(salary_income.specific_allowances.government_entertainment_allowance.amount),
                "supreme_high_court_judges_allowance": float(salary_income.specific_allowances.supreme_high_court_judges_allowance.amount),
                "judge_compensatory_allowance": float(salary_income.specific_allowances.judge_compensatory_allowance.amount),
                "section_10_14_special_allowances": float(salary_income.specific_allowances.section_10_14_special_allowances.amount),
                "travel_on_tour_allowance": float(salary_income.specific_allowances.travel_on_tour_allowance.amount),
                "tour_daily_charge_allowance": float(salary_income.specific_allowances.tour_daily_charge_allowance.amount),
                "conveyance_in_performace_of_duties": float(salary_income.specific_allowances.conveyance_in_performace_of_duties.amount),
                "helper_in_performace_of_duties": float(salary_income.specific_allowances.helper_in_performace_of_duties.amount),
                "academic_research": float(salary_income.specific_allowances.academic_research.amount),
                "uniform_allowance": float(salary_income.specific_allowances.uniform_allowance.amount),
                "any_other_allowance_exemption": float(salary_income.specific_allowances.any_other_allowance.amount)
            }
            result.update(specific_allowances_data)
        else:
            # Add default zero values for all specific allowances if not available
            default_allowances = {
                "city_compensatory_allowance": 0.0,
                "rural_allowance": 0.0,
                "proctorship_allowance": 0.0,
                "wardenship_allowance": 0.0,
                "project_allowance": 0.0,
                "deputation_allowance": 0.0,
                "interim_relief": 0.0,
                "tiffin_allowance": 0.0,
                "overtime_allowance": 0.0,
                "servant_allowance": 0.0,
                "hills_high_altd_allowance": 0.0,
                "border_remote_allowance": 0.0,
                "transport_employee_allowance": 0.0,
                "children_education_allowance": 0.0,
                "hostel_allowance": 0.0,
                "underground_mines_allowance": 0.0,
                "govt_employee_entertainment_allowance": 0.0,
                "supreme_high_court_judges_allowance": 0.0,
                "judge_compensatory_allowance": 0.0,
                "section_10_14_special_allowances": 0.0,
                "travel_on_tour_allowance": 0.0,
                "tour_daily_charge_allowance": 0.0,
                "conveyance_in_performace_of_duties": 0.0,
                "helper_in_performace_of_duties": 0.0,
                "academic_research": 0.0,
                "uniform_allowance": 0.0,
                "any_other_allowance_exemption": 0.0
            }
            result.update(default_allowances)
        
        return result
    
    def _serialize_perquisites(self, perquisites: Perquisites) -> Dict[str, Any]:
        """Serialize perquisites to dict."""
        if not perquisites:
            return {}
        
        result = {}
        
        # Serialize accommodation
        if perquisites.accommodation:
            acc = perquisites.accommodation
            result["accommodation"] = {
                "accommodation_type": acc.accommodation_type.value,
                "city_population": acc.city_population.value,
                "license_fees": float(acc.license_fees.amount),
                "employee_rent_payment": float(acc.employee_rent_payment.amount),
                "rent_paid_by_employer": float(acc.rent_paid_by_employer.amount),
                "hotel_charges": float(acc.hotel_charges.amount),
                "stay_days": acc.stay_days,
                "furniture_cost": float(acc.furniture_cost.amount),
                "furniture_employee_payment": float(acc.furniture_employee_payment.amount),
                "is_furniture_owned_by_employer": acc.is_furniture_owned_by_employer
            }
        
        # Serialize car
        if perquisites.car:
            car = perquisites.car
            result["car"] = {
                "car_use_type": car.car_use_type.value,
                "engine_capacity_cc": car.engine_capacity_cc,
                "months_used": car.months_used,
                "car_cost_to_employer": float(car.car_cost_to_employer.amount),
                "other_vehicle_cost": float(car.other_vehicle_cost.amount),
                "has_expense_reimbursement": car.has_expense_reimbursement,
                "driver_provided": car.driver_provided
            }
        
        # Serialize medical reimbursement
        if perquisites.medical_reimbursement:
            med = perquisites.medical_reimbursement
            result["medical_reimbursement"] = {
                "medical_reimbursement_amount": float(med.medical_reimbursement_amount.amount),
                "is_overseas_treatment": med.is_overseas_treatment
            }
        
        # Serialize LTA
        if perquisites.lta:
            lta = perquisites.lta
            result["lta"] = {
                "lta_amount_claimed": float(lta.lta_amount_claimed.amount),
                "lta_claimed_count": lta.lta_claimed_count,
                "public_transport_cost": float(lta.public_transport_cost.amount)
            }
        
        # Serialize interest free loan
        if perquisites.interest_free_loan:
            loan = perquisites.interest_free_loan
            result["interest_free_loan"] = {
                "loan_amount": float(loan.loan_amount.amount),
                "outstanding_amount": float(loan.outstanding_amount.amount),
                "company_interest_rate": float(loan.company_interest_rate),
                "sbi_interest_rate": float(loan.sbi_interest_rate),
                "loan_months": loan.loan_months
            }
        
        # Serialize ESOP
        if perquisites.esop:
            esop = perquisites.esop
            result["esop"] = {
                "shares_exercised": esop.shares_exercised,
                "exercise_price": float(esop.exercise_price.amount),
                "allotment_price": float(esop.allotment_price.amount)
            }
        
        # Serialize utilities
        if perquisites.utilities:
            util = perquisites.utilities
            result["utilities"] = {
                "gas_paid_by_employer": float(util.gas_paid_by_employer.amount),
                "electricity_paid_by_employer": float(util.electricity_paid_by_employer.amount),
                "water_paid_by_employer": float(util.water_paid_by_employer.amount),
                "gas_paid_by_employee": float(util.gas_paid_by_employee.amount),
                "electricity_paid_by_employee": float(util.electricity_paid_by_employee.amount),
                "water_paid_by_employee": float(util.water_paid_by_employee.amount),
                "is_gas_manufactured_by_employer": util.is_gas_manufactured_by_employer,
                "is_electricity_manufactured_by_employer": util.is_electricity_manufactured_by_employer,
                "is_water_manufactured_by_employer": util.is_water_manufactured_by_employer
            }
        
        # Serialize free education
        if perquisites.free_education:
            edu = perquisites.free_education
            result["free_education"] = {
                "monthly_expenses_child1": float(edu.monthly_expenses_child1.amount),
                "monthly_expenses_child2": float(edu.monthly_expenses_child2.amount),
                "months_child1": edu.months_child1,
                "months_child2": edu.months_child2,
                "employer_maintained_1st_child": edu.employer_maintained_1st_child,
                "employer_maintained_2nd_child": edu.employer_maintained_2nd_child
            }
        
        # Serialize lunch refreshment
        if perquisites.lunch_refreshment:
            lunch = perquisites.lunch_refreshment
            result["lunch_refreshment"] = {
                "employer_cost": float(lunch.employer_cost.amount),
                "employee_payment": float(lunch.employee_payment.amount),
                "meal_days_per_year": lunch.meal_days_per_year
            }
        
        # Serialize domestic help
        if perquisites.domestic_help:
            help_obj = perquisites.domestic_help
            result["domestic_help"] = {
                "domestic_help_paid_by_employer": float(help_obj.domestic_help_paid_by_employer.amount),
                "domestic_help_paid_by_employee": float(help_obj.domestic_help_paid_by_employee.amount)
            }
        
        return result
    
    def _serialize_deductions(self, deductions: TaxDeductions) -> Dict[str, Any]:
        """Serialize deductions to dict with comprehensive breakdown."""
        if not deductions:
            return {
                "hra_exemption": {"actual_rent_paid": 0.0, "hra_city_type": "non_metro"},
                "section_80c": {
                    "life_insurance_premium": 0.0, "epf_contribution": 0.0, "ppf_contribution": 0.0,
                    "nsc_investment": 0.0, "tax_saving_fd": 0.0, "elss_investment": 0.0,
                    "home_loan_principal": 0.0, "tuition_fees": 0.0, "ulip_premium": 0.0,
                    "sukanya_samriddhi": 0.0, "stamp_duty_property": 0.0, "senior_citizen_savings": 0.0,
                    "other_80c_investments": 0.0, "total_invested": 0.0, "limit": 150000, "remaining_limit": 150000
                },
                "section_80ccc": {"pension_fund_contribution": 0.0},
                "section_80ccd": {
                    "employee_nps_contribution": 0.0, "additional_nps_contribution": 0.0,
                    "employer_nps_contribution": 0.0, "limit_80ccd_1b": 50000
                },
                "section_80d": {
                    "self_family_premium": 0.0, "parent_premium": 0.0, "preventive_health_checkup": 0.0,
                    "parent_age": 55, "self_family_limit": 25000, "parent_limit": 25000, "preventive_limit": 5000
                },
                "section_80dd": {"relation": None, "disability_percentage": None, "eligible_deduction": 0.0},
                "section_80ddb": {"dependent_age": 0, "medical_expenses": 0.0, "relation": None, "eligible_deduction": 0.0},
                "section_80e": {"education_loan_interest": 0.0, "relation": None},
                "section_80eeb": {"ev_loan_interest": 0.0, "ev_purchase_date": None, "eligible_deduction": 0.0},
                "section_80g": {
                    "pm_relief_fund": 0.0, "national_defence_fund": 0.0, "national_foundation_communal_harmony": 0.0,
                    "zila_saksharta_samiti": 0.0, "national_illness_assistance_fund": 0.0, "national_blood_transfusion_council": 0.0,
                    "national_trust_autism_fund": 0.0, "national_sports_fund": 0.0, "national_cultural_fund": 0.0,
                    "technology_development_fund": 0.0, "national_children_fund": 0.0, "cm_relief_fund": 0.0,
                    "army_naval_air_force_funds": 0.0, "swachh_bharat_kosh": 0.0, "clean_ganga_fund": 0.0,
                    "drug_abuse_control_fund": 0.0, "other_100_percent_wo_limit": 0.0, "jn_memorial_fund": 0.0,
                    "pm_drought_relief": 0.0, "indira_gandhi_memorial_trust": 0.0, "rajiv_gandhi_foundation": 0.0,
                    "other_50_percent_wo_limit": 0.0, "family_planning_donation": 0.0, "indian_olympic_association": 0.0,
                    "other_100_percent_w_limit": 0.0, "govt_charitable_donations": 0.0, "housing_authorities_donations": 0.0,
                    "religious_renovation_donations": 0.0, "other_charitable_donations": 0.0, "other_50_percent_w_limit": 0.0,
                    "total_donations": 0.0
                },
                "section_80ggc": {"political_party_contribution": 0.0},
                "section_80u": {"disability_percentage": None, "eligible_deduction": 0.0},
                "section_80tta_ttb": {
                    "savings_interest": 0.0, "fd_interest": 0.0, "rd_interest": 0.0, "post_office_interest": 0.0,
                    "age": 25, "applicable_section": "80TTA", "exemption_limit": 10000, "eligible_exemption": 0.0
                },
                "other_deductions": {
                    "education_loan_interest": 0.0, "charitable_donations": 0.0, "savings_interest": 0.0,
                    "nps_contribution": 0.0, "other_deductions": 0.0, "total": 0.0
                },
                "summary": {"total_deductions": 0.0, "total_interest_exemptions": 0.0, "combined_80c_80ccc_80ccd1": 0.0, "regime_applicable": "old"}
            }
        
        # Create comprehensive deductions structure
        result = {
            # HRA Exemption
            "hra_exemption": {
                "actual_rent_paid": float(deductions.hra_exemption.actual_rent_paid.amount) if deductions.hra_exemption else 0.0,
                "hra_city_type": deductions.hra_exemption.hra_city_type if deductions.hra_exemption else "non_metro"
            },
            
            # Section 80C - Detailed breakdown
            "section_80c": self._serialize_section_80c(deductions.section_80c),
            
            # Section 80CCC
            "section_80ccc": {
                "pension_fund_contribution": float(deductions.section_80ccc.pension_fund_contribution.amount) if deductions.section_80ccc else 0.0
            },
            
            # Section 80CCD - NPS contributions
            "section_80ccd": {
                "employee_nps_contribution": float(deductions.section_80ccd.employee_nps_contribution.amount) if deductions.section_80ccd else 0.0,
                "additional_nps_contribution": float(deductions.section_80ccd.additional_nps_contribution.amount) if deductions.section_80ccd else 0.0,
                "employer_nps_contribution": float(deductions.section_80ccd.employer_nps_contribution.amount) if deductions.section_80ccd else 0.0,
                "limit_80ccd_1b": 50000
            },
            
            # Section 80D - Health insurance
            "section_80d": self._serialize_section_80d(deductions.section_80d),
            
            # Section 80DD - Disability (Dependent)
            "section_80dd": self._serialize_section_80dd(deductions.section_80dd),
            
            # Section 80DDB - Medical treatment
            "section_80ddb": self._serialize_section_80ddb(deductions.section_80ddb),
            
            # Section 80E - Education loan interest
            "section_80e": {
                "education_loan_interest": float(deductions.section_80e.education_loan_interest.amount) if deductions.section_80e else 0.0,
                "relation": deductions.section_80e.relation.value if deductions.section_80e and deductions.section_80e.relation else None
            },
            
            # Section 80EEB - Electric vehicle loan interest
            "section_80eeb": self._serialize_section_80eeb(deductions.section_80eeb),
            
            # Section 80G - Charitable donations
            "section_80g": self._serialize_section_80g(deductions.section_80g),
            
            # Section 80GGC - Political party contributions
            "section_80ggc": {
                "political_party_contribution": float(deductions.section_80ggc.political_party_contribution.amount) if deductions.section_80ggc else 0.0
            },
            
            # Section 80U - Self disability
            "section_80u": {
                "disability_percentage": deductions.section_80u.disability_percentage.value if deductions.section_80u and deductions.section_80u.disability_percentage else None,
                "eligible_deduction": self._calculate_80u_deduction(deductions.section_80u)
            },
            
            # Section 80TTA/TTB - Interest exemptions
            "section_80tta_ttb": self._serialize_section_80tta_ttb(deductions.section_80tta_ttb),
            
            # Other deductions
            "other_deductions": {
                "education_loan_interest": float(deductions.other_deductions.education_loan_interest.amount) if deductions.other_deductions else 0.0,
                "charitable_donations": float(deductions.other_deductions.charitable_donations.amount) if deductions.other_deductions else 0.0,
                "savings_interest": float(deductions.other_deductions.savings_interest.amount) if deductions.other_deductions else 0.0,
                "nps_contribution": float(deductions.other_deductions.nps_contribution.amount) if deductions.other_deductions else 0.0,
                "other_deductions": float(deductions.other_deductions.other_deductions.amount) if deductions.other_deductions else 0.0,
                "total": float(deductions.other_deductions.calculate_total().amount) if deductions.other_deductions else 0.0
            },
            
            # Summary totals
            "summary": self._calculate_deductions_summary(deductions)
        }
        
        return result
    
    def _serialize_section_80c(self, section_80c) -> Dict[str, Any]:
        """Serialize Section 80C details."""
        if not section_80c:
            return {
                "life_insurance_premium": 0.0, "epf_contribution": 0.0, "ppf_contribution": 0.0,
                "nsc_investment": 0.0, "tax_saving_fd": 0.0, "elss_investment": 0.0,
                "home_loan_principal": 0.0, "tuition_fees": 0.0, "ulip_premium": 0.0,
                "sukanya_samriddhi": 0.0, "stamp_duty_property": 0.0, "senior_citizen_savings": 0.0,
                "other_80c_investments": 0.0, "total_invested": 0.0, "limit": 150000, "remaining_limit": 150000
            }
        
        total_invested = float(section_80c.calculate_total_investment().amount)
        limit = 150000
        remaining_limit = max(0, limit - total_invested)
        
        return {
            "life_insurance_premium": float(section_80c.life_insurance_premium.amount),
            "epf_contribution": float(section_80c.epf_contribution.amount),
            "ppf_contribution": float(section_80c.ppf_contribution.amount),
            "nsc_investment": float(section_80c.nsc_investment.amount),
            "tax_saving_fd": float(section_80c.tax_saving_fd.amount),
            "elss_investment": float(section_80c.elss_investment.amount),
            "home_loan_principal": float(section_80c.home_loan_principal.amount),
            "tuition_fees": float(section_80c.tuition_fees.amount),
            "ulip_premium": float(section_80c.ulip_premium.amount),
            "sukanya_samriddhi": float(section_80c.sukanya_samriddhi.amount),
            "stamp_duty_property": float(section_80c.stamp_duty_property.amount),
            "senior_citizen_savings": float(section_80c.senior_citizen_savings.amount),
            "other_80c_investments": float(section_80c.other_80c_investments.amount),
            "total_invested": total_invested,
            "limit": limit,
            "remaining_limit": remaining_limit
        }
    
    def _serialize_section_80d(self, section_80d) -> Dict[str, Any]:
        """Serialize Section 80D details."""
        if not section_80d:
            return {
                "self_family_premium": 0.0, "parent_premium": 0.0, "preventive_health_checkup": 0.0,
                "parent_age": 55, "self_family_limit": 25000, "parent_limit": 25000, "preventive_limit": 5000
            }
        
        return {
            "self_family_premium": float(section_80d.self_family_premium.amount),
            "parent_premium": float(section_80d.parent_premium.amount),
            "preventive_health_checkup": float(section_80d.preventive_health_checkup.amount),
            "parent_age": section_80d.parent_age,
            "self_family_limit": float(section_80d.calculate_self_family_limit(30).amount),
            "parent_limit": float(section_80d.calculate_parent_limit().amount),
            "preventive_limit": 5000.0
        }
    
    def _serialize_section_80dd(self, section_80dd) -> Dict[str, Any]:
        """Serialize Section 80DD details."""
        if not section_80dd:
            return {"relation": None, "disability_percentage": None, "eligible_deduction": 0.0}
        
        from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
        regime = TaxRegime(TaxRegimeType.OLD)
        
        return {
            "relation": section_80dd.relation.value if section_80dd.relation else None,
            "disability_percentage": section_80dd.disability_percentage.value if section_80dd.disability_percentage else None,
            "eligible_deduction": float(section_80dd.calculate_eligible_deduction(regime).amount)
        }
    
    def _serialize_section_80ddb(self, section_80ddb) -> Dict[str, Any]:
        """Serialize Section 80DDB details."""
        if not section_80ddb:
            return {"dependent_age": 0, "medical_expenses": 0.0, "relation": None, "eligible_deduction": 0.0}
        
        from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
        regime = TaxRegime(TaxRegimeType.OLD)
        
        return {
            "dependent_age": section_80ddb.dependent_age,
            "medical_expenses": float(section_80ddb.medical_expenses.amount),
            "relation": section_80ddb.relation.value if section_80ddb.relation else None,
            "eligible_deduction": float(section_80ddb.calculate_eligible_deduction(regime).amount)
        }
    
    def _serialize_section_80eeb(self, section_80eeb) -> Dict[str, Any]:
        """Serialize Section 80EEB details."""
        if not section_80eeb:
            return {"ev_loan_interest": 0.0, "ev_purchase_date": None, "eligible_deduction": 0.0}
        
        from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
        regime = TaxRegime(TaxRegimeType.OLD)
        
        return {
            "ev_loan_interest": float(section_80eeb.ev_loan_interest.amount),
            "ev_purchase_date": section_80eeb.ev_purchase_date.isoformat() if section_80eeb.ev_purchase_date else None,
            "eligible_deduction": float(section_80eeb.calculate_eligible_deduction(regime).amount)
        }
    
    def _serialize_section_80g(self, section_80g) -> Dict[str, Any]:
        """Serialize Section 80G details."""
        if not section_80g:
            return {
                "pm_relief_fund": 0.0, "national_defence_fund": 0.0, "national_foundation_communal_harmony": 0.0,
                "zila_saksharta_samiti": 0.0, "national_illness_assistance_fund": 0.0, "national_blood_transfusion_council": 0.0,
                "national_trust_autism_fund": 0.0, "national_sports_fund": 0.0, "national_cultural_fund": 0.0,
                "technology_development_fund": 0.0, "national_children_fund": 0.0, "cm_relief_fund": 0.0,
                "army_naval_air_force_funds": 0.0, "swachh_bharat_kosh": 0.0, "clean_ganga_fund": 0.0,
                "drug_abuse_control_fund": 0.0, "other_100_percent_wo_limit": 0.0, "jn_memorial_fund": 0.0,
                "pm_drought_relief": 0.0, "indira_gandhi_memorial_trust": 0.0, "rajiv_gandhi_foundation": 0.0,
                "other_50_percent_wo_limit": 0.0, "family_planning_donation": 0.0, "indian_olympic_association": 0.0,
                "other_100_percent_w_limit": 0.0, "govt_charitable_donations": 0.0, "housing_authorities_donations": 0.0,
                "religious_renovation_donations": 0.0, "other_charitable_donations": 0.0, "other_50_percent_w_limit": 0.0,
                "total_donations": 0.0
            }
        
        return {
            "pm_relief_fund": float(section_80g.pm_relief_fund.amount),
            "national_defence_fund": float(section_80g.national_defence_fund.amount),
            "national_foundation_communal_harmony": float(section_80g.national_foundation_communal_harmony.amount),
            "zila_saksharta_samiti": float(section_80g.zila_saksharta_samiti.amount),
            "national_illness_assistance_fund": float(section_80g.national_illness_assistance_fund.amount),
            "national_blood_transfusion_council": float(section_80g.national_blood_transfusion_council.amount),
            "national_trust_autism_fund": float(section_80g.national_trust_autism_fund.amount),
            "national_sports_fund": float(section_80g.national_sports_fund.amount),
            "national_cultural_fund": float(section_80g.national_cultural_fund.amount),
            "technology_development_fund": float(section_80g.technology_development_fund.amount),
            "national_children_fund": float(section_80g.national_children_fund.amount),
            "cm_relief_fund": float(section_80g.cm_relief_fund.amount),
            "army_naval_air_force_funds": float(section_80g.army_naval_air_force_funds.amount),
            "swachh_bharat_kosh": float(section_80g.swachh_bharat_kosh.amount),
            "clean_ganga_fund": float(section_80g.clean_ganga_fund.amount),
            "drug_abuse_control_fund": float(section_80g.drug_abuse_control_fund.amount),
            "other_100_percent_wo_limit": float(section_80g.other_100_percent_wo_limit.amount),
            "jn_memorial_fund": float(section_80g.jn_memorial_fund.amount),
            "pm_drought_relief": float(section_80g.pm_drought_relief.amount),
            "indira_gandhi_memorial_trust": float(section_80g.indira_gandhi_memorial_trust.amount),
            "rajiv_gandhi_foundation": float(section_80g.rajiv_gandhi_foundation.amount),
            "other_50_percent_wo_limit": float(section_80g.other_50_percent_wo_limit.amount),
            "family_planning_donation": float(section_80g.family_planning_donation.amount),
            "indian_olympic_association": float(section_80g.indian_olympic_association.amount),
            "other_100_percent_w_limit": float(section_80g.other_100_percent_w_limit.amount),
            "govt_charitable_donations": float(section_80g.govt_charitable_donations.amount),
            "housing_authorities_donations": float(section_80g.housing_authorities_donations.amount),
            "religious_renovation_donations": float(section_80g.religious_renovation_donations.amount),
            "other_charitable_donations": float(section_80g.other_charitable_donations.amount),
            "other_50_percent_w_limit": float(section_80g.other_50_percent_w_limit.amount),
            "total_donations": float(section_80g.calculate_total_donations().amount)
        }
    
    def _serialize_section_80tta_ttb(self, section_80tta_ttb) -> Dict[str, Any]:
        """Serialize Section 80TTA/TTB details."""
        if not section_80tta_ttb:
            return {
                "savings_interest": 0.0, "fd_interest": 0.0, "rd_interest": 0.0, "post_office_interest": 0.0,
                "age": 25, "applicable_section": "80TTA", "exemption_limit": 10000, "eligible_exemption": 0.0
            }
        
        from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
        regime = TaxRegime(TaxRegimeType.OLD)
        
        breakdown = section_80tta_ttb.get_exemption_breakdown(regime)
        
        return {
            "savings_interest": float(section_80tta_ttb.savings_interest.amount),
            "fd_interest": float(section_80tta_ttb.fd_interest.amount),
            "rd_interest": float(section_80tta_ttb.rd_interest.amount),
            "post_office_interest": float(section_80tta_ttb.post_office_interest.amount),
            "age": section_80tta_ttb.age,
            "applicable_section": breakdown.get("applicable_section", "80TTA"),
            "exemption_limit": breakdown.get("exemption_limit", 10000),
            "eligible_exemption": breakdown.get("eligible_exemption", 0.0)
        }
    
    def _calculate_80u_deduction(self, section_80u) -> float:
        """Calculate Section 80U deduction."""
        if not section_80u:
            return 0.0
        
        from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
        regime = TaxRegime(TaxRegimeType.OLD)
        
        return float(section_80u.calculate_eligible_deduction(regime).amount)
    
    def _calculate_deductions_summary(self, deductions: TaxDeductions) -> Dict[str, Any]:
        """Calculate summary totals for deductions."""
        from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
        
        # Use old regime for calculation (deductions are primarily for old regime)
        regime = TaxRegime(TaxRegimeType.OLD)
        
        total_deductions = float(deductions.calculate_total_deductions(regime).amount)
        total_interest_exemptions = float(deductions.calculate_interest_exemptions(regime).amount)
        combined_80c_80ccc_80ccd1 = float(deductions.calculate_combined_80c_80ccc_80ccd1_deduction(regime).amount)
        
        return {
            "total_deductions": total_deductions,
            "total_interest_exemptions": total_interest_exemptions,
            "combined_80c_80ccc_80ccd1": combined_80c_80ccc_80ccd1,
            "regime_applicable": "old"
        }
    
    def _serialize_house_property_income(self, house_property_income: HousePropertyIncome) -> Dict[str, Any]:
        """Serialize house property income to dict."""
        return {
            "property_type": house_property_income.property_type.value,
            "address": house_property_income.address,
            "annual_rent_received": float(house_property_income.annual_rent_received.amount),
            "municipal_taxes_paid": float(house_property_income.municipal_taxes_paid.amount),
            "home_loan_interest": float(house_property_income.home_loan_interest.amount),
            "pre_construction_interest": float(house_property_income.pre_construction_interest.amount)
        }
    
    def _serialize_capital_gains_income(self, capital_gains: CapitalGainsIncome) -> Dict[str, Any]:
        """Serialize capital gains income to dict."""
        return {
            "stcg_111a_equity_stt": float(capital_gains.stcg_111a_equity_stt.amount),
            "stcg_other_assets": float(capital_gains.stcg_other_assets.amount),
            "stcg_debt_mf": float(capital_gains.stcg_debt_mf.amount),
            "ltcg_112a_equity_stt": float(capital_gains.ltcg_112a_equity_stt.amount),
            "ltcg_other_assets": float(capital_gains.ltcg_other_assets.amount),
            "ltcg_debt_mf": float(capital_gains.ltcg_debt_mf.amount)
        }
    
    def _serialize_retirement_benefits(self, retirement_benefits: RetirementBenefits) -> Dict[str, Any]:
        """Serialize retirement benefits to dict."""
        if not retirement_benefits:
            return {}
        
        result = {}
        
        # Serialize leave encashment
        if retirement_benefits.leave_encashment:
            le = retirement_benefits.leave_encashment
            result["leave_encashment"] = {
                "leave_encashment_amount": float(le.leave_encashment_amount.amount),
                "average_monthly_salary": float(le.average_monthly_salary.amount),
                "leave_days_encashed": le.leave_days_encashed,
                "is_govt_employee": le.is_govt_employee,
                "is_deceased": le.is_deceased,
                "during_employment": le.during_employment
            }
        
        # Serialize gratuity
        if retirement_benefits.gratuity:
            gr = retirement_benefits.gratuity
            result["gratuity"] = {
                "gratuity_amount": float(gr.gratuity_amount.amount),
                "monthly_salary": float(gr.monthly_salary.amount),
                "service_years": float(gr.service_years),
                "is_govt_employee": gr.is_govt_employee
            }
        
        # Serialize VRS
        if retirement_benefits.vrs:
            vrs = retirement_benefits.vrs
            result["vrs"] = {
                "vrs_amount": float(vrs.vrs_amount.amount),
                "monthly_salary": float(vrs.monthly_salary.amount),
                "age": vrs.age,
                "service_years": float(vrs.service_years)
            }
        
        # Serialize pension
        if retirement_benefits.pension:
            pen = retirement_benefits.pension
            result["pension"] = {
                "regular_pension": float(pen.regular_pension.amount),
                "commuted_pension": float(pen.commuted_pension.amount),
                "total_pension": float(pen.total_pension.amount),
                "is_govt_employee": pen.is_govt_employee,
                "gratuity_received": pen.gratuity_received
            }
        
        # Serialize retrenchment compensation
        if retirement_benefits.retrenchment_compensation:
            rc = retirement_benefits.retrenchment_compensation
            result["retrenchment_compensation"] = {
                "retrenchment_amount": float(rc.retrenchment_amount.amount),
                "monthly_salary": float(rc.monthly_salary.amount),
                "service_years": float(rc.service_years)
            }
        
        return result
    
    def _serialize_other_income(self, other_income: OtherIncome) -> Dict[str, Any]:
        """Serialize other income to dict."""
        if not other_income:
            return {}
        
        result = {
            "dividend_income": float(other_income.dividend_income.amount),
            "gifts_received": float(other_income.gifts_received.amount),
            "business_professional_income": float(other_income.business_professional_income.amount),
            "other_miscellaneous_income": float(other_income.other_miscellaneous_income.amount)
        }
        
        # Serialize interest income
        if other_income.interest_income:
            interest = other_income.interest_income
            result["interest_income"] = {
                "savings_interest": float(interest.savings_account_interest.amount),
                "fd_interest": float(interest.fixed_deposit_interest.amount),
                "rd_interest": float(interest.recurring_deposit_interest.amount),
                "post_office_interest": float(interest.post_office_interest.amount)
            }
        
        # Serialize house property income
        if other_income.house_property_income:
            result["house_property_income"] = self._serialize_house_property_income(other_income.house_property_income)
        
        # Serialize capital gains income
        if other_income.capital_gains_income:
            result["capital_gains_income"] = self._serialize_capital_gains_income(other_income.capital_gains_income)
        
        return result

    async def compute_monthly_tax(self, employee_id: str, organization_id: str) -> Dict[str, Any]:
        """
        Compute monthly tax for an employee based on their salary package record.
        
        Args:
            employee_id: Employee ID as string
            organization_id: Organization ID for database segregation
            
        Returns:
            Dict[str, Any]: Monthly tax computation result with details
            
        Raises:
            ValueError: If employee or salary data not found
            RuntimeError: If computation fails
        """
        logger.debug(f"UnifiedTaxationController.compute_monthly_tax: Starting for employee {employee_id}, organization {organization_id}")
        
        try:
            
            # Check if enhanced_tax_service is available
            if not self.enhanced_tax_service:
                logger.error("UnifiedTaxationController.compute_monthly_tax: Enhanced tax service not configured")
                raise RuntimeError("Enhanced tax service not configured")
            
            # Use the enhanced tax service to compute monthly tax with details
            result = await self.enhanced_tax_service.compute_monthly_tax_with_details(
                employee_id, organization_id
            )
            
            logger.debug(f"UnifiedTaxationController.compute_monthly_tax: Successfully received result from enhanced tax service")
            logger.debug(f"UnifiedTaxationController.compute_monthly_tax: Result keys: {list(result.keys())}")
            logger.debug(f"UnifiedTaxationController.compute_monthly_tax: Monthly tax liability: {result.get('monthly_tax_liability', 'Not found')}")
            
            return result
            
        except ValueError as e:
            logger.error(f"UnifiedTaxationController.compute_monthly_tax: Validation error for employee {employee_id}: {str(e)}")
            # Re-raise validation errors
            raise e
        except Exception as e:
            logger.error(f"UnifiedTaxationController.compute_monthly_tax: Unexpected error for employee {employee_id}: {str(e)}", exc_info=True)
            # Wrap other errors
            raise RuntimeError(f"Failed to compute monthly tax for employee {employee_id}: {str(e)}")
 