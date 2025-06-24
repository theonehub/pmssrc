"""
Declare Personal Investments Use Case
Employee use case to declare personal investments and deductions
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.entities.taxation.employee_declarations.personal_investments import (
    PersonalInvestmentDeclaration
)
from app.application.interfaces.repositories.taxation_repository import TaxationRepository


@dataclass
class DeclarePersonalInvestmentsCommand:
    """Command to declare personal investments."""
    
    employee_id: str
    organization_id: str
    tax_year: str
    
    # Section 80C investments
    section_80c_investments: Dict[str, float] = None
    
    # Health insurance declarations
    health_insurance_declarations: Dict[str, Any] = None
    
    # NPS declarations
    nps_declarations: Dict[str, float] = None
    
    # Education loan interest
    education_loan_interest: float = 0.0
    
    # Charitable donations
    charitable_donations: Dict[str, float] = None
    
    # EV loan declarations
    ev_loan_declarations: Dict[str, Any] = None
    
    # Disability declarations
    disability_declarations: Dict[str, Any] = None
    
    # Medical treatment declarations
    medical_treatment_declarations: Dict[str, Any] = None
    
    # Interest income declarations
    interest_income_declarations: Dict[str, float] = None
    
    # Other investments
    other_investment_declarations: Dict[str, float] = None


@dataclass
class PersonalInvestmentDeclarationResponse:
    """Response for personal investment declaration."""
    
    success: bool
    declaration_id: str
    message: str
    validation_warnings: List[str]
    investment_summary: Dict[str, Any]


class DeclarePersonalInvestmentsUseCase:
    """
    Use case for employees to declare personal investments.
    Uses existing TaxDeductions computation logic without changes.
    """
    
    def __init__(self, taxation_repository: TaxationRepository):
        self._taxation_repository = taxation_repository
    
    async def execute(self, command: DeclarePersonalInvestmentsCommand) -> PersonalInvestmentDeclarationResponse:
        """
        Process employee personal investment declaration.
        
        Args:
            command: Declaration command
            
        Returns:
            PersonalInvestmentDeclarationResponse: Declaration result
        """
        
        try:
            # Create employee investment declaration entity
            investment_declaration = PersonalInvestmentDeclaration(
                employee_id=EmployeeId(command.employee_id),
                organization_id=command.organization_id,
                tax_year=command.tax_year,
                section_80c_investments=command.section_80c_investments or {},
                health_insurance_declarations=command.health_insurance_declarations or {},
                nps_declarations=command.nps_declarations or {},
                education_loan_interest=command.education_loan_interest,
                charitable_donations=command.charitable_donations or {},
                ev_loan_declarations=command.ev_loan_declarations or {},
                disability_declarations=command.disability_declarations or {},
                medical_treatment_declarations=command.medical_treatment_declarations or {},
                interest_income_declarations=command.interest_income_declarations or {},
                other_investment_declarations=command.other_investment_declarations or {},
                declared_by=command.employee_id
            )
            
            # Validate declaration using entity logic
            validation_warnings = investment_declaration.validate_declaration()
            
            # Test creation of TaxDeductions to ensure computation logic works
            # This uses existing TaxDeductions entity - NO COMPUTATION CHANGES
            tax_deductions = investment_declaration.create_tax_deductions()
            
            # Save declaration (repository handles persistence)
            declaration_id = await self._taxation_repository.save_personal_investment_declaration(investment_declaration)
            
            # Get summary for response
            investment_summary = investment_declaration.get_investment_summary()
            
            return PersonalInvestmentDeclarationResponse(
                success=True,
                declaration_id=declaration_id,
                message="Personal investment declaration saved successfully",
                validation_warnings=validation_warnings,
                investment_summary=investment_summary
            )
            
        except Exception as e:
            return PersonalInvestmentDeclarationResponse(
                success=False,
                declaration_id="",
                message=f"Failed to save investment declaration: {str(e)}",
                validation_warnings=[],
                investment_summary={}
            )


@dataclass
class UpdateInvestmentCommand:
    """Command to update specific investment."""
    
    employee_id: str
    organization_id: str
    tax_year: str
    investment_type: str
    investment_section: str  # '80c', '80d', 'nps', etc.
    amount: float


class UpdateSpecificInvestmentUseCase:
    """Use case to update specific investment amount."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self._taxation_repository = taxation_repository
    
    async def execute(self, command: UpdateInvestmentCommand) -> PersonalInvestmentDeclarationResponse:
        """
        Update specific investment amount.
        
        Args:
            command: Update command
            
        Returns:
            PersonalInvestmentDeclarationResponse: Update result
        """
        
        try:
            # Get existing declaration
            investment_declaration = await self._taxation_repository.get_personal_investment_declaration(
                EmployeeId(command.employee_id),
                command.organization_id,
                command.tax_year
            )
            
            if not investment_declaration:
                # Create new declaration if doesn't exist
                investment_declaration = PersonalInvestmentDeclaration(
                    employee_id=EmployeeId(command.employee_id),
                    organization_id=command.organization_id,
                    tax_year=command.tax_year,
                    declared_by=command.employee_id
                )
            
            # Update specific investment using entity methods
            success = False
            if command.investment_section == '80c':
                success = investment_declaration.update_section_80c_investment(
                    command.investment_type, command.amount
                )
            elif command.investment_section == '80d':
                success = investment_declaration.update_health_insurance({
                    command.investment_type: command.amount
                })
            # Add other sections as needed
            
            if not success:
                return PersonalInvestmentDeclarationResponse(
                    success=False,
                    declaration_id="",
                    message=f"Invalid investment type: {command.investment_type}",
                    validation_warnings=[],
                    investment_summary={}
                )
            
            # Save updated declaration
            declaration_id = await self._taxation_repository.save_personal_investment_declaration(investment_declaration)
            
            return PersonalInvestmentDeclarationResponse(
                success=True,
                declaration_id=declaration_id,
                message=f"Investment updated: {command.investment_type}",
                validation_warnings=investment_declaration.validate_declaration(),
                investment_summary=investment_declaration.get_investment_summary()
            )
            
        except Exception as e:
            return PersonalInvestmentDeclarationResponse(
                success=False,
                declaration_id="",
                message=f"Failed to update investment: {str(e)}",
                validation_warnings=[],
                investment_summary={}
            )


