"""
Assign Components to Organization Use Case
Assigns salary components from global database to specific organizations
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

from app.application.interfaces.repositories.salary_component_assignment_repository import (
    SalaryComponentAssignmentRepository,
    GlobalSalaryComponentRepository
)
from app.application.dto.salary_component_assignment_dto import (
    AssignComponentsRequestDTO,
    BulkAssignmentResponseDTO
)
from app.domain.entities.salary_component_assignment import (
    SalaryComponentAssignment,
    AssignmentStatus,
    BulkComponentAssignment
)
from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.component_id import ComponentId

logger = logging.getLogger(__name__)


@dataclass
class AssignComponentsCommand:
    """Command to assign components to organization"""
    organization_id: str
    component_ids: List[str]
    assigned_by: str
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    notes: str = ""
    effective_from: datetime = None
    effective_to: datetime = None
    organization_specific_config: Dict[str, Any] = None


class AssignComponentsToOrganizationUseCase:
    """Use case for assigning salary components to organizations"""
    
    def __init__(
        self, 
        assignment_repository: SalaryComponentAssignmentRepository,
        global_component_repository: GlobalSalaryComponentRepository
    ):
        self.assignment_repository = assignment_repository
        self.global_component_repository = global_component_repository
    
    async def execute(self, command: AssignComponentsCommand) -> BulkAssignmentResponseDTO:
        """
        Execute the use case.
        
        Args:
            command: Command containing assignment details
            
        Returns:
            Bulk assignment response with results
        """
        try:
            logger.info(f"Assigning {len(command.component_ids)} components to organization {command.organization_id}")
            
            org_id = OrganizationId(command.organization_id)
            operation_id = str(uuid.uuid4())
            
            successful_assignments = 0
            failed_assignments = 0
            successful_components = []
            failed_components = []
            
            # Process each component
            for component_id in command.component_ids:
                try:
                    # Validate component exists in global database
                    component_details = await self.global_component_repository.get_component_by_id(component_id)
                    if not component_details:
                        failed_assignments += 1
                        failed_components.append({
                            "component_id": component_id,
                            "error": "Component not found in global database"
                        })
                        continue
                    
                    # Check if already assigned
                    comp_id = ComponentId(component_id)
                    existing_assignment = await self.assignment_repository.get_assignment_by_organization_and_component(
                        org_id, comp_id
                    )
                    
                    if existing_assignment:
                        # Update existing assignment
                        existing_assignment.status = command.status
                        existing_assignment.notes = command.notes
                        existing_assignment.effective_from = command.effective_from
                        existing_assignment.effective_to = command.effective_to
                        if command.organization_specific_config:
                            existing_assignment.update_config(command.organization_specific_config)
                        
                        await self.assignment_repository.update_assignment(existing_assignment)
                        logger.info(f"Updated assignment for component {component_id}")
                    else:
                        # Create new assignment
                        assignment = SalaryComponentAssignment(
                            assignment_id=str(uuid.uuid4()),
                            organization_id=org_id,
                            component_id=comp_id,
                            status=command.status,
                            assigned_by=command.assigned_by,
                            assigned_at=datetime.utcnow(),
                            notes=command.notes,
                            effective_from=command.effective_from,
                            effective_to=command.effective_to,
                            organization_specific_config=command.organization_specific_config or {}
                        )
                        
                        await self.assignment_repository.save_assignment(assignment)
                        logger.info(f"Created assignment for component {component_id}")
                    
                    successful_assignments += 1
                    successful_components.append(component_id)
                    
                except Exception as e:
                    logger.error(f"Error assigning component {component_id}: {e}")
                    failed_assignments += 1
                    failed_components.append({
                        "component_id": component_id,
                        "error": str(e)
                    })
            
            # Create response
            response = BulkAssignmentResponseDTO(
                operation_id=operation_id,
                organization_id=command.organization_id,
                total_components=len(command.component_ids),
                successful_assignments=successful_assignments,
                failed_assignments=failed_assignments,
                successful_components=successful_components,
                failed_components=failed_components,
                operation_status="completed" if failed_assignments == 0 else "completed_with_errors",
                processed_at=datetime.utcnow(),
                notes=command.notes
            )
            
            logger.info(f"Assignment operation completed: {successful_assignments} successful, {failed_assignments} failed")
            return response
            
        except Exception as e:
            logger.error(f"Error in assign components use case: {e}")
            raise
    
    async def execute_bulk_assignment(self, request: AssignComponentsRequestDTO, assigned_by: str) -> BulkAssignmentResponseDTO:
        """
        Execute bulk assignment from request DTO.
        
        Args:
            request: Assignment request DTO
            assigned_by: User performing the assignment
            
        Returns:
            Bulk assignment response
        """
        try:
            command = AssignComponentsCommand(
                organization_id=request.organization_id,
                component_ids=request.component_ids,
                assigned_by=assigned_by,
                status=request.status,
                notes=request.notes or "",
                effective_from=request.effective_from,
                effective_to=request.effective_to,
                organization_specific_config=request.organization_specific_config
            )
            
            return await self.execute(command)
            
        except Exception as e:
            logger.error(f"Error in bulk assignment: {e}")
            raise
    
    async def assign_components_with_validation(
        self, 
        organization_id: str,
        component_ids: List[str],
        assigned_by: str,
        validate_existence: bool = True
    ) -> BulkAssignmentResponseDTO:
        """
        Assign components with optional validation.
        
        Args:
            organization_id: Organization ID
            component_ids: List of component IDs to assign
            assigned_by: User performing the assignment
            validate_existence: Whether to validate component existence
            
        Returns:
            Bulk assignment response
        """
        try:
            logger.info(f"Assigning components with validation to organization {organization_id}")
            
            org_id = OrganizationId(organization_id)
            operation_id = str(uuid.uuid4())
            
            successful_assignments = 0
            failed_assignments = 0
            successful_components = []
            failed_components = []
            
            # Validate components exist if required
            if validate_existence:
                for component_id in component_ids:
                    component_details = await self.global_component_repository.get_component_by_id(component_id)
                    if not component_details:
                        failed_assignments += 1
                        failed_components.append({
                            "component_id": component_id,
                            "error": "Component not found in global database"
                        })
                        component_ids.remove(component_id)
            
            # Create bulk assignment
            bulk_assignment = BulkComponentAssignment(
                organization_id=org_id,
                component_ids=[ComponentId(cid) for cid in component_ids],
                assigned_by=assigned_by
            )
            
            # Create individual assignments
            assignments = bulk_assignment.create_assignments()
            
            # Save assignments
            if assignments:
                await self.assignment_repository.save_assignments(assignments)
                successful_assignments = len(assignments)
                successful_components = [str(assignment.component_id) for assignment in assignments]
            
            # Create response
            response = BulkAssignmentResponseDTO(
                operation_id=operation_id,
                organization_id=organization_id,
                total_components=len(component_ids) + len(failed_components),
                successful_assignments=successful_assignments,
                failed_assignments=failed_assignments,
                successful_components=successful_components,
                failed_components=failed_components,
                operation_status="completed" if failed_assignments == 0 else "completed_with_errors",
                processed_at=datetime.utcnow()
            )
            
            logger.info(f"Bulk assignment completed: {successful_assignments} successful, {failed_assignments} failed")
            return response
            
        except Exception as e:
            logger.error(f"Error in bulk assignment with validation: {e}")
            raise 