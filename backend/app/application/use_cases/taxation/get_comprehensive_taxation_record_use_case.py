"""
Use case for getting comprehensive taxation record by employee ID.
Handles fetching detailed taxation records and creating default records with computed values.
"""

from typing import Optional
from datetime import datetime, date
import logging

from app.application.dto.taxation_dto import ComprehensiveTaxOutputDTO
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
            # Determine financial year
            financial_year = self._get_financial_year(tax_year)
            
            # Get taxation record from repository
            taxation_record = await self._taxation_repository.get_taxation_record(
                employee_id=employee_id,
                financial_year=financial_year,
                organisation_id=organization_id
            )
            
            if taxation_record:
                # Convert existing domain entity to DTO
                return await self._convert_to_comprehensive_dto(taxation_record, employee_id, organization_id, tax_year or self._get_current_tax_year())
            else:
                # Create default record with computed values
                return await self._create_default_comprehensive_record(employee_id, organization_id, tax_year or self._get_current_tax_year())
                
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
        
        # Convert existing record to comprehensive DTO
        # For now, we'll create a basic structure with existing data
        return ComprehensiveTaxOutputDTO(
            tax_year=tax_year,
            regime_type=regime,
            age=age,
            is_govt_employee=is_govt_employee,
            employee_id=employee_id,
            # All income sources will be None for existing records until we have proper conversion
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