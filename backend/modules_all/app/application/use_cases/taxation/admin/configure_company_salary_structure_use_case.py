"""
Configure Company Salary Structure Use Case
Admin use case to configure company-wide salary structure and policies
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List

from app.domain.value_objects.money import Money
from app.domain.entities.taxation.company_configuration.salary_structure import (
    CompanySalaryStructure, EmployeeSalaryAssignment
)
from app.application.interfaces.repositories.taxation_repository import TaxationRepository


@dataclass
class ConfigureCompanySalaryStructureCommand:
    """Command to configure company salary structure."""
    
    organization_id: str
    structure_name: str
    effective_from_date: str
    admin_user_id: str
    
    # Default salary components
    default_basic_salary: float = 0.0
    default_dearness_allowance: float = 0.0
    default_special_allowance: float = 0.0
    
    # HRA policy configuration
    hra_policy: Dict[str, Any] = None
    
    # Allowance policies (40+ allowances from existing system)
    allowance_policies: Dict[str, float] = None
    
    # Company settings
    perquisites_enabled: bool = True


@dataclass
class CompanySalaryStructureResponse:
    """Response for company salary structure configuration."""
    
    success: bool
    structure_id: str
    message: str
    validation_warnings: List[str]
    structure_summary: Dict[str, Any]


class ConfigureCompanySalaryStructureUseCase:
    """
    Use case for admins to configure company salary structure.
    Uses existing salary computation logic without changes.
    """
    
    def __init__(self, taxation_repository: TaxationRepository):
        self._taxation_repository = taxation_repository
    
    async def execute(self, command: ConfigureCompanySalaryStructureCommand) -> CompanySalaryStructureResponse:
        """
        Configure company salary structure.
        
        Args:
            command: Configuration command
            
        Returns:
            CompanySalaryStructureResponse: Configuration result
        """
        
        try:
            # Create company salary structure entity
            salary_structure = CompanySalaryStructure(
                organization_id=command.organization_id,
                structure_name=command.structure_name,
                effective_from_date=command.effective_from_date,
                default_basic_salary=Money.from_float(command.default_basic_salary),
                default_dearness_allowance=Money.from_float(command.default_dearness_allowance),
                default_special_allowance=Money.from_float(command.default_special_allowance),
                company_hra_policy=command.hra_policy or {},
                company_allowance_policies={
                    name: Money.from_float(amount) 
                    for name, amount in (command.allowance_policies or {}).items()
                },
                company_perquisites_enabled=command.perquisites_enabled,
                created_by=command.admin_user_id,
                updated_by=command.admin_user_id
            )
            
            # Validate structure
            validation_warnings = salary_structure.validate_structure()
            
            # Save structure (repository handles persistence)
            structure_id = await self._taxation_repository.save_company_salary_structure(salary_structure)
            
            # Get structure summary for response
            structure_summary = salary_structure.get_company_allowance_structure()
            
            return CompanySalaryStructureResponse(
                success=True,
                structure_id=structure_id,
                message="Company salary structure configured successfully",
                validation_warnings=validation_warnings,
                structure_summary=structure_summary
            )
            
        except Exception as e:
            return CompanySalaryStructureResponse(
                success=False,
                structure_id="",
                message=f"Failed to configure salary structure: {str(e)}",
                validation_warnings=[],
                structure_summary={}
            )


@dataclass
class UpdateAllowancePolicyCommand:
    """Command to update specific allowance policy."""
    
    organization_id: str
    structure_id: str
    allowance_name: str
    allowance_amount: float
    admin_user_id: str


class UpdateAllowancePolicyUseCase:
    """Use case to update specific allowance policy."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self._taxation_repository = taxation_repository
    
    async def execute(self, command: UpdateAllowancePolicyCommand) -> CompanySalaryStructureResponse:
        """
        Update specific allowance policy.
        
        Args:
            command: Update command
            
        Returns:
            CompanySalaryStructureResponse: Update result
        """
        
        try:
            # Get existing structure
            salary_structure = await self._taxation_repository.get_company_salary_structure(
                command.organization_id, command.structure_id
            )
            
            if not salary_structure:
                return CompanySalaryStructureResponse(
                    success=False,
                    structure_id=command.structure_id,
                    message="Salary structure not found",
                    validation_warnings=[],
                    structure_summary={}
                )
            
            # Update allowance policy using existing entity logic
            success = salary_structure.update_allowance_policy(
                command.allowance_name,
                Money.from_float(command.allowance_amount)
            )
            
            if not success:
                return CompanySalaryStructureResponse(
                    success=False,
                    structure_id=command.structure_id,
                    message=f"Invalid allowance name: {command.allowance_name}",
                    validation_warnings=[],
                    structure_summary={}
                )
            
            # Update metadata
            salary_structure.updated_by = command.admin_user_id
            
            # Save updated structure
            await self._taxation_repository.save_company_salary_structure(salary_structure)
            
            return CompanySalaryStructureResponse(
                success=True,
                structure_id=command.structure_id,
                message=f"Allowance policy for {command.allowance_name} updated successfully",
                validation_warnings=salary_structure.validate_structure(),
                structure_summary=salary_structure.get_company_allowance_structure()
            )
            
        except Exception as e:
            return CompanySalaryStructureResponse(
                success=False,
                structure_id=command.structure_id,
                message=f"Failed to update allowance policy: {str(e)}",
                validation_warnings=[],
                structure_summary={}
            )


@dataclass
class GetCompanySalaryStructuresQuery:
    """Query to get company salary structures."""
    
    organization_id: str
    admin_user_id: str
    include_inactive: bool = False


@dataclass
class CompanySalaryStructuresResponse:
    """Response with company salary structures."""
    
    success: bool
    structures: List[Dict[str, Any]]
    message: str


class GetCompanySalaryStructuresUseCase:
    """Use case to get company salary structures."""
    
    def __init__(self, taxation_repository: TaxationRepository):
        self._taxation_repository = taxation_repository
    
    async def execute(self, query: GetCompanySalaryStructuresQuery) -> CompanySalaryStructuresResponse:
        """
        Get company salary structures.
        
        Args:
            query: Query parameters
            
        Returns:
            CompanySalaryStructuresResponse: Structures list
        """
        
        try:
            # Get structures from repository
            structures = await self._taxation_repository.get_company_salary_structures(
                query.organization_id,
                include_inactive=query.include_inactive
            )
            
            # Convert to response format
            structures_data = [
                structure.get_company_allowance_structure()
                for structure in structures
            ]
            
            return CompanySalaryStructuresResponse(
                success=True,
                structures=structures_data,
                message=f"Found {len(structures)} salary structures"
            )
            
        except Exception as e:
            return CompanySalaryStructuresResponse(
                success=False,
                structures=[],
                message=f"Failed to get salary structures: {str(e)}"
            ) 