@dataclass
class SubmitDeclarationCommand:
    """Command to submit declaration for approval."""
    
    employee_id: str
    organization_id: str
    tax_year: str


class SubmitInvestmentDeclarationUseCase:
    """Use case to submit investment declaration for approval."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self._taxation_repository = taxation_repository
    
    async def execute(self, command: SubmitDeclarationCommand) -> PersonalInvestmentDeclarationResponse:
        """
        Submit investment declaration for approval.
        
        Args:
            command: Submit command
            
        Returns:
            PersonalInvestmentDeclarationResponse: Submit result
        """
        
        try:
            # Get declaration
            investment_declaration = await self._taxation_repository.get_personal_investment_declaration(
                EmployeeId(command.employee_id),
                command.organization_id,
                command.tax_year
            )
            
            if not investment_declaration:
                return PersonalInvestmentDeclarationResponse(
                    success=False,
                    declaration_id="",
                    message="Investment declaration not found",
                    validation_warnings=[],
                    investment_summary={}
                )
            
            # Submit declaration using entity logic
            success = investment_declaration.submit_declaration(command.employee_id)
            
            if not success:
                return PersonalInvestmentDeclarationResponse(
                    success=False,
                    declaration_id="",
                    message="Declaration cannot be submitted (not in draft status)",
                    validation_warnings=[],
                    investment_summary={}
                )
            
            # Save updated declaration
            declaration_id = await self._taxation_repository.save_personal_investment_declaration(investment_declaration)
            
            return PersonalInvestmentDeclarationResponse(
                success=True,
                declaration_id=declaration_id,
                message="Investment declaration submitted for approval",
                validation_warnings=investment_declaration.validate_declaration(),
                investment_summary=investment_declaration.get_investment_summary()
            )
            
        except Exception as e:
            return PersonalInvestmentDeclarationResponse(
                success=False,
                declaration_id="",
                message=f"Failed to submit declaration: {str(e)}",
                validation_warnings=[],
                investment_summary={}
            )


@dataclass
class GetInvestmentDeclarationQuery:
    """Query to get investment declaration."""
    
    employee_id: str
    organization_id: str
    tax_year: str


class GetPersonalInvestmentDeclarationUseCase:
    """Use case to get employee investment declaration."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self._taxation_repository = taxation_repository
    
    async def execute(self, query: GetInvestmentDeclarationQuery) -> PersonalInvestmentDeclarationResponse:
        """
        Get employee investment declaration.
        
        Args:
            query: Query parameters
            
        Returns:
            PersonalInvestmentDeclarationResponse: Declaration data
        """
        
        try:
            # Get declaration from repository
            investment_declaration = await self._taxation_repository.get_personal_investment_declaration(
                EmployeeId(query.employee_id),
                query.organization_id,
                query.tax_year
            )
            
            if not investment_declaration:
                # Return empty declaration structure
                return PersonalInvestmentDeclarationResponse(
                    success=True,
                    declaration_id="",
                    message="No declaration found - returning empty structure",
                    validation_warnings=[],
                    investment_summary={
                        "employee_info": {
                            "employee_id": query.employee_id,
                            "organization_id": query.organization_id,
                            "tax_year": query.tax_year
                        },
                        "declaration_status": "not_started"
                    }
                )
            
            return PersonalInvestmentDeclarationResponse(
                success=True,
                declaration_id=str(investment_declaration.employee_id),
                message="Investment declaration retrieved successfully",
                validation_warnings=investment_declaration.validate_declaration(),
                investment_summary=investment_declaration.get_investment_summary()
            )
            
        except Exception as e:
            return PersonalInvestmentDeclarationResponse(
                success=False,
                declaration_id="",
                message=f"Failed to get investment declaration: {str(e)}",
                validation_warnings=[],
                investment_summary={}
            )


