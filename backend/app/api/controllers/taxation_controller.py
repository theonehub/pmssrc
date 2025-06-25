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
    CreateTaxationRecordRequest,
    CreateTaxationRecordResponse,
    UpdateSalaryIncomeRequest,
    UpdateDeductionsRequest,
    ChangeRegimeRequest,
    CalculateTaxRequest,
    CalculateTaxResponse,
    TaxationRecordSummaryDTO,
    TaxationRecordListResponse,
    UpdateResponse,
    TaxationRecordQuery,
    DetailedTaxBreakdownResponse,
    RegimeComparisonResponse,
    
    # Comprehensive DTOs
    ComprehensiveTaxInputDTO,
    ComprehensiveTaxOutputDTO,
    PerquisitesDTO,
    HousePropertyIncomeDTO,
    MultipleHousePropertiesDTO,
    CapitalGainsIncomeDTO,
    RetirementBenefitsDTO,
    OtherIncomeDTO,
    AnnualPayrollWithLWPDTO,
    
    # Enhanced calculation DTOs
    EnhancedTaxCalculationRequestDTO,
    MidYearJoinerDTO,
    MidYearIncrementDTO,
    ScenarioComparisonRequestDTO,
    
    # Response DTOs
    PeriodicTaxCalculationResponseDTO,
    ScenarioComparisonResponseDTO,
    TaxOptimizationSuggestionDTO,
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
    GetComponentRequest,
    ComponentResponse,
    TaxationRecordStatusResponse,
)

# Import command handlers
from app.application.commands.taxation_commands import (
    CreateTaxationRecordCommand,
    CreateTaxationRecordCommandHandler,
    UpdateSalaryIncomeCommand,
    UpdateSalaryIncomeCommandHandler,
    UpdateDeductionsCommand,
    UpdateDeductionsCommandHandler,
    ChangeRegimeCommand,
    ChangeRegimeCommandHandler,
    CalculateTaxCommand,
    CalculateTaxCommandHandler,
    FinalizeRecordCommand,
    FinalizeRecordCommandHandler,
    ReopenRecordCommand,
    ReopenRecordCommandHandler,
    DeleteTaxationRecordCommand,
    DeleteTaxationRecordCommandHandler
)

# Import domain entities and value objects
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.entities.taxation.taxation_record import TaxationRecord
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.periodic_salary_income import PeriodicSalaryIncome, PeriodicSalaryData
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
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome, CapitalGainsType
from app.domain.entities.taxation.retirement_benefits import (
    RetirementBenefits, LeaveEncashment, Gratuity, VRS, Pension, RetrenchmentCompensation
)
from app.domain.entities.taxation.other_income import OtherIncome, InterestIncome
from app.domain.entities.taxation.monthly_payroll import MonthlyPayroll, AnnualPayrollWithLWP, LWPDetails
from app.domain.entities.taxation.taxation_record import SalaryPackageRecord

# Import services
from app.domain.services.taxation.tax_calculation_service import (
    TaxCalculationService, TaxCalculationInput, TaxCalculationResult
)

