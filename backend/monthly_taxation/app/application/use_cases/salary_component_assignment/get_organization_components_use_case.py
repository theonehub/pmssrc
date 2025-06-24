"""
Get Organization Components Use Case
Retrieves salary components assigned to a specific organization
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

from app.application.interfaces.repositories.salary_component_assignment_repository import (
    SalaryComponentAssignmentRepository,
    GlobalSalaryComponentRepository
)
from app.application.dto.salary_component_assignment_dto import (
    ComponentAssignmentDTO,
    AssignmentSummaryDTO,
    AssignmentComparisonDTO
)
from app.domain.value_objects.organization_id import OrganizationId

logger = logging.getLogger(__name__)


@dataclass
class GetOrganizationComponentsCommand:
    """Command to get organization components"""
    organization_id: str
    include_inactive: bool = False


class GetOrganizationComponentsUseCase:
    """Use case for retrieving organization-specific salary components"""
    
    def __init__(
        self, 
        assignment_repository: SalaryComponentAssignmentRepository,
        global_component_repository: GlobalSalaryComponentRepository
    ):
        self.assignment_repository = assignment_repository
        self.global_component_repository = global_component_repository
    
    async def execute(self, command: GetOrganizationComponentsCommand) -> List[ComponentAssignmentDTO]:
        """
        Execute the use case.
        
        Args:
            command: Command containing organization ID and filters
            
        Returns:
            List of component assignments for the organization
        """
        try:
            logger.info(f"Getting organization components for {command.organization_id}")
            
            # Get assignments from repository
            assignments = await self.assignment_repository.get_assignments_by_organization(
                organization_id=command.organization_id,
                include_inactive=command.include_inactive
            )
            
            # Convert to DTOs
            assignment_dtos = []
            for assignment in assignments:
                dto = ComponentAssignmentDTO(
                    assignment_id=assignment.assignment_id,
                    organization_id=assignment.organization_id,
                    component_id=assignment.component_id,
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
            
            logger.info(f"Retrieved {len(assignment_dtos)} organization components")
            return assignment_dtos
            
        except Exception as e:
            logger.error(f"Error getting organization components: {e}")
            raise
    
    async def get_assignment_summary(self, organization_id: str) -> AssignmentSummaryDTO:
        """
        Get assignment summary for an organization.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            Assignment summary for the organization
        """
        try:
            logger.info(f"Getting assignment summary for organization: {organization_id}")
            
            org_id = OrganizationId(organization_id)
            
            # Get summary from repository
            summary_data = await self.assignment_repository.get_assignment_summary(org_id)
            
            # Get assigned components for details
            assignments = await self.assignment_repository.get_assignments_by_organization(org_id)
            
            # Convert assignments to DTOs
            assignment_dtos = []
            for assignment in assignments:
                component_details = await self.global_component_repository.get_component_by_id(
                    str(assignment.component_id)
                )
                
                dto = ComponentAssignmentDTO(
                    assignment_id=assignment.assignment_id,
                    organization_id=str(assignment.organization_id),
                    component_id=str(assignment.component_id),
                    component_name=component_details.get("name") if component_details else None,
                    component_code=component_details.get("code") if component_details else None,
                    status=assignment.status,
                    assigned_by=assignment.assigned_by,
                    assigned_at=assignment.assigned_at,
                    notes=assignment.notes,
                    effective_from=assignment.effective_from,
                    effective_to=assignment.effective_to,
                    organization_specific_config=assignment.organization_specific_config,
                    is_effective=assignment.is_effective()
                )
                assignment_dtos.append(dto)
            
            # Create summary DTO
            summary_dto = AssignmentSummaryDTO(
                organization_id=organization_id,
                organization_name=None,  # Could be fetched from organization service
                total_components=summary_data.get("total_assignments", 0),
                active_assignments=summary_data.get("active_assignments", 0),
                inactive_assignments=summary_data.get("inactive_assignments", 0),
                last_assignment_date=summary_data.get("last_assignment_date"),
                assigned_components=assignment_dtos
            )
            
            logger.info(f"Retrieved assignment summary for organization {organization_id}")
            return summary_dto
            
        except Exception as e:
            logger.error(f"Error getting assignment summary: {e}")
            raise
    
    async def get_comparison_data(self, organization_id: str) -> AssignmentComparisonDTO:
        """
        Get comparison data showing global vs organization components.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            Comparison data with global and assigned components
        """
        try:
            logger.info(f"Getting comparison data for organization: {organization_id}")
            
            org_id = OrganizationId(organization_id)
            
            # Get all global components
            global_components = await self.global_component_repository.get_active_components()
            
            # Get assigned components
            assignments = await self.assignment_repository.get_assignments_by_organization(org_id)
            
            # Get assignment summary
            summary = await self.get_assignment_summary(organization_id)
            
            # Convert global components to DTOs
            global_dtos = []
            for component in global_components:
                dto = ComponentAssignmentDTO(
                    assignment_id="",  # Not assigned
                    organization_id=organization_id,
                    component_id=component.get("component_id", ""),
                    component_name=component.get("name", ""),
                    component_code=component.get("code", ""),
                    status=None,  # Not assigned
                    assigned_by="",
                    assigned_at=None,
                    notes=None,
                    effective_from=None,
                    effective_to=None,
                    organization_specific_config={},
                    is_effective=False
                )
                global_dtos.append(dto)
            
            # Convert assignments to DTOs
            assigned_dtos = []
            for assignment in assignments:
                component_details = await self.global_component_repository.get_component_by_id(
                    str(assignment.component_id)
                )
                
                dto = ComponentAssignmentDTO(
                    assignment_id=assignment.assignment_id,
                    organization_id=str(assignment.organization_id),
                    component_id=str(assignment.component_id),
                    component_name=component_details.get("name") if component_details else None,
                    component_code=component_details.get("code") if component_details else None,
                    status=assignment.status,
                    assigned_by=assignment.assigned_by,
                    assigned_at=assignment.assigned_at,
                    notes=assignment.notes,
                    effective_from=assignment.effective_from,
                    effective_to=assignment.effective_to,
                    organization_specific_config=assignment.organization_specific_config,
                    is_effective=assignment.is_effective()
                )
                assigned_dtos.append(dto)
            
            # Find components available for assignment (global but not assigned)
            assigned_component_ids = {str(assignment.component_id) for assignment in assignments}
            available_dtos = []
            for component in global_components:
                if component.get("component_id") not in assigned_component_ids:
                    dto = ComponentAssignmentDTO(
                        assignment_id="",  # Not assigned
                        organization_id=organization_id,
                        component_id=component.get("component_id", ""),
                        component_name=component.get("name", ""),
                        component_code=component.get("code", ""),
                        status=None,  # Not assigned
                        assigned_by="",
                        assigned_at=None,
                        notes=None,
                        effective_from=None,
                        effective_to=None,
                        organization_specific_config={},
                        is_effective=False
                    )
                    available_dtos.append(dto)
            
            # Create comparison DTO
            comparison_dto = AssignmentComparisonDTO(
                organization_id=organization_id,
                organization_name=None,  # Could be fetched from organization service
                global_components=global_dtos,
                assigned_components=assigned_dtos,
                available_for_assignment=available_dtos,
                assignment_summary=summary
            )
            
            logger.info(f"Retrieved comparison data for organization {organization_id}")
            return comparison_dto
            
        except Exception as e:
            logger.error(f"Error getting comparison data: {e}")
            raise 