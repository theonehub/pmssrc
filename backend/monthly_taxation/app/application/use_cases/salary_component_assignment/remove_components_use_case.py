"""
Remove Components Use Case
Removes salary component assignments from an organization
"""

import logging
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

from app.application.interfaces.repositories.salary_component_assignment_repository import SalaryComponentAssignmentRepository
from app.application.interfaces.repositories.salary_component_repository import SalaryComponentRepository
from app.application.dto.salary_component_assignment_dto import ComponentAssignmentDTO
from app.domain.entities.salary_component_assignment import AssignmentStatus
from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.component_id import ComponentId

logger = logging.getLogger(__name__)


@dataclass
class RemoveComponentsCommand:
    """Command to remove components from organization"""
    organization_id: str
    component_ids: List[str]
    notes: Optional[str] = None
    removed_by: str = ""


class RemoveComponentsUseCase:
    """Use case for removing salary component assignments from an organization"""
    
    def __init__(
        self,
        assignment_repository: SalaryComponentAssignmentRepository,
        organization_component_repository: SalaryComponentRepository
    ):
        self.assignment_repository = assignment_repository
        self.organization_component_repository = organization_component_repository
    
    async def execute(self, command: RemoveComponentsCommand) -> List[ComponentAssignmentDTO]:
        """
        Execute the use case.
        
        Args:
            command: Command containing removal details
            
        Returns:
            List of removed component assignments
        """
        try:
            logger.info(f"Removing {len(command.component_ids)} components from organization {command.organization_id}")
            
            removed_assignments = []
            
            for component_id in command.component_ids:
                try:
                    # Get existing assignment
                    assignment = await self.assignment_repository.get_assignment_by_organization_and_component(
                        organization_id=OrganizationId(command.organization_id),
                        component_id=ComponentId(component_id)
                    )
                    
                    if not assignment:
                        logger.warning(f"Component {component_id} not assigned to organization {command.organization_id}")
                        continue
                    
                    # Update assignment status to inactive
                    assignment.status = AssignmentStatus.INACTIVE
                    assignment.notes = command.notes or f"Removed by {command.removed_by}"
                    assignment.updated_at = datetime.utcnow()
                    assignment.updated_by = command.removed_by
                    
                    # Save updated assignment
                    updated_assignment = await self.assignment_repository.save_assignment(assignment)
                    
                    # Remove component from organization database
                    await self._remove_component_from_organization(
                        component_id=component_id,
                        organization_id=command.organization_id
                    )
                    
                    removed_assignments.append(updated_assignment)
                    
                    logger.info(f"Successfully removed component {component_id} from organization {command.organization_id}")
                    
                except Exception as e:
                    logger.error(f"Error removing component {component_id}: {e}")
                    continue
            
            # Convert to DTOs
            assignment_dtos = []
            for assignment in removed_assignments:
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
            
            logger.info(f"Successfully removed {len(assignment_dtos)} components from organization {command.organization_id}")
            return assignment_dtos
            
        except Exception as e:
            logger.error(f"Error in remove components use case: {e}")
            raise
    
    async def _remove_component_from_organization(self, component_id: str, organization_id: str):
        """
        Remove component from organization database.
        
        Args:
            component_id: Component ID to remove
            organization_id: Organization ID
        """
        try:
            # Delete component from organization database
            await self.organization_component_repository.delete(
                component_id=ComponentId(component_id),
                hostname=organization_id
            )
            
            logger.info(f"Removed component {component_id} from organization {organization_id}")
            
        except Exception as e:
            logger.error(f"Error removing component from organization: {e}")
            # Don't raise here as the assignment is already marked as inactive
            pass 