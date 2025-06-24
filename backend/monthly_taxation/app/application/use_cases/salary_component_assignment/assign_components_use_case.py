"""
Assign Components Use Case
Assigns salary components from global database to an organization
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from app.application.interfaces.repositories.salary_component_assignment_repository import (
    SalaryComponentAssignmentRepository,
    GlobalSalaryComponentRepository
)
from app.application.interfaces.repositories.salary_component_repository import SalaryComponentRepository
from app.application.dto.salary_component_assignment_dto import ComponentAssignmentDTO
from app.domain.entities.salary_component_assignment import SalaryComponentAssignment, AssignmentStatus
from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.component_id import ComponentId

logger = logging.getLogger(__name__)


@dataclass
class AssignComponentsCommand:
    """Command to assign components to organization"""
    organization_id: str
    component_ids: List[str]
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    notes: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    organization_specific_config: Optional[Dict[str, Any]] = None
    assigned_by: str = ""


class AssignComponentsUseCase:
    """Use case for assigning salary components to an organization"""
    
    def __init__(
        self,
        assignment_repository: SalaryComponentAssignmentRepository,
        global_component_repository: GlobalSalaryComponentRepository,
        organization_component_repository: SalaryComponentRepository
    ):
        self.assignment_repository = assignment_repository
        self.global_component_repository = global_component_repository
        self.organization_component_repository = organization_component_repository
    
    async def execute(self, command: AssignComponentsCommand) -> List[ComponentAssignmentDTO]:
        """
        Execute the use case.
        
        Args:
            command: Command containing assignment details
            
        Returns:
            List of created component assignments
        """
        try:
            logger.info(f"Assigning {len(command.component_ids)} components to organization {command.organization_id}")
            
            assignments = []
            
            for component_id in command.component_ids:
                try:
                    # Get component from global database
                    global_component = await self.global_component_repository.get_component_by_id(component_id)
                    
                    if not global_component:
                        logger.warning(f"Component {component_id} not found in global database")
                        continue
                    
                    # Check if already assigned
                    existing_assignment = await self.assignment_repository.get_assignment_by_organization_and_component(
                        organization_id=OrganizationId(command.organization_id),
                        component_id=ComponentId(component_id)
                    )
                    
                    if existing_assignment:
                        logger.info(f"Component {component_id} already assigned to organization {command.organization_id}")
                        continue
                    
                    # Create assignment record
                    assignment = SalaryComponentAssignment(
                        organization_id=OrganizationId(command.organization_id),
                        component_id=ComponentId(component_id),
                        status=command.status,
                        assigned_by=command.assigned_by,
                        assigned_at=datetime.utcnow(),
                        notes=command.notes,
                        effective_from=command.effective_from,
                        effective_to=command.effective_to,
                        organization_specific_config=command.organization_specific_config or {}
                    )
                    
                    # Save assignment
                    saved_assignment = await self.assignment_repository.save_assignment(assignment)
                    
                    # Copy component to organization database
                    await self._copy_component_to_organization(
                        global_component=global_component,
                        organization_id=command.organization_id
                    )
                    
                    assignments.append(saved_assignment)
                    
                    logger.info(f"Successfully assigned component {component_id} to organization {command.organization_id}")
                    
                except Exception as e:
                    logger.error(f"Error assigning component {component_id}: {e}")
                    continue
            
            # Convert to DTOs
            assignment_dtos = []
            for assignment in assignments:
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
                assignment_dtos.append(dto)
            
            logger.info(f"Successfully assigned {len(assignment_dtos)} components to organization {command.organization_id}")
            return assignment_dtos
            
        except Exception as e:
            logger.error(f"Error in assign components use case: {e}")
            raise
    
    async def _copy_component_to_organization(self, global_component: dict, organization_id: str):
        """
        Copy component from global database to organization database.
        
        Args:
            global_component: Component data from global database
            organization_id: Target organization ID
        """
        try:
            # Create component entity for organization
            from app.domain.entities.salary_component import SalaryComponent
            from app.domain.value_objects.component_type import ComponentType, ValueType
            from app.domain.entities.salary_component import ExemptionSection
            
            component = SalaryComponent(
                id=ComponentId(global_component["component_id"]),
                code=global_component["code"],
                name=global_component["name"],
                component_type=ComponentType(global_component["component_type"]),
                value_type=ValueType(global_component["value_type"]),
                is_taxable=global_component["is_taxable"],
                exemption_section=ExemptionSection(global_component.get("exemption_section", "NONE")),
                formula=global_component.get("formula"),
                default_value=global_component.get("default_value"),
                description=global_component.get("description"),
                is_active=True,
                created_by="system",
                updated_by="system"
            )
            
            # Save to organization database
            await self.organization_component_repository.save(component, organization_id)
            
            logger.info(f"Copied component {global_component['component_id']} to organization {organization_id}")
            
        except Exception as e:
            logger.error(f"Error copying component to organization: {e}")
            raise 