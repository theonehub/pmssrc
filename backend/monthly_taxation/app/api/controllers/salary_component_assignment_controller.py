"""
Salary Component Assignment Controller
Handles salary component assignment operations for superadmin
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from app.application.use_cases.salary_component_assignment.get_global_salary_components_use_case import (
    GetGlobalSalaryComponentsUseCase,
    GetGlobalSalaryComponentsCommand
)
from app.application.use_cases.salary_component_assignment.get_organization_components_use_case import (
    GetOrganizationComponentsUseCase,
    GetOrganizationComponentsCommand
)
from app.application.use_cases.salary_component_assignment.assign_components_use_case import (
    AssignComponentsUseCase,
    AssignComponentsCommand
)
from app.application.use_cases.salary_component_assignment.remove_components_use_case import (
    RemoveComponentsUseCase,
    RemoveComponentsCommand
)
from app.application.use_cases.salary_component_assignment.get_comparison_data_use_case import (
    GetComparisonDataUseCase,
    GetComparisonDataCommand
)
from app.application.dto.salary_component_assignment_dto import (
    AssignComponentsRequestDTO,
    RemoveComponentsRequestDTO,
    UpdateAssignmentRequestDTO,
    AssignmentQueryRequestDTO
)

logger = logging.getLogger(__name__)


@dataclass
class CurrentUser:
    """Current user data for controller operations"""
    employee_id: str
    hostname: str
    role: str


class SalaryComponentAssignmentController:
    """Controller for salary component assignment operations"""
    
    def __init__(
        self,
        get_global_components_use_case: GetGlobalSalaryComponentsUseCase,
        get_organization_components_use_case: GetOrganizationComponentsUseCase,
        assign_components_use_case: AssignComponentsUseCase,
        remove_components_use_case: RemoveComponentsUseCase,
        get_comparison_data_use_case: GetComparisonDataUseCase
    ):
        self.get_global_components_use_case = get_global_components_use_case
        self.get_organization_components_use_case = get_organization_components_use_case
        self.assign_components_use_case = assign_components_use_case
        self.remove_components_use_case = remove_components_use_case
        self.get_comparison_data_use_case = get_comparison_data_use_case
    
    async def get_global_components(
        self,
        search_term: Optional[str] = None,
        component_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
        current_user: CurrentUser = None
    ) -> Dict[str, Any]:
        """
        Get global salary components from the global database.
        
        Args:
            search_term: Search term for filtering components
            component_type: Component type filter
            is_active: Active status filter
            page: Page number for pagination
            page_size: Page size for pagination
            current_user: Current user information
            
        Returns:
            Dictionary containing global components data
        """
        try:
            logger.info(f"Getting global salary components for user {current_user.employee_id}")
            
            command = GetGlobalSalaryComponentsCommand(
                search_term=search_term,
                component_type=component_type,
                is_active=is_active,
                page=page,
                page_size=page_size
            )
            
            components = await self.get_global_components_use_case.execute(command)
            
            # Convert to response format
            component_data = []
            for component in components:
                component_data.append({
                    "component_id": component.component_id,
                    "code": component.code,
                    "name": component.name,
                    "component_type": component.component_type,
                    "value_type": component.value_type,
                    "is_taxable": component.is_taxable,
                    "exemption_section": component.exemption_section,
                    "formula": component.formula,
                    "default_value": component.default_value,
                    "description": component.description,
                    "is_active": component.is_active,
                    "created_at": component.created_at.isoformat() if component.created_at else None,
                    "updated_at": component.updated_at.isoformat() if component.updated_at else None
                })
            
            return {
                "success": True,
                "data": component_data,
                "total": len(component_data),
                "page": page,
                "page_size": page_size,
                "message": f"Retrieved {len(component_data)} global components"
            }
            
        except Exception as e:
            logger.error(f"Error getting global components: {e}")
            return {
                "success": False,
                "data": [],
                "total": 0,
                "message": f"Failed to get global components: {str(e)}"
            }
    
    async def get_organization_components(
        self,
        organization_id: str,
        include_inactive: bool = False,
        current_user: CurrentUser = None
    ) -> Dict[str, Any]:
        """
        Get salary components assigned to a specific organization.
        
        Args:
            organization_id: Organization ID
            include_inactive: Whether to include inactive assignments
            current_user: Current user information
            
        Returns:
            Dictionary containing organization components data
        """
        try:
            logger.info(f"Getting organization components for {organization_id}")
            
            command = GetOrganizationComponentsCommand(
                organization_id=organization_id,
                include_inactive=include_inactive
            )
            
            assignments = await self.get_organization_components_use_case.execute(command)
            
            # Convert to response format
            assignment_data = []
            for assignment in assignments:
                assignment_data.append({
                    "assignment_id": assignment.assignment_id,
                    "organization_id": assignment.organization_id,
                    "component_id": assignment.component_id,
                    "component_name": assignment.component_name,
                    "component_code": assignment.component_code,
                    "status": assignment.status.value,
                    "assigned_by": assignment.assigned_by,
                    "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None,
                    "notes": assignment.notes,
                    "effective_from": assignment.effective_from.isoformat() if assignment.effective_from else None,
                    "effective_to": assignment.effective_to.isoformat() if assignment.effective_to else None,
                    "organization_specific_config": assignment.organization_specific_config,
                    "is_effective": assignment.is_effective
                })
            
            return {
                "success": True,
                "data": assignment_data,
                "total": len(assignment_data),
                "message": f"Retrieved {len(assignment_data)} organization components"
            }
            
        except Exception as e:
            logger.error(f"Error getting organization components: {e}")
            return {
                "success": False,
                "data": [],
                "total": 0,
                "message": f"Failed to get organization components: {str(e)}"
            }
    
    async def get_assignment_summary(
        self,
        organization_id: str,
        current_user: CurrentUser = None
    ) -> Dict[str, Any]:
        """
        Get assignment summary for an organization.
        
        Args:
            organization_id: Organization ID
            current_user: Current user information
            
        Returns:
            Dictionary containing assignment summary
        """
        try:
            logger.info(f"Getting assignment summary for {organization_id}")
            
            # Get organization components
            org_command = GetOrganizationComponentsCommand(
                organization_id=organization_id,
                include_inactive=False
            )
            org_assignments = await self.get_organization_components_use_case.execute(org_command)
            
            # Get global components
            global_command = GetGlobalSalaryComponentsCommand(
                search_term=None,
                component_type=None,
                is_active=True,
                page=1,
                page_size=1000
            )
            global_components = await self.get_global_components_use_case.execute(global_command)
            
            # Calculate summary
            active_assignments = [a for a in org_assignments if a.status.value == "ACTIVE"]
            inactive_assignments = [a for a in org_assignments if a.status.value == "INACTIVE"]
            
            summary = {
                "organization_id": organization_id,
                "total_global_components": len(global_components),
                "total_assigned_components": len(org_assignments),
                "active_assignments": len(active_assignments),
                "inactive_assignments": len(inactive_assignments),
                "available_for_assignment": len(global_components) - len(org_assignments),
                "assignment_breakdown": {
                    "earning": len([a for a in active_assignments if a.component_type == "EARNING"]),
                    "deduction": len([a for a in active_assignments if a.component_type == "DEDUCTION"]),
                    "reimbursement": len([a for a in active_assignments if a.component_type == "REIMBURSEMENT"])
                }
            }
            
            return {
                "success": True,
                "data": summary,
                "message": "Assignment summary retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting assignment summary: {e}")
            return {
                "success": False,
                "data": {},
                "message": f"Failed to get assignment summary: {str(e)}"
            }
    
    async def get_comparison_data(
        self,
        organization_id: str,
        current_user: CurrentUser = None
    ) -> Dict[str, Any]:
        """
        Get comparison data showing global vs organization components.
        
        Args:
            organization_id: Organization ID
            current_user: Current user information
            
        Returns:
            Dictionary containing comparison data
        """
        try:
            logger.info(f"Getting comparison data for {organization_id}")
            
            command = GetComparisonDataCommand(
                organization_id=organization_id
            )
            
            comparison_data = await self.get_comparison_data_use_case.execute(command)
            
            return {
                "success": True,
                "data": {
                    "global_components": comparison_data.global_components,
                    "organization_components": comparison_data.organization_components,
                    "available_for_assignment": comparison_data.available_for_assignment
                },
                "message": "Comparison data retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting comparison data: {e}")
            return {
                "success": False,
                "data": {
                    "global_components": [],
                    "organization_components": [],
                    "available_for_assignment": []
                },
                "message": f"Failed to get comparison data: {str(e)}"
            }
    
    async def assign_components(
        self,
        request: AssignComponentsRequestDTO,
        current_user: CurrentUser = None
    ) -> Dict[str, Any]:
        """
        Assign salary components to an organization.
        
        Args:
            request: Assignment request data
            current_user: Current user information
            
        Returns:
            Dictionary containing assignment results
        """
        try:
            logger.info(f"Assigning components to organization {request.organization_id}")
            
            command = AssignComponentsCommand(
                organization_id=request.organization_id,
                component_ids=request.component_ids,
                status=request.status,
                notes=request.notes,
                effective_from=request.effective_from,
                effective_to=request.effective_to,
                organization_specific_config=request.organization_specific_config,
                assigned_by=current_user.employee_id
            )
            
            assignments = await self.assign_components_use_case.execute(command)
            
            # Convert to response format
            assignment_data = []
            for assignment in assignments:
                assignment_data.append({
                    "assignment_id": assignment.assignment_id,
                    "organization_id": assignment.organization_id,
                    "component_id": assignment.component_id,
                    "component_name": assignment.component_name,
                    "component_code": assignment.component_code,
                    "status": assignment.status.value,
                    "assigned_by": assignment.assigned_by,
                    "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None,
                    "notes": assignment.notes,
                    "effective_from": assignment.effective_from.isoformat() if assignment.effective_from else None,
                    "effective_to": assignment.effective_to.isoformat() if assignment.effective_to else None,
                    "organization_specific_config": assignment.organization_specific_config,
                    "is_effective": assignment.is_effective
                })
            
            return {
                "success": True,
                "data": assignment_data,
                "message": f"Successfully assigned {len(assignment_data)} components"
            }
            
        except Exception as e:
            logger.error(f"Error assigning components: {e}")
            return {
                "success": False,
                "data": [],
                "message": f"Failed to assign components: {str(e)}"
            }
    
    async def remove_components(
        self,
        request: RemoveComponentsRequestDTO,
        current_user: CurrentUser = None
    ) -> Dict[str, Any]:
        """
        Remove salary component assignments from an organization.
        
        Args:
            request: Removal request data
            current_user: Current user information
            
        Returns:
            Dictionary containing removal results
        """
        try:
            logger.info(f"Removing components from organization {request.organization_id}")
            
            command = RemoveComponentsCommand(
                organization_id=request.organization_id,
                component_ids=request.component_ids,
                notes=request.notes,
                removed_by=current_user.employee_id
            )
            
            removed_assignments = await self.remove_components_use_case.execute(command)
            
            # Convert to response format
            assignment_data = []
            for assignment in removed_assignments:
                assignment_data.append({
                    "assignment_id": assignment.assignment_id,
                    "organization_id": assignment.organization_id,
                    "component_id": assignment.component_id,
                    "component_name": assignment.component_name,
                    "component_code": assignment.component_code,
                    "status": assignment.status.value,
                    "assigned_by": assignment.assigned_by,
                    "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None,
                    "notes": assignment.notes,
                    "effective_from": assignment.effective_from.isoformat() if assignment.effective_from else None,
                    "effective_to": assignment.effective_to.isoformat() if assignment.effective_to else None,
                    "organization_specific_config": assignment.organization_specific_config,
                    "is_effective": assignment.is_effective
                })
            
            return {
                "success": True,
                "data": assignment_data,
                "message": f"Successfully removed {len(assignment_data)} components"
            }
            
        except Exception as e:
            logger.error(f"Error removing components: {e}")
            return {
                "success": False,
                "data": [],
                "message": f"Failed to remove components: {str(e)}"
            }
    
    async def update_assignment(
        self,
        request: UpdateAssignmentRequestDTO,
        current_user: CurrentUser = None
    ) -> Dict[str, Any]:
        """
        Update an existing component assignment.
        
        Args:
            request: Update request data
            current_user: Current user information
            
        Returns:
            Dictionary containing update results
        """
        try:
            logger.info(f"Updating assignment {request.assignment_id}")
            
            # This would need a separate use case for updating assignments
            # For now, return a placeholder response
            return {
                "success": True,
                "data": {
                    "assignment_id": request.assignment_id,
                    "message": "Assignment update functionality not yet implemented"
                },
                "message": "Assignment update not yet implemented"
            }
            
        except Exception as e:
            logger.error(f"Error updating assignment: {e}")
            return {
                "success": False,
                "data": {},
                "message": f"Failed to update assignment: {str(e)}"
            }
    
    async def search_assignments(
        self,
        request: AssignmentQueryRequestDTO,
        current_user: CurrentUser = None
    ) -> Dict[str, Any]:
        """
        Search component assignments with filters.
        
        Args:
            request: Search request data
            current_user: Current user information
            
        Returns:
            Dictionary containing search results
        """
        try:
            logger.info("Searching assignments")
            
            # This would need a separate use case for searching assignments
            # For now, return a placeholder response
            return {
                "success": True,
                "data": [],
                "total": 0,
                "message": "Assignment search functionality not yet implemented"
            }
            
        except Exception as e:
            logger.error(f"Error searching assignments: {e}")
            return {
                "success": False,
                "data": [],
                "total": 0,
                "message": f"Failed to search assignments: {str(e)}"
            }
    
    async def health_check(self, current_user: CurrentUser = None) -> Dict[str, Any]:
        """
        Health check endpoint for assignment functionality.
        
        Args:
            current_user: Current user information
            
        Returns:
            Dictionary containing health status
        """
        try:
            logger.info("Performing health check")
            
            # Basic health check - try to get global components
            command = GetGlobalSalaryComponentsCommand(
                search_term=None,
                component_type=None,
                is_active=True,
                page=1,
                page_size=1
            )
            
            components = await self.get_global_components_use_case.execute(command)
            
            return {
                "success": True,
                "data": {
                    "status": "healthy",
                    "global_components_accessible": len(components) >= 0,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "message": "Assignment service is healthy"
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "success": False,
                "data": {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                },
                "message": f"Assignment service is unhealthy: {str(e)}"
            } 