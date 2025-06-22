"""
Use case for getting comprehensive taxation record by employee ID.
Handles fetching detailed taxation records and creating default records with computed values.
"""

from typing import Optional
from datetime import datetime, date
import logging

from app.application.dto.taxation_dto import ComprehensiveTaxOutputDTO, CapitalGainsIncomeDTO
from app.domain.repositories.taxation_repository import TaxationRepository
from app.application.interfaces.repositories.user_repository import UserQueryRepository
from app.application.interfaces.repositories.organisation_repository import OrganisationQueryRepository
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.organisation_id import OrganisationId
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class GetComprehensiveTaxationRecordUseCase:
    """
    Use case for retrieving comprehensive taxation record by employee ID.
    
    This use case:
    1. Validates the employee ID and tax year
    2. Fetches the taxation record from repository
    3. If not found, creates default record with computed values:
       - Age computed from DOB in user info
       - is_govt_employee based on organization type
       - employee_id from UI parameter
    4. Converts domain entity to ComprehensiveTaxOutputDTO
    """
    
    def __init__(
        self, 
        taxation_repository: TaxationRepository,
        user_repository: UserQueryRepository,
        organisation_repository: OrganisationQueryRepository
    ):
        self._taxation_repository = taxation_repository
        self._user_repository = user_repository
        self._organisation_repository = organisation_repository
    
    async def execute(
        self,
        employee_id: str,
        organization_id: str,
        tax_year: Optional[str] = None
    ) -> ComprehensiveTaxOutputDTO:
        """
        Execute the use case to get comprehensive taxation record by employee ID.
        
        Args:
            employee_id: Employee ID to fetch record for
            organization_id: Organization ID for context
            tax_year: Optional tax year filter (e.g., "2024-25")
            
        Returns:
            ComprehensiveTaxOutputDTO: Comprehensive taxation record
            
        Raises:
            ValueError: If employee_id is invalid
            Exception: If record not found or other errors occur
        """
        
        logger.info(f"Getting comprehensive taxation record for employee {employee_id}, tax_year: {tax_year}")
        
        # Validate inputs
        if not employee_id or not employee_id.strip():
            raise ValueError("Employee ID is required")
        
        if not organization_id or not organization_id.strip():
            raise ValueError("Organization ID is required")
        
        try:
            # Default tax_year to current tax year if None
            effective_tax_year = tax_year or self._get_current_tax_year()
            
            # Get taxation record from repository
            taxation_record = await self._taxation_repository.get_taxation_record(
                employee_id=employee_id,
                tax_year=effective_tax_year,
                organisation_id=organization_id
            )
            
            if taxation_record:
                # Convert existing domain entity to DTO
                return await self._convert_to_comprehensive_dto(taxation_record, employee_id, organization_id, effective_tax_year)
            else:
                # Create default record with computed values
                return await self._create_default_comprehensive_record(employee_id, organization_id, effective_tax_year)
                
        except Exception as e:
            logger.error(f"Error getting comprehensive taxation record for employee {employee_id}: {str(e)}")
            raise
    
    def _get_financial_year(self, tax_year: Optional[str]) -> int:
        """
        Convert tax year string to financial year integer.
        
        Args:
            tax_year: Tax year string (e.g., "2024-25")
            
        Returns:
            Financial year as integer (e.g., 2024)
        """
        if tax_year:
            try:
                return int(tax_year.split('-')[0])
            except (ValueError, IndexError):
                logger.warning(f"Invalid tax year format: {tax_year}, using current year")
        
        # Default to current financial year
        current_date = date.today()
        if current_date.month >= 4:  # April onwards is new financial year
            return current_date.year
        else:
            return current_date.year - 1
    
    def _get_current_tax_year(self) -> str:
        """Get current tax year string."""
        financial_year = self._get_financial_year(None)
        return f"{financial_year}-{str(financial_year + 1)[2:]}"
    
    async def _convert_to_comprehensive_dto(
        self, 
        taxation_record, 
        employee_id: str, 
        organization_id: str, 
        tax_year: str
    ) -> ComprehensiveTaxOutputDTO:
        """
        Convert existing domain entity to ComprehensiveTaxOutputDTO.
        
        Args:
            taxation_record: Domain taxation record entity
            employee_id: Employee ID
            organization_id: Organization ID
            tax_year: Tax year string
            
        Returns:
            ComprehensiveTaxOutputDTO: DTO for API response
        """
        
        # Get user information for age and other details
        user = await self._user_repository.get_by_id(EmployeeId(employee_id), organization_id)
        age = await self._compute_age_from_user(user) if user else 30
        
        # Get organization information for government employee check
        organisation = await self._organisation_repository.get_by_hostname(organization_id)
        is_govt_employee = organisation.is_government_organisation() if organisation else False
        
        # Get regime information
        regime = "new"  # Default
        if hasattr(taxation_record, 'regime') and taxation_record.regime:
            if hasattr(taxation_record.regime, 'regime_type'):
                regime = taxation_record.regime.regime_type.value.lower()
            elif hasattr(taxation_record.regime, 'value'):
                regime = taxation_record.regime.value.lower()
        
        # Capital gains income (now part of other_income)
        capital_gains_dto = None
        if taxation_record.other_income and taxation_record.other_income.capital_gains_income:
            capital_gains = taxation_record.other_income.capital_gains_income
            capital_gains_dto = CapitalGainsIncomeDTO(
                stcg_111a_equity_stt=capital_gains.stcg_111a_equity_stt.to_float(),
                stcg_other_assets=capital_gains.stcg_other_assets.to_float(),
                stcg_debt_mf=capital_gains.stcg_debt_mf.to_float(),
                ltcg_112a_equity_stt=capital_gains.ltcg_112a_equity_stt.to_float(),
                ltcg_other_assets=capital_gains.ltcg_other_assets.to_float(),
                ltcg_debt_mf=capital_gains.ltcg_debt_mf.to_float()
            )
        
        # Convert existing record to comprehensive DTO with actual values
        return ComprehensiveTaxOutputDTO(
            tax_year=tax_year,
            regime_type=regime,
            age=age,
            is_govt_employee=is_govt_employee,
            employee_id=employee_id,
            # Convert actual income sources from entity
            salary_income=self._convert_salary_income_entity_to_dto(taxation_record.salary_income) if hasattr(taxation_record, 'salary_income') and taxation_record.salary_income else None,
            periodic_salary_income=self._convert_periodic_salary_entity_to_dto(taxation_record.periodic_salary_income) if hasattr(taxation_record, 'periodic_salary_income') and taxation_record.periodic_salary_income else None,
            perquisites=self._convert_perquisites_entity_to_dto(taxation_record.perquisites) if hasattr(taxation_record, 'perquisites') and taxation_record.perquisites else None,
            house_property_income=self._convert_house_property_entity_to_dto(
                taxation_record.other_income.house_property_income if hasattr(taxation_record, 'other_income') and taxation_record.other_income and hasattr(taxation_record.other_income, 'house_property_income') else None
            ),
            multiple_house_properties=None,  # Not implemented yet
            capital_gains_income=capital_gains_dto,
            retirement_benefits=self._convert_retirement_benefits_entity_to_dto(taxation_record.retirement_benefits) if hasattr(taxation_record, 'retirement_benefits') and taxation_record.retirement_benefits else None,
            other_income=self._convert_other_income_entity_to_dto(taxation_record.other_income) if hasattr(taxation_record, 'other_income') and taxation_record.other_income else None,
            monthly_payroll=self._convert_monthly_payroll_entity_to_dto(taxation_record.monthly_payroll) if hasattr(taxation_record, 'monthly_payroll') and taxation_record.monthly_payroll else None,
            deductions=self._convert_deductions_entity_to_dto(taxation_record.deductions) if hasattr(taxation_record, 'deductions') and taxation_record.deductions else None
        )
    
    async def _create_default_comprehensive_record(
        self, 
        employee_id: str, 
        organization_id: str, 
        tax_year: str
    ) -> ComprehensiveTaxOutputDTO:
        """
        Create a default comprehensive record when no taxation record exists.
        
        Args:
            employee_id: Employee ID
            organization_id: Organization ID
            tax_year: Tax year string
            
        Returns:
            ComprehensiveTaxOutputDTO: Default comprehensive record
        """
        
        # Get user information for age computation
        user = await self._user_repository.get_by_id(EmployeeId(employee_id), organization_id)
        age = await self._compute_age_from_user(user) if user else 30
        
        # Get organization information for government employee check
        organisation = await self._organisation_repository.get_by_hostname(organization_id)
        is_govt_employee = organisation.is_government_organisation() if organisation else False
        
        logger.info(f"Creating default comprehensive record for employee {employee_id}, age: {age}, is_govt_employee: {is_govt_employee}")
        
        return ComprehensiveTaxOutputDTO(
            tax_year=tax_year,
            regime_type="new",  # Default to new regime
            age=age,
            is_govt_employee=is_govt_employee,
            employee_id=employee_id,
            # All income sources are None (zero values) by default
            salary_income=None,
            periodic_salary_income=None,
            perquisites=None,
            house_property_income=None,
            multiple_house_properties=None,
            capital_gains_income=None,
            retirement_benefits=None,
            other_income=None,
            monthly_payroll=None,
            deductions=None
        )
    
    async def _compute_age_from_user(self, user) -> int:
        """
        Compute age from user's date of birth.
        
        Args:
            user: User entity
            
        Returns:
            Age in years
        """
        if not user:
            return 30  # Default age
        
        try:
            # Try to get date of birth from different possible locations
            date_of_birth = None
            
            # Check personal_details first
            if hasattr(user, 'personal_details') and user.personal_details:
                if hasattr(user.personal_details, 'date_of_birth'):
                    date_of_birth = user.personal_details.date_of_birth
            
            # Fallback to direct attribute
            if not date_of_birth and hasattr(user, 'date_of_birth'):
                date_of_birth = user.date_of_birth
            
            if not date_of_birth:
                logger.warning(f"No date of birth found for user {user.employee_id}, using default age 30")
                return 30
            
            # Handle different date formats
            if isinstance(date_of_birth, str):
                # Try to parse string date
                try:
                    if 'T' in date_of_birth:  # ISO format with time
                        dob = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00')).date()
                    else:
                        dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Invalid date format for user {user.employee_id}: {date_of_birth}")
                    return 30
            elif isinstance(date_of_birth, datetime):
                dob = date_of_birth.date()
            elif isinstance(date_of_birth, date):
                dob = date_of_birth
            else:
                logger.warning(f"Unknown date type for user {user.employee_id}: {type(date_of_birth)}")
                return 30
            
            # Calculate age
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Validate age range
            if age < 18 or age > 100:
                logger.warning(f"Invalid computed age {age} for user {user.employee_id}, using default age 30")
                return 30
            
            logger.info(f"Computed age {age} for user {user.employee_id} from DOB {dob}")
            return age
            
        except Exception as e:
            logger.error(f"Error computing age for user {user.employee_id if user else 'unknown'}: {str(e)}")
            return 30  # Default age on error
    
    def _convert_salary_income_entity_to_dto(self, salary_income):
        """Convert SalaryIncome entity to SalaryIncomeDTO."""
        from app.application.dto.taxation_dto import SalaryIncomeDTO
        
        if not salary_income:
            return None
        
        def get_allowance_value(field_name, default=0):
            """Helper function to get allowance value from either direct field or specific_allowances."""
            # First try to get from direct field
            if hasattr(salary_income, field_name):
                value = getattr(salary_income, field_name)
                if hasattr(value, 'to_float'):
                    return value.to_float()
                return float(value) if value is not None else default
            
            # Then try to get from specific_allowances
            if hasattr(salary_income, 'specific_allowances') and salary_income.specific_allowances:
                if hasattr(salary_income.specific_allowances, field_name):
                    value = getattr(salary_income.specific_allowances, field_name)
                    if hasattr(value, 'to_float'):
                        return value.to_float()
                    return float(value) if value is not None else default
            
            return default
            
        return SalaryIncomeDTO(
            basic_salary=salary_income.basic_salary.to_float() if hasattr(salary_income.basic_salary, 'to_float') else float(salary_income.basic_salary),
            dearness_allowance=salary_income.dearness_allowance.to_float() if hasattr(salary_income.dearness_allowance, 'to_float') else float(salary_income.dearness_allowance),
            hra_received=salary_income.hra_received.to_float() if hasattr(salary_income.hra_received, 'to_float') else float(salary_income.hra_received),
            hra_city_type=getattr(salary_income, 'hra_city_type', 'non_metro'),
            actual_rent_paid=salary_income.actual_rent_paid.to_float() if hasattr(salary_income, 'actual_rent_paid') and hasattr(salary_income.actual_rent_paid, 'to_float') else 0,
            bonus=salary_income.bonus.to_float() if hasattr(salary_income.bonus, 'to_float') else float(salary_income.bonus),
            commission=salary_income.commission.to_float() if hasattr(salary_income.commission, 'to_float') else float(salary_income.commission),
            special_allowance=salary_income.special_allowance.to_float() if hasattr(salary_income.special_allowance, 'to_float') else float(salary_income.special_allowance),
            # Additional allowances - try both direct fields and specific_allowances
            city_compensatory_allowance=get_allowance_value('city_compensatory_allowance'),
            rural_allowance=get_allowance_value('rural_allowance'),
            proctorship_allowance=get_allowance_value('proctorship_allowance'),
            wardenship_allowance=get_allowance_value('wardenship_allowance'),
            project_allowance=get_allowance_value('project_allowance'),
            deputation_allowance=get_allowance_value('deputation_allowance'),
            interim_relief=get_allowance_value('interim_relief'),
            tiffin_allowance=get_allowance_value('tiffin_allowance'),
            overtime_allowance=get_allowance_value('overtime_allowance'),
            servant_allowance=get_allowance_value('servant_allowance'),
            hills_high_altd_allowance=get_allowance_value('hills_allowance'),  # Note: different field name in entity
            hills_high_altd_exemption_limit=get_allowance_value('hills_exemption_limit'),  # Note: different field name in entity
            border_remote_allowance=get_allowance_value('border_allowance'),  # Note: different field name in entity
            border_remote_exemption_limit=get_allowance_value('border_exemption_limit'),  # Note: different field name in entity
            transport_employee_allowance=get_allowance_value('transport_employee_allowance'),
            children_education_allowance=get_allowance_value('children_education_allowance'),
            children_education_count=get_allowance_value('children_count'),  # Note: different field name in entity
            children_education_months=get_allowance_value('children_education_months'),
            hostel_allowance=get_allowance_value('hostel_allowance'),
            hostel_count=get_allowance_value('hostel_count'),
            hostel_months=get_allowance_value('hostel_months'),
            transport_months=get_allowance_value('transport_months'),
            underground_mines_allowance=get_allowance_value('underground_mines_allowance'),
            underground_mines_months=get_allowance_value('mine_work_months'),  # Note: different field name in entity
            govt_employee_entertainment_allowance=get_allowance_value('government_entertainment_allowance'),  # Note: different field name in entity
            govt_employees_outside_india_allowance=get_allowance_value('govt_employees_outside_india_allowance'),
            supreme_high_court_judges_allowance=get_allowance_value('supreme_high_court_judges_allowance'),
            judge_compensatory_allowance=get_allowance_value('judge_compensatory_allowance'),
            section_10_14_special_allowances=get_allowance_value('section_10_14_special_allowances'),
            travel_on_tour_allowance=get_allowance_value('travel_on_tour_allowance'),
            tour_daily_charge_allowance=get_allowance_value('tour_daily_charge_allowance'),
            conveyance_in_performace_of_duties=get_allowance_value('conveyance_in_performace_of_duties'),
            helper_in_performace_of_duties=get_allowance_value('helper_in_performace_of_duties'),
            academic_research=get_allowance_value('academic_research'),
            uniform_allowance=get_allowance_value('uniform_allowance'),
            any_other_allowance_exemption=get_allowance_value('any_other_allowance_exemption')
        )
    
    def _convert_periodic_salary_entity_to_dto(self, periodic_salary):
        """Convert PeriodicSalaryIncome entity to PeriodicSalaryIncomeDTO."""
        from app.application.dto.taxation_dto import PeriodicSalaryIncomeDTO, PeriodicSalaryDataDTO, EmploymentPeriodDTO
        
        if not periodic_salary or not hasattr(periodic_salary, 'periods'):
            return None
            
        periods_dto = []
        for period_data in periodic_salary.periods:
            period_dto = EmploymentPeriodDTO(
                start_date=period_data.period.start_date if hasattr(period_data, 'period') else period_data.start_date,
                end_date=period_data.period.end_date if hasattr(period_data, 'period') else period_data.end_date,
                description=period_data.period.description if hasattr(period_data, 'period') else getattr(period_data, 'description', '')
            )
            
            salary_income = period_data.salary_income if hasattr(period_data, 'salary_income') else period_data
            salary_data_dto = PeriodicSalaryDataDTO(
                period=period_dto,
                basic_salary=salary_income.basic_salary.to_float() if hasattr(salary_income.basic_salary, 'to_float') else float(salary_income.basic_salary),
                dearness_allowance=salary_income.dearness_allowance.to_float() if hasattr(salary_income.dearness_allowance, 'to_float') else float(salary_income.dearness_allowance),
                hra_received=salary_income.hra_received.to_float() if hasattr(salary_income.hra_received, 'to_float') else float(salary_income.hra_received),
                hra_city_type=getattr(salary_income, 'hra_city_type', 'non_metro'),
                actual_rent_paid=salary_income.actual_rent_paid.to_float() if hasattr(salary_income, 'actual_rent_paid') and hasattr(salary_income.actual_rent_paid, 'to_float') else 0,
                special_allowance=salary_income.special_allowance.to_float() if hasattr(salary_income.special_allowance, 'to_float') else float(salary_income.special_allowance),
                bonus=salary_income.bonus.to_float() if hasattr(salary_income.bonus, 'to_float') else float(salary_income.bonus),
                commission=salary_income.commission.to_float() if hasattr(salary_income.commission, 'to_float') else float(salary_income.commission),
            )
            
            periods_dto.append(salary_data_dto)
        
        return PeriodicSalaryIncomeDTO(periods=periods_dto)
    
    def _convert_perquisites_entity_to_dto(self, perquisites):
        """Convert Perquisites entity to PerquisitesDTO."""
        from app.application.dto.taxation_dto import PerquisitesDTO
        
        if not perquisites:
            return None
            
        # For now, return a basic PerquisitesDTO with available fields
        # This would need to be expanded based on the actual perquisites entity structure
        return PerquisitesDTO(
            # Basic perquisite values - these would need to be mapped from the actual entity
            accommodation=None,  # Would need proper conversion
            car=None,  # Would need proper conversion
            medical_reimbursement=None,  # Would need proper conversion
            lta=None,  # Would need proper conversion
            interest_free_loan=None,  # Would need proper conversion
            esop=None,  # Would need proper conversion
            utilities=None,  # Would need proper conversion
            free_education=None,  # Would need proper conversion
            movable_asset_usage=None,  # Would need proper conversion
            movable_asset_transfer=None,  # Would need proper conversion
            lunch_refreshment=None,  # Would need proper conversion
            gift_voucher=None,  # Would need proper conversion
            monetary_benefits=None,  # Would need proper conversion
            club_expenses=None,  # Would need proper conversion
            domestic_help=None  # Would need proper conversion
        )
    
    def _convert_house_property_entity_to_dto(self, house_property):
        """Convert HousePropertyIncome entity to HousePropertyIncomeDTO."""
        from app.application.dto.taxation_dto import HousePropertyIncomeDTO
        
        if not house_property:
            return None
        
        # Map property type from entity format to DTO format
        property_type_mapping = {
            'self_occupied': 'Self-Occupied',
            'let_out': 'Let-Out', 
            'deemed_let_out': 'Deemed Let-Out',
            'Self-Occupied': 'Self-Occupied',  # Already correct format
            'Let-Out': 'Let-Out',  # Already correct format
            'Deemed Let-Out': 'Deemed Let-Out'  # Already correct format
        }
        
        raw_property_type = getattr(house_property, 'property_type', 'self_occupied')
        property_type = property_type_mapping.get(raw_property_type, 'Self-Occupied')
            
        return HousePropertyIncomeDTO(
            property_type=property_type,
            annual_rent_received=house_property.annual_rent_received.to_float() if hasattr(house_property, 'annual_rent_received') and hasattr(house_property.annual_rent_received, 'to_float') else 0,
            municipal_taxes_paid=house_property.municipal_taxes_paid.to_float() if hasattr(house_property, 'municipal_taxes_paid') and hasattr(house_property.municipal_taxes_paid, 'to_float') else 0,
            home_loan_interest=house_property.home_loan_interest.to_float() if hasattr(house_property, 'home_loan_interest') and hasattr(house_property.home_loan_interest, 'to_float') else 0,
            pre_construction_interest=house_property.pre_construction_interest.to_float() if hasattr(house_property, 'pre_construction_interest') and hasattr(house_property.pre_construction_interest, 'to_float') else 0
        )
    
    def _convert_retirement_benefits_entity_to_dto(self, retirement_benefits):
        """Convert RetirementBenefits entity to RetirementBenefitsDTO."""
        from app.application.dto.taxation_dto import (
            RetirementBenefitsDTO, LeaveEncashmentDTO, GratuityDTO, 
            VRSDTO, PensionDTO, RetrenchmentCompensationDTO
        )
        
        if not retirement_benefits:
            return None
        
        # Convert leave encashment
        leave_encashment = None
        if hasattr(retirement_benefits, 'leave_encashment') and retirement_benefits.leave_encashment:
            # Handle nested LeaveEncashment object
            if hasattr(retirement_benefits.leave_encashment, 'leave_encashment_amount'):
                leave_encashment_amount = retirement_benefits.leave_encashment.leave_encashment_amount.to_float()
                leave_days_encashed = getattr(retirement_benefits.leave_encashment, 'leave_days_encashed', 0)
                is_govt_employee = getattr(retirement_benefits.leave_encashment, 'is_govt_employee', False)
            else:
                # Fallback for backward compatibility
                leave_encashment_amount = retirement_benefits.leave_encashment.to_float() if hasattr(retirement_benefits.leave_encashment, 'to_float') else 0
                leave_days_encashed = getattr(retirement_benefits, 'leave_days_encashed', 0)
                is_govt_employee = getattr(retirement_benefits, 'is_govt_employee', False)
            
            leave_encashment = LeaveEncashmentDTO(
                leave_encashment_amount=leave_encashment_amount,
                average_monthly_salary=getattr(retirement_benefits, 'average_monthly_salary', 0),
                leave_days_encashed=leave_days_encashed,
                is_govt_employee=is_govt_employee,
                during_employment=getattr(retirement_benefits, 'during_employment', False)
            )
        elif hasattr(retirement_benefits, 'leave_encashment_amount') and retirement_benefits.leave_encashment_amount:
            leave_encashment_amount = retirement_benefits.leave_encashment_amount.to_float() if hasattr(retirement_benefits.leave_encashment_amount, 'to_float') else float(retirement_benefits.leave_encashment_amount)
            if leave_encashment_amount > 0:
                leave_encashment = LeaveEncashmentDTO(
                    leave_encashment_amount=leave_encashment_amount,
                    average_monthly_salary=getattr(retirement_benefits, 'average_monthly_salary', 0),
                    leave_days_encashed=getattr(retirement_benefits, 'leave_days_encashed', 0),
                    is_govt_employee=getattr(retirement_benefits, 'is_govt_employee', False),
                    during_employment=getattr(retirement_benefits, 'during_employment', False)
                )
        
        # Convert gratuity
        gratuity = None
        if hasattr(retirement_benefits, 'gratuity') and retirement_benefits.gratuity:
            # Handle nested Gratuity object
            if hasattr(retirement_benefits.gratuity, 'gratuity_amount'):
                gratuity_amount = retirement_benefits.gratuity.gratuity_amount.to_float()
                service_years = float(retirement_benefits.gratuity.service_years) if hasattr(retirement_benefits.gratuity, 'service_years') else 0
                is_govt_employee = getattr(retirement_benefits.gratuity, 'is_govt_employee', False)
            else:
                # Fallback for backward compatibility
                gratuity_amount = retirement_benefits.gratuity.to_float() if hasattr(retirement_benefits.gratuity, 'to_float') else 0
                service_years = getattr(retirement_benefits, 'service_years', 0)
                is_govt_employee = getattr(retirement_benefits, 'is_govt_employee', False)
            
            gratuity = GratuityDTO(
                gratuity_amount=gratuity_amount,
                monthly_salary=getattr(retirement_benefits, 'monthly_salary', 0),
                service_years=service_years,
                is_govt_employee=is_govt_employee
            )
        elif hasattr(retirement_benefits, 'gratuity_amount') and retirement_benefits.gratuity_amount:
            gratuity_amount = retirement_benefits.gratuity_amount.to_float() if hasattr(retirement_benefits.gratuity_amount, 'to_float') else float(retirement_benefits.gratuity_amount)
            if gratuity_amount > 0:
                gratuity = GratuityDTO(
                    gratuity_amount=gratuity_amount,
                    monthly_salary=getattr(retirement_benefits, 'monthly_salary', 0),
                    service_years=getattr(retirement_benefits, 'service_years', 0),
                    is_govt_employee=getattr(retirement_benefits, 'is_govt_employee', False)
                )
        
        # Convert VRS
        vrs = None
        if hasattr(retirement_benefits, 'vrs') and retirement_benefits.vrs:
            # Handle nested VRS object
            if hasattr(retirement_benefits.vrs, 'vrs_amount'):
                vrs_amount = retirement_benefits.vrs.vrs_amount.to_float()
            else:
                # Fallback for backward compatibility
                vrs_amount = retirement_benefits.vrs.to_float() if hasattr(retirement_benefits.vrs, 'to_float') else 0
            
            vrs = VRSDTO(
                vrs_amount=vrs_amount,
                monthly_salary=getattr(retirement_benefits, 'monthly_salary', 0),
                age=getattr(retirement_benefits, 'age', 30),
                service_years=getattr(retirement_benefits, 'service_years', 0)
            )
        elif hasattr(retirement_benefits, 'vrs_amount') and retirement_benefits.vrs_amount:
            vrs_amount = retirement_benefits.vrs_amount.to_float() if hasattr(retirement_benefits.vrs_amount, 'to_float') else float(retirement_benefits.vrs_amount)
            if vrs_amount > 0:
                vrs = VRSDTO(
                    vrs_amount=vrs_amount,
                    monthly_salary=getattr(retirement_benefits, 'monthly_salary', 0),
                    age=getattr(retirement_benefits, 'age', 30),
                    service_years=getattr(retirement_benefits, 'service_years', 0)
                )
        
        # Convert pension
        pension = None
        if hasattr(retirement_benefits, 'pension') and retirement_benefits.pension:
            # Handle nested Pension object
            if hasattr(retirement_benefits.pension, 'total_pension'):
                pension_amount = retirement_benefits.pension.total_pension.to_float()
                regular_pension = retirement_benefits.pension.regular_pension.to_float() if hasattr(retirement_benefits.pension, 'regular_pension') else pension_amount
                commuted_pension = retirement_benefits.pension.commuted_pension.to_float() if hasattr(retirement_benefits.pension, 'commuted_pension') else 0
                is_govt_employee = getattr(retirement_benefits.pension, 'is_govt_employee', False)
            else:
                # Fallback for backward compatibility
                pension_amount = retirement_benefits.pension.to_float() if hasattr(retirement_benefits.pension, 'to_float') else 0
                regular_pension = pension_amount
                commuted_pension = 0
                is_govt_employee = getattr(retirement_benefits, 'is_govt_employee', False)
            
            pension = PensionDTO(
                regular_pension=regular_pension,
                commuted_pension=commuted_pension,
                total_pension=pension_amount,
                is_govt_employee=is_govt_employee,
                gratuity_received=getattr(retirement_benefits, 'gratuity_received', False)
            )
        elif hasattr(retirement_benefits, 'pension_amount') and retirement_benefits.pension_amount:
            pension_amount = retirement_benefits.pension_amount.to_float() if hasattr(retirement_benefits.pension_amount, 'to_float') else float(retirement_benefits.pension_amount)
            if pension_amount > 0:
                pension = PensionDTO(
                    regular_pension=pension_amount,
                    commuted_pension=getattr(retirement_benefits, 'commuted_pension', 0),
                    total_pension=pension_amount,
                    is_govt_employee=getattr(retirement_benefits, 'is_govt_employee', False),
                    gratuity_received=getattr(retirement_benefits, 'gratuity_received', False)
                )
        
        # Convert retrenchment compensation
        retrenchment_compensation = None
        if hasattr(retirement_benefits, 'retrenchment_compensation') and retirement_benefits.retrenchment_compensation:
            # Handle nested RetrenchmentCompensation object
            if hasattr(retirement_benefits.retrenchment_compensation, 'compensation_amount'):
                retrenchment_amount = retirement_benefits.retrenchment_compensation.compensation_amount.to_float()
            else:
                # Fallback for backward compatibility
                retrenchment_amount = retirement_benefits.retrenchment_compensation.to_float() if hasattr(retirement_benefits.retrenchment_compensation, 'to_float') else 0
            
            retrenchment_compensation = RetrenchmentCompensationDTO(
                retrenchment_amount=retrenchment_amount,
                monthly_salary=getattr(retirement_benefits, 'monthly_salary', 0),
                service_years=getattr(retirement_benefits, 'service_years', 0)
            )
        
        # Only return RetirementBenefitsDTO if at least one component has data
        if any([leave_encashment, gratuity, vrs, pension, retrenchment_compensation]):
            return RetirementBenefitsDTO(
                leave_encashment=leave_encashment,
                gratuity=gratuity,
                vrs=vrs,
                pension=pension,
                retrenchment_compensation=retrenchment_compensation
            )
        
        return None
    
    def _convert_other_income_entity_to_dto(self, other_income):
        """Convert OtherIncome entity to OtherIncomeDTO."""
        from app.application.dto.taxation_dto import OtherIncomeDTO, InterestIncomeDTO, HousePropertyIncomeDTO, CapitalGainsIncomeDTO
        
        if not other_income:
            return None
        
        # Convert interest income
        interest_income_dto = None
        if other_income.interest_income:
            interest_income_dto = InterestIncomeDTO(
                savings_account_interest=other_income.interest_income.savings_account_interest.to_float() if hasattr(other_income.interest_income.savings_account_interest, 'to_float') else 0,
                fixed_deposit_interest=other_income.interest_income.fixed_deposit_interest.to_float() if hasattr(other_income.interest_income.fixed_deposit_interest, 'to_float') else 0,
                recurring_deposit_interest=other_income.interest_income.recurring_deposit_interest.to_float() if hasattr(other_income.interest_income.recurring_deposit_interest, 'to_float') else 0,
                post_office_interest=other_income.interest_income.post_office_interest.to_float() if hasattr(other_income.interest_income.post_office_interest, 'to_float') else 0
            )
        
        # Convert house property income
        house_property_dto = None
        if other_income.house_property_income:
            house_property_dto = self._convert_house_property_entity_to_dto(other_income.house_property_income)
        
        # Convert capital gains income
        capital_gains_dto = None
        if other_income and other_income.capital_gains_income:
            capital_gains = other_income.capital_gains_income
            capital_gains_dto = CapitalGainsIncomeDTO(
                stcg_111a_equity_stt=capital_gains.stcg_111a_equity_stt.to_float(),
                stcg_other_assets=capital_gains.stcg_other_assets.to_float(),
                stcg_debt_mf=capital_gains.stcg_debt_mf.to_float(),
                ltcg_112a_equity_stt=capital_gains.ltcg_112a_equity_stt.to_float(),
                ltcg_other_assets=capital_gains.ltcg_other_assets.to_float(),
                ltcg_debt_mf=capital_gains.ltcg_debt_mf.to_float()
            )
        
        return OtherIncomeDTO(
            interest_income=interest_income_dto,
            house_property_income=house_property_dto,
            capital_gains_income=capital_gains_dto,
            dividend_income=other_income.dividend_income.to_float() if hasattr(other_income.dividend_income, 'to_float') else 0,
            gifts_received=other_income.gifts_received.to_float() if hasattr(other_income.gifts_received, 'to_float') else 0,
            business_professional_income=other_income.business_professional_income.to_float() if hasattr(other_income.business_professional_income, 'to_float') else 0,
            other_miscellaneous_income=other_income.other_miscellaneous_income.to_float() if hasattr(other_income.other_miscellaneous_income, 'to_float') else 0
        )
    
    def _convert_monthly_payroll_entity_to_dto(self, monthly_payroll):
        """Convert PayoutMonthlyProjection entity to PayoutMonthlyProjectionDTO."""
        from app.application.dto.taxation_dto import PayoutMonthlyProjectionDTO
        
        if not monthly_payroll:
            return None
            
        # Convert PayoutMonthlyProjection to PayoutMonthlyProjectionDTO
        return PayoutMonthlyProjectionDTO(
            employee_id=monthly_payroll.employee_id,
            month=monthly_payroll.pay_period_start.month if hasattr(monthly_payroll, 'pay_period_start') else 1,
            year=monthly_payroll.pay_period_start.year if hasattr(monthly_payroll, 'pay_period_start') else 2024,
            
            # Salary components
            basic_salary=monthly_payroll.basic_salary,
            da=monthly_payroll.da,
            hra=monthly_payroll.hra,
            special_allowance=monthly_payroll.special_allowance,
            bonus=monthly_payroll.bonus,
            commission=monthly_payroll.commission,
            
            # Deductions
            epf_employee=monthly_payroll.epf_employee,
            esi_employee=monthly_payroll.esi_employee,
            professional_tax=monthly_payroll.professional_tax,
            advance_deduction=monthly_payroll.advance_deduction,
            loan_deduction=monthly_payroll.loan_deduction,
            other_deductions=monthly_payroll.other_deductions,
            
            # Calculated totals
            gross_salary=monthly_payroll.gross_salary,
            net_salary=monthly_payroll.net_salary,
            total_deductions=monthly_payroll.total_deductions,
            tds=monthly_payroll.tds,
            
            # Annual projections
            annual_gross_salary=monthly_payroll.annual_gross_salary,
            annual_tax_liability=monthly_payroll.annual_tax_liability,
            
            # Tax details
            tax_regime=monthly_payroll.tax_regime,
            
            # Working days
            effective_working_days=monthly_payroll.effective_working_days,
            lwp_days=monthly_payroll.lwp_days,
            
            # Status
            status=monthly_payroll.status,
            notes=monthly_payroll.notes,
            remarks=getattr(monthly_payroll, 'remarks', None)
        )
    
    def _convert_deductions_entity_to_dto(self, deductions):
        """Convert TaxDeductions entity to TaxDeductionsDTO."""
        from app.application.dto.taxation_dto import TaxDeductionsDTO, DeductionSection80CDTO, DeductionSection80DDTO, DeductionSection80GDTO, DeductionSection80EDTO, DeductionSection80TTADTO, OtherDeductionsDTO
        
        if not deductions:
            return None
            
        # Convert Section 80C
        section_80c = DeductionSection80CDTO(
            life_insurance_premium=deductions.life_insurance_premium.to_float() if hasattr(deductions.life_insurance_premium, 'to_float') else 0,
            epf_contribution=deductions.employee_provident_fund.to_float() if hasattr(deductions.employee_provident_fund, 'to_float') else 0,
            ppf_contribution=deductions.public_provident_fund.to_float() if hasattr(deductions.public_provident_fund, 'to_float') else 0,
            nsc_investment=deductions.national_savings_certificate.to_float() if hasattr(deductions.national_savings_certificate, 'to_float') else 0,
            tax_saving_fd=deductions.tax_saving_fixed_deposits.to_float() if hasattr(deductions.tax_saving_fixed_deposits, 'to_float') else 0,
            elss_investment=deductions.elss_investments.to_float() if hasattr(deductions.elss_investments, 'to_float') else 0,
            home_loan_principal=deductions.principal_repayment_home_loan.to_float() if hasattr(deductions.principal_repayment_home_loan, 'to_float') else 0,
            tuition_fees=deductions.tuition_fees.to_float() if hasattr(deductions.tuition_fees, 'to_float') else 0,
            sukanya_samriddhi=deductions.sukanya_samriddhi.to_float() if hasattr(deductions.sukanya_samriddhi, 'to_float') else 0,
            other_80c_investments=deductions.other_80c_deductions.to_float() if hasattr(deductions.other_80c_deductions, 'to_float') else 0
        )
        
        # Convert Section 80D
        section_80d = DeductionSection80DDTO(
            self_family_premium=deductions.health_insurance_self.to_float() if hasattr(deductions.health_insurance_self, 'to_float') else 0,
            parent_premium=deductions.health_insurance_parents.to_float() if hasattr(deductions.health_insurance_parents, 'to_float') else 0,
            preventive_health_checkup=deductions.preventive_health_checkup.to_float() if hasattr(deductions.preventive_health_checkup, 'to_float') else 0,
            employee_age=30,  # Default age, would need to be passed from context
            parent_age=60  # Default parent age
        )
        
        # Convert Section 80G
        section_80g = DeductionSection80GDTO(
            charitable_donations=deductions.donations_80g.to_float() if hasattr(deductions.donations_80g, 'to_float') else 0
        )
        
        # Convert Section 80E
        section_80e = DeductionSection80EDTO(
            education_loan_interest=deductions.education_loan_interest.to_float() if hasattr(deductions.education_loan_interest, 'to_float') else 0
        )
        
        # Convert Section 80TTA
        section_80tta_ttb = DeductionSection80TTADTO(
            savings_interest=deductions.savings_account_interest.to_float() if hasattr(deductions.savings_account_interest, 'to_float') else 0,
            senior_citizen_interest=deductions.senior_citizen_interest.to_float() if hasattr(deductions.senior_citizen_interest, 'to_float') else 0,
            employee_age=30  # Default age, would need to be passed from context
        )
        
        # Convert Other Deductions
        other_deductions = OtherDeductionsDTO(
            education_loan_interest=deductions.education_loan_interest.to_float() if hasattr(deductions.education_loan_interest, 'to_float') else 0,
            charitable_donations=deductions.donations_80g.to_float() if hasattr(deductions.donations_80g, 'to_float') else 0,
            savings_interest=deductions.savings_account_interest.to_float() if hasattr(deductions.savings_account_interest, 'to_float') else 0
        )
        
        return TaxDeductionsDTO(
            section_80c=section_80c,
            section_80d=section_80d,
            section_80g=section_80g,
            section_80e=section_80e,
            section_80tta_ttb=section_80tta_ttb,
            other_deductions=other_deductions
        ) 