# Import use cases
from app.application.use_cases.taxation.get_employees_for_selection_use_case import GetEmployeesForSelectionUseCase
from app.application.use_cases.taxation.get_taxation_record_by_employee_use_case import GetTaxationRecordByEmployeeUseCase
from app.application.use_cases.taxation.get_comprehensive_taxation_record_use_case import GetComprehensiveTaxationRecordUseCase

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
                 # Command handlers for basic operations
                 create_handler: CreateTaxationRecordCommandHandler,
                 update_salary_handler: UpdateSalaryIncomeCommandHandler,
                 update_deductions_handler: UpdateDeductionsCommandHandler,
                 change_regime_handler: ChangeRegimeCommandHandler,
                 calculate_tax_handler: CalculateTaxCommandHandler,
                 finalize_handler: FinalizeRecordCommandHandler,
                 reopen_handler: ReopenRecordCommandHandler,
                 delete_handler: DeleteTaxationRecordCommandHandler,
                 
                 # Services for comprehensive calculations
                 enhanced_tax_service: TaxCalculationService,
                 
                 # Repository for direct database access
                 taxation_repository,
                 user_repository,
                 salary_package_repository,
                 
                 # Use cases
                 get_employees_for_selection_use_case: GetEmployeesForSelectionUseCase,
                 get_taxation_record_by_employee_use_case: GetTaxationRecordByEmployeeUseCase,
                 get_comprehensive_taxation_record_use_case: GetComprehensiveTaxationRecordUseCase):
        
        # Basic operation handlers
        self.create_handler = create_handler
        self.update_salary_handler = update_salary_handler
        self.update_deductions_handler = update_deductions_handler
        self.change_regime_handler = change_regime_handler
        self.calculate_tax_handler = calculate_tax_handler
        self.finalize_handler = finalize_handler
        self.reopen_handler = reopen_handler
        self.delete_handler = delete_handler
        
        # Enhanced calculation services
        self.enhanced_tax_service = enhanced_tax_service
        
        # Repository for direct database access
        self.taxation_repository = taxation_repository
        self.user_repository = user_repository
        self.salary_package_repository = salary_package_repository
        
        # Use cases
        self.get_employees_for_selection_use_case = get_employees_for_selection_use_case
        self.get_taxation_record_by_employee_use_case = get_taxation_record_by_employee_use_case
        self.get_comprehensive_taxation_record_use_case = get_comprehensive_taxation_record_use_case
    
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
    # BASIC TAXATION RECORD OPERATIONS
    # =============================================================================
    
    async def create_taxation_record(self,
                                   request: CreateTaxationRecordRequest,
                                   organization_id: str) -> CreateTaxationRecordResponse:
        """Create new taxation record with comprehensive income support."""
        
        logger.info(f"Creating taxation record for user {request.employee_id}, year {request.tax_year}")
        
        # Convert core DTO to domain entities
        # Handle case when salary_income is null - create default with zero values
        if request.salary_income:
            salary_income = self._convert_salary_dto_to_entity(request.salary_income)
        else:
            # Create default salary income with zero values
            salary_income = SalaryIncome(
                basic_salary=Money.zero(),
                dearness_allowance=Money.zero(),
                hra_provided=Money.zero(),
                special_allowance=Money.zero(),
            )
        
        deductions = self._convert_deductions_dto_to_entity(request.deductions)
        
        # Convert comprehensive income components
        perquisites = self._convert_perquisites_dto_to_entity(request.perquisites) if request.perquisites else None
        house_property_income = self._convert_house_property_dto_to_entity(request.house_property_income) if request.house_property_income else None
        capital_gains_income = self._convert_capital_gains_dto_to_entity(request.capital_gains_income) if request.capital_gains_income else None
        retirement_benefits = self._convert_retirement_benefits_dto_to_entity(request.retirement_benefits) if request.retirement_benefits else None
        other_income = self._convert_other_income_dto_to_entity(request.other_income) if request.other_income else None
        monthly_payroll = self._convert_monthly_payroll_dto_to_entity(request.monthly_payroll) if request.monthly_payroll else None
        
        # Handle enhanced deductions if provided
        if request.comprehensive_deductions:
            deductions = self._convert_comprehensive_deductions_dto_to_entity(request.comprehensive_deductions)
        
        # Create command with comprehensive income support
        logger.info("🔍 Creating CreateTaxationRecordCommand...")
        logger.info(f"🔍 salary_income type: {type(salary_income)}")
        logger.info(f"🔍 salary_income basic_salary: {salary_income.basic_salary}")
        logger.info(f"🔍 salary_income hra_provided: {salary_income.hra_provided}")
        
        try:
            command = CreateTaxationRecordCommand(
                employee_id=request.employee_id,
                organization_id=organization_id,
                tax_year=request.tax_year,
                regime=request.regime,
                age=request.age,
                salary_income=salary_income,
                deductions=deductions,
                perquisites=perquisites,
                house_property_income=house_property_income,
                capital_gains_income=capital_gains_income,
                retirement_benefits=retirement_benefits,
                other_income=other_income,
                monthly_payroll=monthly_payroll
            )
            logger.info("✅ CreateTaxationRecordCommand created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create CreateTaxationRecordCommand: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            raise
        
        # Execute command
        logger.info("🔍 Executing command handler...")
        try:
            response = await self.create_handler.handle(command, organization_id)
            logger.info("✅ Command handler executed successfully")
        except Exception as e:
            logger.error(f"❌ Command handler failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            raise
        
        logger.info(f"Created taxation record with comprehensive income: {response.taxation_id}")
        return response
    
    async def list_taxation_records(self,
                                  query: TaxationRecordQuery,
                                  organization_id: str) -> TaxationRecordListResponse:
        """List taxation records with filtering and pagination."""
        
        # Calculate offset
        offset = (query.page - 1) * query.page_size
        
        # Mock response for now
        return TaxationRecordListResponse(
            records=[],
            total_count=0,
            page=query.page,
            page_size=query.page_size
        )

    async def get_taxation_record_by_employee(self,
                                employee_id: str,
                                organization_id: str,
                                tax_year: Optional[str] = None) -> ComprehensiveTaxOutputDTO:
        """Get comprehensive taxation record by employee ID and optional tax year."""
        
        logger.info(f"Getting comprehensive taxation record for employee {employee_id}, tax_year: {tax_year}")
        
        try:
            # Execute the use case to get the comprehensive taxation record
            response = await self.get_comprehensive_taxation_record_use_case.execute(
                employee_id, organization_id, tax_year
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting comprehensive taxation record for employee {employee_id}: {str(e)}")
            raise

    async def get_taxation_record(self,
                                taxation_id: str,
                                organization_id: str) -> TaxationRecordSummaryDTO:
        """Get taxation record by ID."""
        
        # This would use a query handler
        raise NotImplementedError("Query implementation needed")
    
    async def get_detailed_breakdown(self,
                                   taxation_id: str,
                                   organization_id: str) -> DetailedTaxBreakdownResponse:
        """Get detailed tax breakdown."""
        
        # This would use a query handler
        raise NotImplementedError("Query implementation needed")
    
    async def update_salary_income(self,
                                 taxation_id: str,
                                 request: UpdateSalaryIncomeRequest,
                                 organization_id: str) -> UpdateResponse:
        """Update salary income."""
        
        logger.info(f"Updating salary income for taxation record {taxation_id}")
        
        # Convert DTO to domain entity
        salary_income = self._convert_salary_dto_to_entity(request.salary_income)
        
        # Create command
        command = UpdateSalaryIncomeCommand(
            taxation_id=taxation_id,
            organization_id=organization_id,
            salary_income=salary_income
        )
        
        # Execute command
        await self.update_salary_handler.handle(command)
        
        return UpdateResponse(
            taxation_id=taxation_id,
            status="success",
            message="Salary income updated successfully",
            updated_at=datetime.utcnow()
        )
    
    async def update_deductions(self,
                              taxation_id: str,
                              request: UpdateDeductionsRequest,
                              organization_id: str) -> UpdateResponse:
        """Update tax deductions."""
        
        logger.info(f"Updating deductions for taxation record {taxation_id}")
        
        # Convert DTO to domain entity
        deductions = self._convert_deductions_dto_to_entity(request.deductions)
        
        # Create command
        command = UpdateDeductionsCommand(
            taxation_id=taxation_id,
            organization_id=organization_id,
            deductions=deductions
        )
        
        # Execute command
        await self.update_deductions_handler.handle(command)
        
        return UpdateResponse(
            taxation_id=taxation_id,
            status="success",
            message="Tax deductions updated successfully",
            updated_at=datetime.utcnow()
        )
    
    async def change_regime(self,
                          taxation_id: str,
                          request: ChangeRegimeRequest,
                          organization_id: str) -> UpdateResponse:
        """Change tax regime."""
        
        logger.info(f"Changing regime to {request.new_regime} for taxation record {taxation_id}")
        
        # Create command
        command = ChangeRegimeCommand(
            taxation_id=taxation_id,
            organization_id=organization_id,
            new_regime=request.new_regime
        )
        
        # Execute command
        await self.change_regime_handler.handle(command)
        
        return UpdateResponse(
            taxation_id=taxation_id,
            status="success",
            message=f"Tax regime changed to {request.new_regime}",
            updated_at=datetime.utcnow()
        )
    
    async def calculate_tax(self,
                          taxation_id: str,
                          request: CalculateTaxRequest,
                          organization_id: str) -> CalculateTaxResponse:
        """Calculate tax."""
        
        logger.info(f"Calculating tax for taxation record {taxation_id}")
        
        # Create command
        command = CalculateTaxCommand(
            taxation_id=taxation_id,
            organization_id=organization_id,
            force_recalculate=request.force_recalculate
        )
        
        # Execute command
        response = await self.calculate_tax_handler.handle(command)
        
        # Convert to DTO response
        return CalculateTaxResponse(
            taxation_id=response.taxation_id,
            employee_id=response.employee_id,
            tax_year=response.tax_year,
            regime=response.regime,
            calculation_breakdown={
                "regime_type": response.regime,
                "total_tax_liability": response.total_tax_liability,
                "effective_tax_rate": response.effective_tax_rate,
                "monthly_tax_liability": response.monthly_tax_liability,
                "detailed_breakdown": response.calculation_breakdown
            },
            calculated_at=response.calculated_at
        )
    
    async def compare_regimes(self,
                            taxation_id: str,
                            organization_id: str) -> RegimeComparisonResponse:
        """Compare tax regimes."""
        
        logger.info(f"Comparing regimes for taxation record {taxation_id}")
        
        # This would use the regime comparison service
        raise NotImplementedError("Regime comparison implementation needed")
    
    async def finalize_record(self,
                            taxation_id: str,
                            organization_id: str) -> UpdateResponse:
        """Finalize taxation record."""
        
        logger.info(f"Finalizing taxation record {taxation_id}")
        
        # Create command
        command = FinalizeRecordCommand(
            taxation_id=taxation_id,
            organization_id=organization_id
        )
        
        # Execute command
        await self.finalize_handler.handle(command)
        
        return UpdateResponse(
            taxation_id=taxation_id,
            status="success",
            message="Taxation record finalized successfully",
            updated_at=datetime.utcnow()
        )
    
    async def reopen_record(self,
                          taxation_id: str,
                          organization_id: str) -> UpdateResponse:
        """Reopen finalized taxation record."""
        
        logger.info(f"Reopening taxation record {taxation_id}")
        
        # Create command
        command = ReopenRecordCommand(
            taxation_id=taxation_id,
            organization_id=organization_id
        )
        
        # Execute command
        await self.reopen_handler.handle(command)
        
        return UpdateResponse(
            taxation_id=taxation_id,
            status="success",
            message="Taxation record reopened successfully",
            updated_at=datetime.utcnow()
        )
    
    async def delete_record(self,
                          taxation_id: str,
                          organization_id: str) -> None:
        """Delete taxation record."""
        
        logger.info(f"Deleting taxation record {taxation_id}")
        
        # Create command
        command = DeleteTaxationRecordCommand(
            taxation_id=taxation_id,
            organization_id=organization_id
        )
        
        # Execute command
        await self.delete_handler.handle(command)
        
        logger.info(f"Deleted taxation record {taxation_id}")
    
    # =============================================================================
    # COMPREHENSIVE TAX CALCULATION OPERATIONS
    # =============================================================================
    
    async def calculate_comprehensive_tax(self,
                                        request: ComprehensiveTaxInputDTO,
                                        organization_id: str) -> TaxCalculationResult:
        """
        Calculate comprehensive tax including all income sources.
        
        This method performs generic tax calculation without database operations.
        For employee-specific calculations with database operations, use 
        calculate_comprehensive_tax_for_employee() instead.
        
        Args:
            request: Comprehensive tax input DTO
            organization_id: Organization ID for multi-tenancy
            
        Returns:
            TaxCalculationResult: Complete tax calculation result
        """
        try:
            logger.info(f"Starting comprehensive tax calculation for year {request.tax_year}")
            
            # Convert DTO to domain input for calculation
            domain_input = self._convert_dto_to_domain_input(request)
            
            # Calculate tax using the enhanced tax service (without database operations)
            logger.info(f"Calculating tax for regime {request.regime_type}")
            calculation_result = await self.enhanced_tax_service.calculate_and_update_taxation_record(
                domain_input, organization_id
            )
            
            logger.info(f"Comprehensive tax calculation completed")
            return calculation_result
            
        except Exception as e:
            logger.error(f"Error in comprehensive tax calculation: {str(e)}")
            raise
    
    async def calculate_enhanced_tax(self,
                                   request: EnhancedTaxCalculationRequestDTO,
                                   organization_id: str) -> PeriodicTaxCalculationResponseDTO:
        """Calculate enhanced tax with periodic salary and analytics."""
        try:
            logger.info(f"Starting enhanced tax calculation for org {organization_id}")
            
            # Validate request
            self._validate_enhanced_request(request)
            
            # Convert to comprehensive format
            comprehensive_request = self._convert_enhanced_to_comprehensive(request)
            
            # Calculate using comprehensive method
            result = await self.calculate_comprehensive_tax(comprehensive_request, organization_id)
            
            # Add enhanced-specific features
            enhanced_result = self._add_enhanced_features(result, comprehensive_request)
            
            logger.info(f"Enhanced tax calculation completed for org {organization_id}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in enhanced tax calculation for org {organization_id}: {str(e)}")
            raise
    
    async def calculate_mid_year_joiner_tax(self,
                                          request: MidYearJoinerDTO,
                                          tax_year: str,
                                          regime_type: str,
                                          age: int,
                                          deductions: Dict[str, float],
                                          organization_id: str) -> PeriodicTaxCalculationResponseDTO:
        """Calculate tax for mid-year joiner scenario."""
        try:
            logger.info(f"Calculating mid-year joiner tax for org {organization_id}")
            
            # Validate request
            self._validate_mid_year_joiner_request(request, tax_year, regime_type, age)
            
            # Convert to comprehensive format
            comprehensive_request = self._create_mid_year_joiner_comprehensive_request(
                request, tax_year, regime_type, age, deductions
            )
            
            # Calculate tax
            result = await self.calculate_comprehensive_tax(comprehensive_request, organization_id)
            
            # Add mid-year specific enhancements
            enhanced_result = self._add_mid_year_enhancements(result, request, "joiner")
            
            logger.info(f"Mid-year joiner tax calculation completed for org {organization_id}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in mid-year joiner calculation for org {organization_id}: {str(e)}")
            raise
    
    async def calculate_mid_year_increment_tax(self,
                                             request: MidYearIncrementDTO,
                                             tax_year: str,
                                             regime_type: str,
                                             age: int,
                                             deductions: Dict[str, float],
                                             organization_id: str) -> PeriodicTaxCalculationResponseDTO:
        """Calculate tax for mid-year increment scenario."""
        try:
            logger.info(f"Calculating mid-year increment tax for org {organization_id}")
            
            # Validate request
            self._validate_mid_year_increment_request(request, tax_year, regime_type, age)
            
            # Convert to periodic salary income format
            periodic_salary = self._create_periodic_salary_from_mid_year_increment(
                request, tax_year
            )
            
            # Create comprehensive tax input
            comprehensive_request = self._create_comprehensive_from_periodic_salary(
                periodic_salary, regime_type, age, deductions, tax_year
            )
            
            # Calculate tax
            result = await self.calculate_comprehensive_tax(comprehensive_request, organization_id)
            
            # Add mid-year specific enhancements
            enhanced_result = self._add_mid_year_enhancements(result, request, "increment")
            
            logger.info(f"Mid-year increment tax calculation completed for org {organization_id}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in mid-year increment calculation for org {organization_id}: {str(e)}")
            raise
    
    async def compare_scenarios(self,
                              request: ScenarioComparisonRequestDTO,
                              organization_id: str) -> ScenarioComparisonResponseDTO:
        """Compare multiple tax scenarios."""
        try:
            logger.info(f"Starting scenario comparison for org {organization_id}")
            
            # Validate request
            self._validate_scenario_comparison_request(request)
            
            # Calculate base scenario
            base_result = await self.calculate_enhanced_tax(request.base_request, organization_id)
            
            # Calculate comparison scenarios
            comparisons = await self._calculate_comparison_scenarios(request, organization_id)
            
            # Build response
            response = self._build_scenario_comparison_response(base_result, comparisons, request)
            
            logger.info(f"Scenario comparison completed for org {organization_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in scenario comparison for org {organization_id}: {str(e)}")
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
    
    async def calculate_house_property_only(self,
                                          house_property: HousePropertyIncomeDTO,
                                          regime_type: str,
                                          organization_id: str) -> Dict[str, Any]:
        """Calculate only house property income."""
        try:
            # Convert DTO to entity
            house_property_entity = self._convert_house_property_dto_to_entity(house_property)
            regime = TaxRegime(TaxRegimeType.OLD if regime_type.lower() == "old" else TaxRegimeType.NEW)
            
            # Calculate house property income
            net_income = house_property_entity.calculate_net_income_from_house_property(regime)
            breakdown = house_property_entity.get_house_property_breakdown(regime)
            
            return {
                "net_house_property_income": net_income.to_float(),
                "house_property_breakdown": breakdown,
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
    
    async def calculate_payroll_tax(self,
                                  payroll: AnnualPayrollWithLWPDTO,
                                  deductions_data: Dict[str, float],
                                  regime_type: str,
                                  age: int,
                                  organization_id: str) -> Dict[str, Any]:
        """Calculate payroll tax with LWP considerations."""
        try:
            # Convert DTO to entity
            payroll_entity = self._convert_payroll_dto_to_entity(payroll)
            regime = TaxRegime(TaxRegimeType.OLD if regime_type.lower() == "old" else TaxRegimeType.NEW)
            
            # Calculate payroll tax
            result = self.enhanced_tax_service.calculate_annual_payroll_tax(
                payroll_entity, regime, age, deductions_data
            )
            
            return {
                "annual_payroll_result": result.to_dict(),
                "monthly_breakdown": [month.to_dict() for month in result.monthly_results],
                "lwp_impact_summary": result.get_lwp_impact_summary(),
                "regime_used": regime_type
            }
            
        except Exception as e:
            logger.error(f"Error calculating payroll tax for org {organization_id}: {str(e)}")
            raise
    
    # =============================================================================
    # DTO TO DOMAIN ENTITY CONVERSION METHODS
    # =============================================================================
    
    def _convert_dto_to_domain_input(self, request: ComprehensiveTaxInputDTO):
        """Convert ComprehensiveTaxInputDTO to TaxCalculationInput for domain service."""
        from app.domain.services.taxation.tax_calculation_service import TaxCalculationInput
        from app.domain.value_objects.taxation.tax_regime import TaxRegime, TaxRegimeType
        
        # Convert regime
        regime_type = TaxRegimeType.OLD if request.regime_type.lower() == "old" else TaxRegimeType.NEW
        regime = TaxRegime(regime_type)
        
        # Convert salary income
        salary_income = self._convert_salary_dto_to_entity(request.salary_income) if request.salary_income else self._create_default_salary_income()
        
        # Convert other components
        perquisites = self._convert_perquisites_dto_to_entity(request.perquisites) if request.perquisites else self._create_default_perquisites()
        house_property_income = self._convert_house_property_dto_to_entity(request.house_property_income) if request.house_property_income else self._create_default_house_property()
        capital_gains_income = self._convert_capital_gains_dto_to_entity(request.capital_gains_income) if request.capital_gains_income else self._create_default_capital_gains()
        retirement_benefits = self._convert_retirement_benefits_dto_to_entity(request.retirement_benefits) if request.retirement_benefits else self._create_default_retirement_benefits()
        other_income = self._convert_other_income_dto_to_entity(request.other_income) if request.other_income else self._create_default_other_income()
        deductions = self._convert_deductions_dto_to_entity(request.deductions) if request.deductions else self._create_default_deductions()
        
        # Determine citizen status
        is_senior_citizen = request.age >= 60
        is_super_senior_citizen = request.age >= 80
        
        return TaxCalculationInput(
            salary_income=salary_income,
            perquisites=perquisites,
            house_property_income=house_property_income,
            capital_gains_income=capital_gains_income,
            retirement_benefits=retirement_benefits,
            other_income=other_income,
            deductions=deductions,
            regime=regime,
            age=request.age,
            is_senior_citizen=is_senior_citizen,
            is_super_senior_citizen=is_super_senior_citizen,
            is_government_employee=getattr(request, 'is_govt_employee', False)
        )
    
    def _convert_result_to_dto(self, result, request: ComprehensiveTaxInputDTO) -> PeriodicTaxCalculationResponseDTO:
        """Convert TaxCalculationResult to PeriodicTaxCalculationResponseDTO."""
        from app.application.dto.taxation_dto import PeriodicTaxCalculationResponseDTO
        from datetime import datetime
        
        # Calculate additional fields
        effective_tax_rate = 0.0
        if result.total_income.to_float() > 0:
            effective_tax_rate = (result.tax_liability.to_float() / result.total_income.to_float()) * 100
        
        # Calculate surcharge and cess (simplified calculation)
        tax_before_surcharge = result.tax_liability.to_float()
        surcharge = 0.0
        cess = tax_before_surcharge * 0.04  # 4% health and education cess
        
        # Build response
        return PeriodicTaxCalculationResponseDTO(
            total_tax_liability=result.tax_liability.to_float(),
            taxable_income=result.taxable_income.to_float(),
            effective_tax_rate=effective_tax_rate,
            regime_used=request.regime_type,
            gross_income=result.total_income.to_float(),
            total_exemptions=result.total_exemptions.to_float(),
            total_deductions=result.total_deductions.to_float(),
            tax_before_rebate=tax_before_surcharge,
            rebate_87a=0.0,  # Calculate if applicable
            tax_after_rebate=tax_before_surcharge,
            surcharge=surcharge,
            cess=cess,
            
            # Enhanced details
            employment_periods=[],  # Not applicable for simple calculation
            total_employment_days=365,  # Full year assumption
            is_mid_year_scenario=False,
            period_wise_income={},
            surcharge_breakdown={},
            full_year_projection={},
            mid_year_impact={},
            optimization_suggestions=[],
            taxpayer_age=request.age,
            calculation_breakdown=result.tax_breakdown,
            
            # Metadata
            calculated_at=datetime.utcnow(),
            calculation_version="1.0"
        )
    
    def _create_default_salary_income(self):
        """Create default salary income entity."""
        from app.domain.entities.taxation.salary_income import SalaryIncome, SpecificAllowances
        from app.domain.value_objects.money import Money
        
        return SalaryIncome(
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
    
    def _create_default_house_property(self):
        """Create default house property entity."""
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
        from app.domain.entities.taxation.other_income import OtherIncome
        from app.domain.value_objects.money import Money
        
        return OtherIncome(
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
        
        return SalaryIncome(
            basic_salary=Money.from_decimal(salary_dto.basic_salary),
            dearness_allowance=Money.from_decimal(salary_dto.dearness_allowance),
            hra_provided=Money.from_decimal(salary_dto.hra_provided),
            special_allowance=Money.from_decimal(salary_dto.special_allowance),
            # Optional components with defaults
            bonus=Money.from_decimal(getattr(salary_dto, 'bonus', 0)),
            commission=Money.from_decimal(getattr(salary_dto, 'commission', 0)),
        )
    
    def _convert_periodic_salary_dto_to_entity(self, periodic_dto) -> PeriodicSalaryIncome:
        """Convert periodic salary DTO to entity."""
        periods = []
        for period_dto in periodic_dto.periods:
            period_data = PeriodicSalaryData(
                start_date=period_dto.period.start_date,
                end_date=period_dto.period.end_date,
                description=period_dto.period.description,
                basic_salary=float(period_dto.basic_salary),
                dearness_allowance=float(period_dto.dearness_allowance),
                hra_provided=float(period_dto.hra_provided),
                special_allowance=float(period_dto.special_allowance),
                bonus=float(period_dto.bonus),
                commission=float(period_dto.commission),
            )
            periods.append(period_data)
        
        return PeriodicSalaryIncome(periods=periods)
    
    def _convert_deductions_dto_to_entity(self, deductions_dto) -> TaxDeductions:
        """Convert deductions DTO to domain entity."""
        
        # Initialize with default values
        deductions = TaxDeductions()
        
        if not deductions_dto:
            return deductions
        
        # Map Section 80C fields using the new nested structure
        if deductions_dto.section_80c:
            sec_80c_dto = deductions_dto.section_80c
            deductions.section_80c.life_insurance_premium = Money.from_decimal(sec_80c_dto.life_insurance_premium)
            deductions.section_80c.epf_contribution = Money.from_decimal(sec_80c_dto.epf_contribution)
            deductions.section_80c.ppf_contribution = Money.from_decimal(sec_80c_dto.ppf_contribution)
            deductions.section_80c.nsc_investment = Money.from_decimal(sec_80c_dto.nsc_investment)
            deductions.section_80c.tax_saving_fd = Money.from_decimal(sec_80c_dto.tax_saving_fd)
            deductions.section_80c.elss_investment = Money.from_decimal(sec_80c_dto.elss_investment)
            deductions.section_80c.home_loan_principal = Money.from_decimal(sec_80c_dto.home_loan_principal)
            deductions.section_80c.tuition_fees = Money.from_decimal(sec_80c_dto.tuition_fees)
            deductions.section_80c.sukanya_samriddhi = Money.from_decimal(sec_80c_dto.sukanya_samriddhi)
            deductions.section_80c.other_80c_investments = Money.from_decimal(sec_80c_dto.other_80c_investments)
        
        # Map Section 80D fields using the new nested structure
        if deductions_dto.section_80d:
            sec_80d_dto = deductions_dto.section_80d
            deductions.section_80d.self_family_premium = Money.from_decimal(sec_80d_dto.self_family_premium)
            deductions.section_80d.parent_premium = Money.from_decimal(sec_80d_dto.parent_premium)
            deductions.section_80d.preventive_health_checkup = Money.from_decimal(sec_80d_dto.preventive_health_checkup)
            deductions.section_80d.parent_age = sec_80d_dto.parent_age if hasattr(sec_80d_dto, 'parent_age') else 55
        
        # Map HRA Exemption fields using the new nested structure
        if deductions_dto.hra_exemption:
            hra_dto = deductions_dto.hra_exemption
            from app.domain.entities.taxation.deductions import HRAExemption
            deductions.hra_exemption = HRAExemption(
                actual_rent_paid=Money.from_decimal(hra_dto.actual_rent_paid),
                hra_city_type=hra_dto.hra_city_type
            )
        
        # Map Other Deductions fields using the new nested structure
        if deductions_dto.other_deductions:
            other_dto = deductions_dto.other_deductions
            deductions.other_deductions.education_loan_interest = Money.from_decimal(other_dto.education_loan_interest)
            deductions.other_deductions.charitable_donations = Money.from_decimal(other_dto.charitable_donations)
            deductions.other_deductions.savings_interest = Money.from_decimal(other_dto.savings_interest)
            deductions.other_deductions.nps_contribution = Money.from_decimal(other_dto.nps_contribution)
            deductions.other_deductions.other_deductions = Money.from_decimal(other_dto.other_deductions)
        
        return deductions
    
    def _convert_comprehensive_deductions_dto_to_entity(self, comp_deductions_dto) -> TaxDeductions:
        """Convert comprehensive deductions DTO to entity."""
        # This method would handle the comprehensive deductions conversion
        # For now, we'll use the existing deductions conversion logic
        return self._convert_deductions_dto_to_entity(comp_deductions_dto)
    
    def _convert_perquisites_dto_to_entity(self, perquisites_dto) -> Perquisites:
        """Convert perquisites DTO to entity."""
        # Convert accommodation
        accommodation = None
        if perquisites_dto.accommodation:
            acc_dto = perquisites_dto.accommodation
            accommodation = AccommodationPerquisite(
                accommodation_type=AccommodationType(acc_dto.accommodation_type),
                city_population=CityPopulation(acc_dto.city_population),
                license_fees=Money.from_decimal(acc_dto.license_fees),
                employee_rent_payment=Money.from_decimal(acc_dto.employee_rent_payment),
                basic_salary=Money.from_decimal(acc_dto.basic_salary),
                dearness_allowance=Money.from_decimal(acc_dto.dearness_allowance),
                rent_paid_by_employer=Money.from_decimal(acc_dto.rent_paid_by_employer),
                hotel_charges=Money.from_decimal(acc_dto.hotel_charges),
                stay_days=acc_dto.stay_days,
                furniture_cost=Money.from_decimal(acc_dto.furniture_cost),
                furniture_employee_payment=Money.from_decimal(acc_dto.furniture_employee_payment),
                is_furniture_owned_by_employer=acc_dto.is_furniture_owned_by_employer
            )
        
        # Convert car
        car = None
        if perquisites_dto.car:
            car_dto = perquisites_dto.car
            car = CarPerquisite(
                car_use_type=CarUseType(car_dto.car_use_type),
                engine_capacity_cc=car_dto.engine_capacity_cc,
                months_used=car_dto.months_used,
                car_cost_to_employer=Money.from_decimal(car_dto.car_cost_to_employer),
                other_vehicle_cost=Money.from_decimal(car_dto.other_vehicle_cost),
                has_expense_reimbursement=car_dto.has_expense_reimbursement,
                driver_provided=car_dto.driver_provided
            )
        
        # Convert medical reimbursement
        medical_reimbursement = None
        if perquisites_dto.medical_reimbursement:
            med_dto = perquisites_dto.medical_reimbursement
            medical_reimbursement = MedicalReimbursement(
                medical_reimbursement_amount=Money.from_decimal(med_dto.medical_reimbursement_amount),
                is_overseas_treatment=med_dto.is_overseas_treatment
            )
        
        # Convert LTA
        lta = None
        if perquisites_dto.lta:
            lta_dto = perquisites_dto.lta
            lta = LTAPerquisite(
                lta_amount_claimed=Money.from_decimal(lta_dto.lta_amount_claimed),
                lta_claimed_count=lta_dto.lta_claimed_count,
                public_transport_cost=Money.from_decimal(lta_dto.public_transport_cost)
            )
        
        # Convert interest free loan
        interest_free_loan = None
        if perquisites_dto.interest_free_loan:
            loan_dto = perquisites_dto.interest_free_loan
            interest_free_loan = InterestFreeConcessionalLoan(
                loan_amount=Money.from_decimal(loan_dto.loan_amount),
                outstanding_amount=Money.from_decimal(loan_dto.outstanding_amount),
                company_interest_rate=Decimal(str(loan_dto.company_interest_rate)),
                sbi_interest_rate=Decimal(str(loan_dto.sbi_interest_rate)),
                loan_months=loan_dto.loan_months
            )
        
        # Convert ESOP
        esop = None
        if perquisites_dto.esop:
            esop_dto = perquisites_dto.esop
            esop = ESOPPerquisite(
                shares_exercised=esop_dto.shares_exercised,
                exercise_price=Money.from_decimal(esop_dto.exercise_price),
                allotment_price=Money.from_decimal(esop_dto.allotment_price)
            )
        
        # Convert utilities
        utilities = None
        if perquisites_dto.utilities:
            util_dto = perquisites_dto.utilities
            utilities = UtilitiesPerquisite(
                gas_paid_by_employer=Money.from_decimal(util_dto.gas_paid_by_employer),
                electricity_paid_by_employer=Money.from_decimal(util_dto.electricity_paid_by_employer),
                water_paid_by_employer=Money.from_decimal(util_dto.water_paid_by_employer),
                gas_paid_by_employee=Money.from_decimal(util_dto.gas_paid_by_employee),
                electricity_paid_by_employee=Money.from_decimal(util_dto.electricity_paid_by_employee),
                water_paid_by_employee=Money.from_decimal(util_dto.water_paid_by_employee),
                is_gas_manufactured_by_employer=util_dto.is_gas_manufactured_by_employer,
                is_electricity_manufactured_by_employer=util_dto.is_electricity_manufactured_by_employer,
                is_water_manufactured_by_employer=util_dto.is_water_manufactured_by_employer
            )
        
        # Convert free education
        free_education = None
        if perquisites_dto.free_education:
            edu_dto = perquisites_dto.free_education
            free_education = FreeEducationPerquisite(
                monthly_expenses_child1=Money.from_decimal(edu_dto.monthly_expenses_child1),
                monthly_expenses_child2=Money.from_decimal(edu_dto.monthly_expenses_child2),
                months_child1=edu_dto.months_child1,
                months_child2=edu_dto.months_child2,
                employer_maintained_1st_child=edu_dto.employer_maintained_1st_child,
                employer_maintained_2nd_child=edu_dto.employer_maintained_2nd_child
            )
        
        # Convert movable asset usage
        movable_asset_usage = None
        if perquisites_dto.movable_asset_usage:
            asset_dto = perquisites_dto.movable_asset_usage
            movable_asset_usage = MovableAssetUsage(
                asset_type=AssetType(asset_dto.asset_type),
                asset_value=Money.from_decimal(asset_dto.asset_value),
                employee_payment=Money.from_decimal(asset_dto.employee_payment),
                is_employer_owned=asset_dto.is_employer_owned
            )
        
        # Convert movable asset transfer
        movable_asset_transfer = None
        if perquisites_dto.movable_asset_transfer:
            transfer_dto = perquisites_dto.movable_asset_transfer
            movable_asset_transfer = MovableAssetTransfer(
                asset_type=AssetType(transfer_dto.asset_type),
                asset_cost=Money.from_decimal(transfer_dto.asset_cost),
                years_of_use=transfer_dto.years_of_use,
                employee_payment=Money.from_decimal(transfer_dto.employee_payment)
            )
        
        # Convert lunch refreshment
        lunch_refreshment = None
        if perquisites_dto.lunch_refreshment:
            lunch_dto = perquisites_dto.lunch_refreshment
            lunch_refreshment = LunchRefreshmentPerquisite(
                employer_cost=Money.from_decimal(lunch_dto.employer_cost),
                employee_payment=Money.from_decimal(lunch_dto.employee_payment),
                meal_days_per_year=lunch_dto.meal_days_per_year
            )
        
        # Convert gift voucher
        gift_voucher = None
        if perquisites_dto.gift_voucher:
            gift_dto = perquisites_dto.gift_voucher
            gift_voucher = GiftVoucherPerquisite(
                gift_voucher_amount=Money.from_decimal(gift_dto.gift_voucher_amount)
            )
        
        # Convert monetary benefits
        monetary_benefits = None
        if perquisites_dto.monetary_benefits:
            money_dto = perquisites_dto.monetary_benefits
            monetary_benefits = MonetaryBenefitsPerquisite(
                monetary_amount_paid_by_employer=Money.from_decimal(money_dto.monetary_amount_paid_by_employer),
                expenditure_for_official_purpose=Money.from_decimal(money_dto.expenditure_for_official_purpose),
                amount_paid_by_employee=Money.from_decimal(money_dto.amount_paid_by_employee)
            )
        
        # Convert club expenses
        club_expenses = None
        if perquisites_dto.club_expenses:
            club_dto = perquisites_dto.club_expenses
            club_expenses = ClubExpensesPerquisite(
                club_expenses_paid_by_employer=Money.from_decimal(club_dto.club_expenses_paid_by_employer),
                club_expenses_paid_by_employee=Money.from_decimal(club_dto.club_expenses_paid_by_employee),
                club_expenses_for_official_purpose=Money.from_decimal(club_dto.club_expenses_for_official_purpose)
            )
        
        # Convert domestic help
        domestic_help = None
        if perquisites_dto.domestic_help:
            help_dto = perquisites_dto.domestic_help
            domestic_help = DomesticHelpPerquisite(
                domestic_help_paid_by_employer=Money.from_decimal(help_dto.domestic_help_paid_by_employer),
                domestic_help_paid_by_employee=Money.from_decimal(help_dto.domestic_help_paid_by_employee)
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
            movable_asset_transfer=movable_asset_transfer,
            lunch_refreshment=lunch_refreshment,
            gift_voucher=gift_voucher,
            monetary_benefits=monetary_benefits,
            club_expenses=club_expenses,
            domestic_help=domestic_help
        )
    
    def _convert_house_property_dto_to_entity(self, house_dto) -> HousePropertyIncome:
        """Convert house property DTO to entity."""
        from app.domain.entities.taxation.house_property_income import PropertyType
        
        # Map property type to enum
        property_type_mapping = {
            "Self-Occupied": PropertyType.SELF_OCCUPIED,
            "Let-Out": PropertyType.LET_OUT
        }
        property_type = property_type_mapping.get(house_dto.property_type, PropertyType.SELF_OCCUPIED)
        
        return HousePropertyIncome(
            property_type=property_type,
            address=getattr(house_dto, 'address', ''),
            annual_rent_received=Money.from_decimal(house_dto.annual_rent_received),
            municipal_taxes_paid=Money.from_decimal(house_dto.municipal_taxes_paid),
            home_loan_interest=Money.from_decimal(house_dto.home_loan_interest),
            pre_construction_interest=Money.from_decimal(house_dto.pre_construction_interest)
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
            interest_income = InterestIncome(
                savings_account_interest=Money.from_decimal(int_dto.savings_account_interest),
                fixed_deposit_interest=Money.from_decimal(int_dto.fixed_deposit_interest),
                recurring_deposit_interest=Money.from_decimal(int_dto.recurring_deposit_interest),
                post_office_interest=Money.from_decimal(int_dto.post_office_interest)
            )
        
        # Convert house property income if present
        house_property_income = None
        if hasattr(other_income_dto, 'house_property_income') and other_income_dto.house_property_income:
            house_property_income = self._convert_house_property_dto_to_entity(other_income_dto.house_property_income)
        
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
    
    def _convert_monthly_payroll_dto_to_entity(self, payroll_dto) -> AnnualPayrollWithLWP:
        """Convert monthly payroll DTO to entity."""
        # Convert monthly payrolls
        monthly_payrolls = []
        for mp_dto in payroll_dto.monthly_payrolls:
            monthly_payroll = MonthlyPayroll(
                month=mp_dto.month,
                year=mp_dto.year,
                base_monthly_gross=Money.from_decimal(mp_dto.base_monthly_gross),
                lwp_days=mp_dto.lwp_days,
                working_days_in_month=mp_dto.working_days_in_month
            )
            monthly_payrolls.append(monthly_payroll)
        
        # Convert LWP details
        lwp_details = []
        for lwp_dto in payroll_dto.lwp_details:
            lwp_detail = LWPDetails(
                month=lwp_dto.month,
                year=lwp_dto.year,
                lwp_days=lwp_dto.lwp_days,
                working_days_in_month=lwp_dto.working_days_in_month
            )
            lwp_details.append(lwp_detail)
        
        return AnnualPayrollWithLWP(
            monthly_payrolls=monthly_payrolls,
            annual_salary=Money.from_decimal(payroll_dto.annual_salary),
            total_lwp_days=payroll_dto.total_lwp_days,
            lwp_details=lwp_details
        )
    
    # =============================================================================
    # MID-YEAR SCENARIO HELPER METHODS
    # =============================================================================
    
    def _validate_mid_year_increment_request(self, request, tax_year: str, regime_type: str, age: int):
        """Validate mid-year increment request."""
        if not request.increment_date:
            raise ValueError("Increment date is required")
        
        if not request.pre_increment_salary or not request.post_increment_salary:
            raise ValueError("Both pre and post increment salary details are required")
        
        if regime_type not in ["old", "new"]:
            raise ValueError("Invalid regime type")
        
        if age < 18 or age > 100:
            raise ValueError("Invalid age")
    
    def _create_periodic_salary_from_mid_year_increment(self, request, tax_year: str):
        """Create PeriodicSalaryIncome from mid-year increment request."""
        from app.domain.value_objects.tax_year import TaxYear
        from app.domain.entities.periodic_salary_income import PeriodicSalaryIncome
        
        # Parse tax year
        tax_year_obj = TaxYear.from_string(tax_year)
        
        # Convert DTOs to SalaryIncome entities
        pre_salary = self._convert_periodic_salary_data_to_salary_income(request.pre_increment_salary)
        post_salary = self._convert_periodic_salary_data_to_salary_income(request.post_increment_salary)
        
        # Create periodic salary with increment
        return PeriodicSalaryIncome.create_with_increment(
            initial_salary=pre_salary,
            increment_salary=post_salary,
            increment_date=request.increment_date,
            tax_year=tax_year_obj
        )
    
    def _convert_periodic_salary_data_to_salary_income(self, salary_data_dto):
        """Convert PeriodicSalaryDataDTO to SalaryIncome entity."""
        from app.domain.entities.taxation.salary_income import SalaryIncome
        from app.domain.value_objects.money import Money
        
        return SalaryIncome(
            basic_salary=Money.from_decimal(salary_data_dto.basic_salary),
            dearness_allowance=Money.from_decimal(salary_data_dto.dearness_allowance),
            hra_provided=Money.from_decimal(salary_data_dto.hra_provided),
            special_allowance=Money.from_decimal(salary_data_dto.special_allowance),
            bonus=Money.from_decimal(getattr(salary_data_dto, 'bonus', 0)),
            commission=Money.from_decimal(getattr(salary_data_dto, 'commission', 0))
            # Note: hra_city_type and actual_rent_paid are now handled in deductions module
        )
    
    def _create_comprehensive_from_periodic_salary(self, periodic_salary, regime_type: str, age: int, deductions: Dict[str, float], tax_year: str):
        """Create ComprehensiveTaxInputDTO from PeriodicSalaryIncome."""
        from app.application.dto.taxation_dto import ComprehensiveTaxInputDTO, TaxDeductionsDTO
        from app.application.dto.taxation_dto import DeductionSection80CDTO, DeductionSection80DDTO
        
        # Convert periodic salary to DTO
        periodic_salary_dto = self._convert_periodic_salary_entity_to_dto(periodic_salary)
        
        # Create deductions DTO
        section_80c = DeductionSection80CDTO(
            epf_contribution=deductions.get("section_80c", 0)
        )
        
        section_80d = DeductionSection80DDTO(
            self_family_premium=deductions.get("section_80d", 0),
            employee_age=age
        )
        
        deductions_dto = TaxDeductionsDTO(
            section_80c=section_80c,
            section_80d=section_80d
        )
        
        return ComprehensiveTaxInputDTO(
            tax_year=tax_year,
            regime_type=regime_type,
            age=age,
            periodic_salary_income=periodic_salary_dto,
            deductions=deductions_dto
        )
    
    def _convert_periodic_salary_entity_to_dto(self, periodic_salary):
        """Convert PeriodicSalaryIncome entity to DTO."""
        from app.application.dto.taxation_dto import PeriodicSalaryIncomeDTO, PeriodicSalaryDataDTO, EmploymentPeriodDTO
        
        periods_dto = []
        for period_data in periodic_salary.periods:
            period_dto = EmploymentPeriodDTO(
                start_date=period_data.period.start_date,
                end_date=period_data.period.end_date,
                description=period_data.period.description
            )
            
            salary_data_dto = PeriodicSalaryDataDTO(
                period=period_dto,
                basic_salary=period_data.salary_income.basic_salary.to_float(),
                dearness_allowance=period_data.salary_income.dearness_allowance.to_float(),
                hra_provided=period_data.salary_income.hra_provided.to_float(),
                hra_city_type="metro",  # Default value - HRA details are in deductions module
                actual_rent_paid=0.0,   # Default value - HRA details are in deductions module
                special_allowance=period_data.salary_income.special_allowance.to_float(),
                bonus=period_data.salary_income.bonus.to_float(),
                commission=period_data.salary_income.commission.to_float()
            )
            
            periods_dto.append(salary_data_dto)
        
        return PeriodicSalaryIncomeDTO(periods=periods_dto)
    
    def _add_mid_year_enhancements(self, result, request, scenario_type: str):
        """Add mid-year specific enhancements to calculation result."""
        # Add mid-year specific analysis
        if hasattr(result, 'mid_year_impact'):
            if scenario_type == "increment":
                result.optimization_suggestions.extend([
                    f"Mid-year increment from {request.increment_date.strftime('%B %Y')} provides tax optimization",
                    "Consider adjusting Section 80C investments in higher salary period",
                    "Plan annual bonuses and allowances in lower tax periods"
                ])
        
        return result
    
    def _update_taxation_record_from_dto(self, taxation_record: TaxationRecord, request: ComprehensiveTaxInputDTO) -> TaxationRecord:
        """
        Update a TaxationRecord entity with data from ComprehensiveTaxInputDTO.
        
        Args:
            taxation_record: Existing TaxationRecord to update
            request: ComprehensiveTaxInputDTO with new data
            
        Returns:
            TaxationRecord: Updated taxation record
        """
        # Update basic information
        taxation_record.age = request.age
        taxation_record.regime = TaxRegime(TaxRegimeType.OLD if request.regime_type.lower() == "old" else TaxRegimeType.NEW)
        
        # Update salary income if provided
        if request.salary_income:
            salary_income = self._convert_salary_dto_to_entity(request.salary_income)
            taxation_record.update_salary(salary_income)
        
        # Update deductions if provided
        if request.deductions:
            deductions = self._convert_deductions_dto_to_entity(request.deductions)
            taxation_record.update_deductions(deductions)
        
        # Update perquisites if provided
        if request.perquisites:
            perquisites = self._convert_perquisites_dto_to_entity(request.perquisites)
            taxation_record.update_perquisites(perquisites)
        else:
            taxation_record.update_perquisites(None)
        
        # Update other income (including house property income and capital gains) if provided
        if request.other_income or request.house_property_income or request.capital_gains_income:
            # Create other income entity
            other_income = None
            if request.other_income:
                other_income = self._convert_other_income_dto_to_entity(request.other_income)
            else:
                # Create default other income if only house property or capital gains is provided
                from app.domain.entities.taxation.other_income import OtherIncome
                other_income = OtherIncome()
            
            # Add house property income if provided separately
            if request.house_property_income:
                house_property = self._convert_house_property_dto_to_entity(request.house_property_income)
                other_income.house_property_income = house_property
            
            # Add capital gains income if provided separately
            if request.capital_gains_income:
                capital_gains = self._convert_capital_gains_dto_to_entity(request.capital_gains_income)
                other_income.capital_gains_income = capital_gains
            
            taxation_record.update_other_income(other_income)
        else:
            taxation_record.update_other_income(None)
        
        # Update retirement benefits if provided
        if request.retirement_benefits:
            retirement_benefits = self._convert_retirement_benefits_dto_to_entity(request.retirement_benefits)
            taxation_record.update_retirement_benefits(retirement_benefits)
        else:
            taxation_record.update_retirement_benefits(None)
        
        # Update monthly payroll if provided
        if request.monthly_payroll:
            monthly_payroll = self._convert_monthly_payroll_dto_to_entity(request.monthly_payroll)
            taxation_record.update_monthly_payroll(monthly_payroll)
        else:
            taxation_record.update_monthly_payroll(None)
        
        return taxation_record

    async def calculate_comprehensive_tax_for_employee(self,
                                                     employee_id: str,
                                                     request: ComprehensiveTaxInputDTO,
                                                     organization_id: str) -> TaxCalculationResult:
        """
        Calculate comprehensive tax for a specific employee and update their taxation record.
        
        This method:
        1. Gets the taxation record for employee and tax_year from database
        2. Updates the record with data from ComprehensiveTaxInputDTO
        3. Computes tax using the enhanced tax service
        4. Updates the record with computed tax results
        5. Saves the updated record back to database
        6. Returns TaxCalculationResult
        
        Args:
            employee_id: Employee ID for the record
            request: ComprehensiveTaxInputDTO containing tax data
            organization_id: Organization ID for database operations
            
        Returns:
            TaxCalculationResult: Tax calculation result with database update
            
        Raises:
            ValueError: If employee_id or tax_year is invalid
            RuntimeError: If database operations fail
        """
        
        logger.info(f"Calculating comprehensive tax for employee {employee_id}, tax_year: {request.tax_year}")
        
        try:
            # Step 1: Get existing taxation record from database
            taxation_record = await self.taxation_repository.get_taxation_record(
                employee_id, request.tax_year, organization_id
            )
            
            # If no record exists, create a new one
            if not taxation_record:
                logger.info(f"No existing record found for employee {employee_id}, creating new record")
                taxation_record = await self._create_new_taxation_record(
                    employee_id, request, organization_id
                )
            
            # Step 2: Update the taxation record with DTO data
            updated_record = self._update_taxation_record_from_dto(taxation_record, request)
            
            # Step 3: Calculate tax and update the record
            calculation_result = await self.enhanced_tax_service.calculate_and_update_taxation_record(
                updated_record, organization_id
            )
            
            logger.info(f"Successfully calculated and updated tax for employee {employee_id}")
            return calculation_result
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive tax for employee {employee_id}: {e}")
            raise RuntimeError(f"Failed to calculate comprehensive tax: {str(e)}")
    
    async def _create_new_taxation_record(self,
                                        employee_id: str,
                                        request: ComprehensiveTaxInputDTO,
                                        organization_id: str) -> TaxationRecord:
        """Create a new taxation record for the employee."""
        
        try:
            # Get user information for additional details
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), organization_id)
            if not user:
                raise ValueError(f"Employee {employee_id} not found")
            
            # Create default salary income if not provided
            if request.salary_income:
                salary_income = self._convert_salary_dto_to_entity(request.salary_income)
            else:
                salary_income = self._create_default_salary_income()
            
            # Create default deductions if not provided
            if request.deductions:
                deductions = self._convert_deductions_dto_to_entity(request.deductions)
            else:
                deductions = self._create_default_deductions()
            
            # Create the taxation record with all required parameters
            taxation_record = TaxationRecord(
                employee_id=EmployeeId(employee_id),
                tax_year=TaxYear.from_string(request.tax_year),
                salary_income=salary_income,
                deductions=deductions,
                regime=TaxRegime.from_string(request.regime_type),
                age=request.age,
                organization_id=organization_id
            )
            
            return taxation_record
            
        except Exception as e:
            logger.error(f"Error creating new taxation record for employee {employee_id}: {e}")
            raise ValueError(f"Failed to create taxation record: {str(e)}")
    
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
            default_salary_income = SalaryIncome(
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
        
        # Create new salary package record with correct parameters
        salary_package_record = SalaryPackageRecord(
            employee_id=employee_id_vo,
            tax_year=tax_year_vo,
            age=25,  # Default age
            regime=TaxRegime.old_regime(),  # Default to old regime
            salary_incomes=[default_salary_income],
            deductions=default_deductions,
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
        """Update perquisites component individually."""
        
        try:
            # Get or create taxation record
            taxation_record = await self._get_or_create_taxation_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            # Convert DTO to entity
            perquisites = self._convert_perquisites_dto_to_entity(request.perquisites)
            
            # Update the record
            taxation_record.perquisites = perquisites
            taxation_record.updated_at = datetime.utcnow()
            
            # Save to database
            await self.taxation_repository.save(taxation_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=taxation_record.taxation_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="perquisites",
                status="success",
                message="Perquisites component updated successfully",
                updated_at=taxation_record.updated_at,
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
        """Update deductions component individually."""
        
        try:
            # Get or create taxation record
            taxation_record = await self._get_or_create_taxation_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            # Convert DTO to entity
            deductions = self._convert_comprehensive_deductions_dto_to_entity(request.deductions)
            
            # Update the record
            taxation_record.deductions = deductions
            taxation_record.updated_at = datetime.utcnow()
            
            # Save to database
            await self.taxation_repository.save(taxation_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=taxation_record.taxation_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="deductions",
                status="success",
                message="Deductions component updated successfully",
                updated_at=taxation_record.updated_at,
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
        """Update house property component individually."""
        
        try:
            # Get or create taxation record
            taxation_record = await self._get_or_create_taxation_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            # Convert DTO to entity
            house_property = self._convert_house_property_dto_to_entity(request.house_property_income)
            
            # Create or update other_income
            if not taxation_record.other_income:
                taxation_record.other_income = self._create_default_other_income()
            
            # Update house property in other income
            taxation_record.other_income.house_property_income = house_property
            taxation_record.updated_at = datetime.utcnow()
            
            # Save to database
            await self.taxation_repository.save(taxation_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=taxation_record.taxation_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="house_property_income",
                status="success",
                message="House property component updated successfully",
                updated_at=taxation_record.updated_at,
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
        """Update capital gains component individually."""
        
        try:
            # Get or create taxation record
            taxation_record = await self._get_or_create_taxation_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            # Convert DTO to entity
            capital_gains = self._convert_capital_gains_dto_to_entity(request.capital_gains_income)
            
            # Create or update other_income
            if not taxation_record.other_income:
                taxation_record.other_income = self._create_default_other_income()
            
            # Update capital gains in other income
            taxation_record.other_income.capital_gains_income = capital_gains
            taxation_record.updated_at = datetime.utcnow()
            
            # Save to database
            await self.taxation_repository.save(taxation_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=taxation_record.taxation_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="capital_gains_income",
                status="success",
                message="Capital gains component updated successfully",
                updated_at=taxation_record.updated_at,
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
        """Update retirement benefits component individually."""
        
        try:
            # Get or create taxation record
            taxation_record = await self._get_or_create_taxation_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            # Convert DTO to entity
            retirement_benefits = self._convert_retirement_benefits_dto_to_entity(request.retirement_benefits)
            
            # Update the record
            taxation_record.retirement_benefits = retirement_benefits
            taxation_record.updated_at = datetime.utcnow()
            
            # Save to database
            await self.taxation_repository.save(taxation_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=taxation_record.taxation_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="retirement_benefits",
                status="success",
                message="Retirement benefits component updated successfully",
                updated_at=taxation_record.updated_at,
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
        """Update other income component individually."""
        
        try:
            # Get or create taxation record
            taxation_record = await self._get_or_create_taxation_record(
                request.employee_id, request.tax_year, organization_id
            )
            
            # Convert DTO to entity
            other_income = self._convert_other_income_dto_to_entity(request.other_income)
            
            # Update the record
            taxation_record.other_income = other_income
            taxation_record.updated_at = datetime.utcnow()
            
            # Save to database
            await self.taxation_repository.save(taxation_record, organization_id)
            
            return ComponentUpdateResponse(
                taxation_id=taxation_record.taxation_id,
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                component_type="other_income",
                status="success",
                message="Other income component updated successfully",
                updated_at=taxation_record.updated_at,
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
    
    async def _get_or_create_taxation_record(
        self,
        employee_id: str,
        tax_year: str,
        organization_id: str
    ) -> TaxationRecord:
        """Get existing taxation record or create a new one with defaults."""
        
        # Try to get existing record
        taxation_record = await self.taxation_repository.get_taxation_record(
            employee_id, tax_year, organization_id
        )
        
        if taxation_record:
            return taxation_record
        
        # Create new record with defaults
        employee_id_vo = EmployeeId(employee_id)
        tax_year_vo = TaxYear.from_string(tax_year)
        
        # Create default components
        salary_income = self._create_default_salary_income()
        deductions = self._create_default_deductions()
        perquisites = self._create_default_perquisites()
        other_income = self._create_default_other_income()
        retirement_benefits = self._create_default_retirement_benefits()
        regime = TaxRegime(TaxRegimeType.OLD)  # Default to old regime
        
        taxation_record = TaxationRecord(
            employee_id=employee_id_vo,
            tax_year=tax_year_vo,
            salary_income=salary_income,
            deductions=deductions,
            perquisites=perquisites,
            other_income=other_income,
            retirement_benefits=retirement_benefits,
            regime=regime,
            age=25,  # Default age
            organization_id=organization_id
        )
        
        # Save the new record
        await self.taxation_repository.save(taxation_record, organization_id)
        
        return taxation_record
    
    def _extract_component_data(self, taxation_record: TaxationRecord, component_type: str) -> Dict[str, Any]:
        """Extract component data from taxation record."""
        
        # Handle frontend component type aliases
        component_type_mapping = {
            "salary": "salary_income",
            "house-property": "house_property_income",
            "capital-gains": "capital_gains_income",
            "retirement-benefits": "retirement_benefits",
            "other-income": "other_income",
            "monthly-payroll": "monthly_payroll"
        }
        
        # Map frontend component type to backend component type
        mapped_component_type = component_type_mapping.get(component_type, component_type)
        
        if mapped_component_type == "salary_income":
            return self._serialize_salary_income(taxation_record.salary_income)
        elif mapped_component_type == "perquisites":
            return self._serialize_perquisites(taxation_record.perquisites) if taxation_record.perquisites else {}
        elif mapped_component_type == "deductions":
            return self._serialize_deductions(taxation_record.deductions)
        elif mapped_component_type == "house_property_income":
            if taxation_record.other_income and taxation_record.other_income.house_property_income:
                return self._serialize_house_property_income(taxation_record.other_income.house_property_income)
            return {}
        elif mapped_component_type == "capital_gains_income":
            if taxation_record.other_income and taxation_record.other_income.capital_gains_income:
                return self._serialize_capital_gains_income(taxation_record.other_income.capital_gains_income)
            return {}
        elif mapped_component_type == "retirement_benefits":
            return self._serialize_retirement_benefits(taxation_record.retirement_benefits) if taxation_record.retirement_benefits else {}
        elif mapped_component_type == "other_income":
            return self._serialize_other_income(taxation_record.other_income) if taxation_record.other_income else {}
        elif mapped_component_type == "monthly_payroll":
            return self._serialize_monthly_payroll(taxation_record.monthly_payroll) if taxation_record.monthly_payroll else {}
        elif mapped_component_type == "regime":
            return {
                "regime_type": taxation_record.regime.regime_type.value,
                "age": taxation_record.age
            }
        else:
            raise ValueError(f"Unknown component type: {component_type}")
    
    def _extract_component_data_from_salary_package(self, salary_package_record: SalaryPackageRecord, component_type: str) -> Dict[str, Any]:
        """Extract component data from salary package record."""
        
        # Handle frontend component type aliases
        component_type_mapping = {
            "salary": "salary_income",
            "house-property": "house_property_income",
            "capital-gains": "capital_gains_income",
            "retirement-benefits": "retirement_benefits",
            "other-income": "other_income",
            "monthly-payroll": "monthly_payroll"
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
    
    def _build_components_status(self, taxation_record: TaxationRecord) -> Dict[str, Dict[str, Any]]:
        """Build status of all components."""
        
        components_status = {}
        
        # Component type mapping for frontend compatibility
        component_type_mapping = {
            "salary": "salary_income",
            "house-property": "house_property_income",
            "capital-gains": "capital_gains_income",
            "retirement-benefits": "retirement_benefits",
            "other-income": "other_income",
            "monthly-payroll": "monthly_payroll"
        }
        
        # Salary income
        components_status["salary"] = {
            "has_data": True,
            "last_updated": taxation_record.updated_at.isoformat(),
            "status": "complete"
        }
        
        # Deductions
        components_status["deductions"] = {
            "has_data": True,
            "last_updated": taxation_record.updated_at.isoformat(),
            "status": "complete"
        }
        
        # Perquisites
        components_status["perquisites"] = {
            "has_data": taxation_record.perquisites is not None,
            "last_updated": taxation_record.updated_at.isoformat() if taxation_record.perquisites else None,
            "status": "complete" if taxation_record.perquisites else "not_provided"
        }
        
        # House property income
        has_house_property = (taxation_record.other_income and 
                            taxation_record.other_income.house_property_income)
        components_status["house-property"] = {
            "has_data": has_house_property,
            "last_updated": taxation_record.updated_at.isoformat() if has_house_property else None,
            "status": "complete" if has_house_property else "not_provided"
        }
        
        # Capital gains income
        has_capital_gains = (taxation_record.other_income and 
                           taxation_record.other_income.capital_gains_income)
        components_status["capital-gains"] = {
            "has_data": has_capital_gains,
            "last_updated": taxation_record.updated_at.isoformat() if has_capital_gains else None,
            "status": "complete" if has_capital_gains else "not_provided"
        }
        
        # Retirement benefits
        components_status["retirement-benefits"] = {
            "has_data": taxation_record.retirement_benefits is not None,
            "last_updated": taxation_record.updated_at.isoformat() if taxation_record.retirement_benefits else None,
            "status": "complete" if taxation_record.retirement_benefits else "not_provided"
        }
        
        # Other income
        components_status["other-income"] = {
            "has_data": taxation_record.other_income is not None,
            "last_updated": taxation_record.updated_at.isoformat() if taxation_record.other_income else None,
            "status": "complete" if taxation_record.other_income else "not_provided"
        }
        
        # Monthly payroll
        components_status["monthly-payroll"] = {
            "has_data": taxation_record.monthly_payroll is not None,
            "last_updated": taxation_record.updated_at.isoformat() if taxation_record.monthly_payroll else None,
            "status": "complete" if taxation_record.monthly_payroll else "not_provided"
        }
        
        # Regime
        components_status["regime"] = {
            "has_data": True,
            "last_updated": taxation_record.updated_at.isoformat(),
            "status": "complete",
            "regime_type": taxation_record.regime.regime_type.value,
            "age": taxation_record.age
        }
        
        return components_status
    
    def _determine_overall_status(self, components_status: Dict[str, Dict[str, Any]]) -> str:
        """Determine overall status based on component statuses."""
        
        required_components = ["salary", "deductions", "regime"]
        optional_components = ["perquisites", "house-property", "capital-gains", 
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
                "basic_salary": float(acc.basic_salary.amount),
                "dearness_allowance": float(acc.dearness_allowance.amount),
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
        if perquisites.interest_free_concessional_loan:
            loan = perquisites.interest_free_concessional_loan
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
        """Serialize deductions to dict."""
        if not deductions:
            return {
                "section_80c_investments": 0.0,
                "section_80d_health_insurance": 0.0,
                "section_80d_parents_health_insurance": 0.0,
                "section_80e_education_loan": 0.0,
                "section_80g_donations": 0.0,
                "section_80tta_savings_interest": 0.0,
                "section_80ccd1b_nps": 0.0
            }
        
        # Calculate section 80C total investments
        section_80c_total = 0.0
        if deductions.section_80c:
            section_80c_total = float(deductions.section_80c.calculate_total_investment().amount)
        
        # Get section 80D health insurance amounts
        section_80d_health_insurance = 0.0
        section_80d_parents_health_insurance = 0.0
        if deductions.section_80d:
            section_80d_health_insurance = float(deductions.section_80d.self_family_premium.amount)
            section_80d_parents_health_insurance = float(deductions.section_80d.parent_premium.amount)
        
        # Get section 80E education loan interest
        section_80e_education_loan = 0.0
        if deductions.section_80e:
            section_80e_education_loan = float(deductions.section_80e.education_loan_interest.amount)
        
        # Get section 80G donations
        section_80g_donations = 0.0
        if deductions.section_80g:
            section_80g_donations = float(deductions.section_80g.calculate_total_donations().amount)
        
        # Get section 80TTA savings interest
        section_80tta_savings_interest = 0.0
        if deductions.section_80tta_ttb:
            section_80tta_savings_interest = float(deductions.section_80tta_ttb.savings_interest.amount)
        
        # Get section 80CCD(1B) NPS contribution
        section_80ccd1b_nps = 0.0
        if deductions.section_80ccd:
            section_80ccd1b_nps = float(deductions.section_80ccd.additional_nps_contribution.amount)
        
        return {
            "section_80c_investments": section_80c_total,
            "section_80d_health_insurance": section_80d_health_insurance,
            "section_80d_parents_health_insurance": section_80d_parents_health_insurance,
            "section_80e_education_loan": section_80e_education_loan,
            "section_80g_donations": section_80g_donations,
            "section_80tta_savings_interest": section_80tta_savings_interest,
            "section_80ccd1b_nps": section_80ccd1b_nps
        }
    
    def _serialize_house_property_income(self, house_property: HousePropertyIncome) -> Dict[str, Any]:
        """Serialize house property income to dict."""
        return {
            "property_type": house_property.property_type.value,
            "address": house_property.address,
            "annual_rent_received": float(house_property.annual_rent_received.amount),
            "municipal_taxes_paid": float(house_property.municipal_taxes_paid.amount),
            "home_loan_interest": float(house_property.home_loan_interest.amount),
            "pre_construction_interest": float(house_property.pre_construction_interest.amount)
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
                "savings_interest": float(interest.savings_interest.amount),
                "fd_interest": float(interest.fd_interest.amount),
                "rd_interest": float(interest.rd_interest.amount),
                "post_office_interest": float(interest.post_office_interest.amount)
            }
        
        # Serialize house property income
        if other_income.house_property_income:
            result["house_property_income"] = self._serialize_house_property_income(other_income.house_property_income)
        
        # Serialize capital gains income
        if other_income.capital_gains_income:
            result["capital_gains_income"] = self._serialize_capital_gains_income(other_income.capital_gains_income)
        
        return result
    
    def _serialize_monthly_payroll(self, monthly_payroll: AnnualPayrollWithLWP) -> Dict[str, Any]:
        """Serialize monthly payroll to dict."""
        if not monthly_payroll:
            return {}
        
        return {
            "monthly_payrolls": [payroll.to_dict() for payroll in monthly_payroll.monthly_payrolls],
            "annual_salary": float(monthly_payroll.annual_salary.amount),
            "total_lwp_days": monthly_payroll.total_lwp_days,
            "lwp_details": [lwp.to_dict() for lwp in monthly_payroll.lwp_details]
        }


        async def compute_monthly_tax(self, employee_id: EmployeeId, month: int, year: int) -> Dict[str, Any]:
            """Compute monthly tax."""
            
            return {}
        