@dataclass
class GetInvestmentOptionsQuery:
    """Query to get available investment options."""
    
    organization_id: str


class GetInvestmentOptionsUseCase:
    """Use case to get available investment options for declarations."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self._taxation_repository = taxation_repository
    
    async def execute(self, query: GetInvestmentOptionsQuery) -> PersonalInvestmentDeclarationResponse:
        """
        Get available investment options.
        
        Args:
            query: Query parameters
            
        Returns:
            PersonalInvestmentDeclarationResponse: Investment options data
        """
        
        try:
            # Define available investment options
            investment_options = {
                "section_80c": {
                    "epf": {"max_limit": 150000, "description": "Employee Provident Fund"},
                    "ppf": {"max_limit": 150000, "description": "Public Provident Fund"},
                    "elss": {"max_limit": 150000, "description": "ELSS Mutual Funds"},
                    "nsc": {"max_limit": 150000, "description": "National Savings Certificate"},
                    "tax_saver_fd": {"max_limit": 150000, "description": "Tax Saver Fixed Deposits"},
                    "life_insurance": {"max_limit": 150000, "description": "Life Insurance Premium"},
                    "ulip": {"max_limit": 150000, "description": "Unit Linked Insurance Plan"}
                },
                "section_80d": {
                    "self_family": {"max_limit": 25000, "description": "Self and Family Health Insurance"},
                    "parents": {"max_limit": 25000, "description": "Parents Health Insurance"},
                    "senior_parents": {"max_limit": 50000, "description": "Senior Citizen Parents"}
                },
                "section_80ccd": {
                    "nps_employer": {"max_limit": 150000, "description": "NPS Employer Contribution"},
                    "nps_additional": {"max_limit": 50000, "description": "Additional NPS Contribution"}
                },
                "other_sections": {
                    "section_80e": {"max_limit": None, "description": "Education Loan Interest"},
                    "section_80g": {"max_limit": None, "description": "Charitable Donations"},
                    "section_80tta": {"max_limit": 10000, "description": "Savings Account Interest"},
                    "section_80ttb": {"max_limit": 50000, "description": "Senior Citizen Interest"}
                }
            }
            
            return PersonalInvestmentDeclarationResponse(
                success=True,
                declaration_id="",
                message="Investment options retrieved successfully",
                validation_warnings=[],
                investment_summary={"investment_options": investment_options}
            )
            
        except Exception as e:
            return PersonalInvestmentDeclarationResponse(
                success=False,
                declaration_id="",
                message=f"Failed to get investment options: {str(e)}",
                validation_warnings=[],
                investment_summary={}
            ) 