"""
Get Comparison Data Use Case
Provides comparison data between global and organization components
"""

import logging
from typing import List
from dataclasses import dataclass

from app.application.interfaces.repositories.salary_component_assignment_repository import (
    SalaryComponentAssignmentRepository,
    GlobalSalaryComponentRepository
)
from app.application.dto.salary_component_assignment_dto import (
    GlobalSalaryComponentDTO,
    ComponentAssignmentDTO
)

logger = logging.getLogger(__name__)


@dataclass
class GetComparisonDataCommand:
    """Command to get comparison data"""
    organization_id: str


@dataclass
class ComparisonDataResult:
    """Result containing comparison data"""
    global_components: List[GlobalSalaryComponentDTO]
    organization_components: List[ComponentAssignmentDTO]
    available_for_assignment: List[GlobalSalaryComponentDTO]


class GetComparisonDataUseCase:
    """Use case for getting comparison data between global and organization components"""
    
    def __init__(
        self,
        assignment_repository: SalaryComponentAssignmentRepository,
        global_component_repository: GlobalSalaryComponentRepository
    ):
        self.assignment_repository = assignment_repository
        self.global_component_repository = global_component_repository
    
    async def execute(self, command: GetComparisonDataCommand) -> ComparisonDataResult:
        """
        Execute the use case.
        
        Args:
            command: Command containing organization ID
            
        Returns:
            Comparison data result
        """
        try:
            logger.info(f"Getting comparison data for organization {command.organization_id}")
            
            # Get all global components
            global_components = await self.global_component_repository.get_all_components()
            
            # Get organization assignments
            from app.domain.value_objects.organization_id import OrganizationId
            organization_assignments = await self.assignment_repository.get_assignments_by_organization(
                organization_id=OrganizationId(command.organization_id),
                include_inactive=False
            )
            
            # Convert global components to DTOs
            global_component_dtos = []
            for component in global_components:
                dto = GlobalSalaryComponentDTO(
                    component_id=component.get("component_id", ""),
                    code=component.get("code", ""),
                    name=component.get("name", ""),
                    component_type=component.get("component_type", ""),
                    value_type=component.get("value_type", ""),
                    is_taxable=component.get("is_taxable", False),
                    exemption_section=component.get("exemption_section"),
                    formula=component.get("formula"),
                    default_value=component.get("default_value"),
                    description=component.get("description"),
                    is_active=component.get("is_active", True),
                    created_at=component.get("created_at"),
                    updated_at=component.get("updated_at")
                )
                global_component_dtos.append(dto)
            
            # Convert organization assignments to DTOs
            organization_component_dtos = []
            for assignment in organization_assignments:
                dto = ComponentAssignmentDTO(
                    assignment_id=assignment.assignment_id,
                    organization_id=str(assignment.organization_id),
                    component_id=str(assignment.component_id),
                    component_name=assignment.component_name,
                    component_code=assignment.component_code,
                    status=assignment.status,
                    assigned_by=assignment.assigned_by,
                    assigned_at=assignment.assigned_at,
                    notes=assignment.notes,
                    effective_from=assignment.effective_from,
                    effective_to=assignment.effective_to,
                    organization_specific_config=assignment.organization_specific_config,
                    is_effective=assignment.is_effective
                )
                organization_component_dtos.append(dto)
            
            # Find components available for assignment (global components not yet assigned)
            assigned_component_ids = {str(assignment.component_id) for assignment in organization_assignments}
            available_for_assignment = [
                dto for dto in global_component_dtos 
                if dto.component_id not in assigned_component_ids
            ]
            
            result = ComparisonDataResult(
                global_components=global_component_dtos,
                organization_components=organization_component_dtos,
                available_for_assignment=available_for_assignment
            )
            
            logger.info(f"Retrieved comparison data: {len(global_component_dtos)} global, {len(organization_component_dtos)} assigned, {len(available_for_assignment)} available")
            return result
            
        except Exception as e:
            logger.error(f"Error getting comparison data: {e}")
            raise 