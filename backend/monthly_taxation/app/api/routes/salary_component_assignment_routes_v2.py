"""
Salary Component Assignment API Routes v2
RESTful endpoints for salary component assignment operations
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, status, Depends, Body
from pydantic import BaseModel, Field

from app.application.dto.salary_component_assignment_dto import (
    AssignComponentsRequestDTO,
    RemoveComponentsRequestDTO,
    UpdateAssignmentRequestDTO,
    AssignmentQueryRequestDTO
)
from app.api.controllers.salary_component_assignment_controller import (
    SalaryComponentAssignmentController,
    CurrentUser
)
from app.auth.auth_dependencies import get_current_user, require_role, require_superadmin

logger = logging.getLogger(__name__)

# Router instance
router = APIRouter(
    prefix="/api/v2/salary-components/assignments",
    tags=["salary-component-assignments"],
    responses={404: {"description": "Not found"}}
)


def get_assignment_controller() -> SalaryComponentAssignmentController:
    """Dependency injection for assignment controller"""
    from app.config.dependency_container import container
    return container.get_salary_component_assignment_controller()


def convert_user_to_controller_user(user_dict: Dict[str, Any]) -> CurrentUser:
    """Convert user dictionary to controller CurrentUser object"""
    return CurrentUser(
        employee_id=user_dict["employee_id"],
        hostname=user_dict["hostname"],
        role=user_dict["role"]
    )


@router.get("/global", response_model=Dict[str, Any])
async def get_global_salary_components(
    search_term: Optional[str] = Query(None, description="Search term"),
    component_type: Optional[str] = Query(None, description="Component type filter"),
    is_active: Optional[bool] = Query(None, description="Active status filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    controller: SalaryComponentAssignmentController = Depends(get_assignment_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    role: str = Depends(require_superadmin)
) -> Dict[str, Any]:
    """
    Get all salary components from the global database.
    
    This endpoint retrieves salary components that are available for assignment
    to organizations. Only superadmin can access this endpoint.
    """
    logger.info("API: Getting global salary components")
    
    try:
        result = await controller.get_global_components(
            search_term=search_term,
            component_type=component_type,
            is_active=is_active,
            page=page,
            page_size=page_size,
            current_user=convert_user_to_controller_user(current_user)
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_global_salary_components: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organization/{organization_id}", response_model=Dict[str, Any])
async def get_organization_components(
    organization_id: str = Path(..., description="Organization ID"),
    include_inactive: bool = Query(False, description="Include inactive assignments"),
    controller: SalaryComponentAssignmentController = Depends(get_assignment_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    role: str = Depends(require_superadmin)
) -> Dict[str, Any]:
    """
    Get salary components assigned to a specific organization.
    
    This endpoint retrieves all salary components that have been assigned
    to the specified organization. Only superadmin can access this endpoint.
    """
    logger.info(f"API: Getting components for organization {organization_id}")
    
    try:
        result = await controller.get_organization_components(
            organization_id=organization_id,
            include_inactive=include_inactive,
            current_user=convert_user_to_controller_user(current_user)
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_organization_components: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organization/{organization_id}/summary", response_model=Dict[str, Any])
async def get_assignment_summary(
    organization_id: str = Path(..., description="Organization ID"),
    controller: SalaryComponentAssignmentController = Depends(get_assignment_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    role: str = Depends(require_superadmin)
) -> Dict[str, Any]:
    """
    Get assignment summary for an organization.
    
    This endpoint provides a summary of component assignments for the
    specified organization. Only superadmin can access this endpoint.
    """
    logger.info(f"API: Getting assignment summary for organization {organization_id}")
    
    try:
        result = await controller.get_assignment_summary(
            organization_id=organization_id,
            current_user=convert_user_to_controller_user(current_user)
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_assignment_summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organization/{organization_id}/comparison", response_model=Dict[str, Any])
async def get_comparison_data(
    organization_id: str = Path(..., description="Organization ID"),
    controller: SalaryComponentAssignmentController = Depends(get_assignment_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    role: str = Depends(require_superadmin)
) -> Dict[str, Any]:
    """
    Get comparison data showing global vs organization components.
    
    This endpoint provides a side-by-side comparison of global components
    and components assigned to the organization. Only superadmin can access this endpoint.
    """
    logger.info(f"API: Getting comparison data for organization {organization_id}")
    
    try:
        result = await controller.get_comparison_data(
            organization_id=organization_id,
            current_user=convert_user_to_controller_user(current_user)
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_comparison_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign", response_model=Dict[str, Any])
async def assign_components(
    request: AssignComponentsRequestDTO = Body(...),
    controller: SalaryComponentAssignmentController = Depends(get_assignment_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    role: str = Depends(require_superadmin)
) -> Dict[str, Any]:
    """
    Assign salary components to an organization.
    
    This endpoint assigns one or more salary components from the global database
    to a specific organization. Only superadmin can access this endpoint.
    """
    logger.info(f"API: Assigning components to organization {request.organization_id}")
    
    try:
        result = await controller.assign_components(
            request=request,
            current_user=convert_user_to_controller_user(current_user)
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error in assign_components: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove", response_model=Dict[str, Any])
async def remove_components(
    request: RemoveComponentsRequestDTO = Body(...),
    controller: SalaryComponentAssignmentController = Depends(get_assignment_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    role: str = Depends(require_superadmin)
) -> Dict[str, Any]:
    """
    Remove salary component assignments from an organization.
    
    This endpoint removes one or more salary component assignments from
    a specific organization. Only superadmin can access this endpoint.
    """
    logger.info(f"API: Removing components from organization {request.organization_id}")
    
    try:
        result = await controller.remove_components(
            request=request,
            current_user=convert_user_to_controller_user(current_user)
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error in remove_components: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", response_model=Dict[str, Any])
async def update_assignment(
    request: UpdateAssignmentRequestDTO = Body(...),
    controller: SalaryComponentAssignmentController = Depends(get_assignment_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    role: str = Depends(require_superadmin)
) -> Dict[str, Any]:
    """
    Update an existing component assignment.
    
    This endpoint updates the status, notes, effective dates, or configuration
    of an existing component assignment. Only superadmin can access this endpoint.
    """
    logger.info(f"API: Updating assignment {request.assignment_id}")
    
    try:
        result = await controller.update_assignment(
            request=request,
            current_user=convert_user_to_controller_user(current_user)
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error in update_assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=Dict[str, Any])
async def search_assignments(
    organization_id: Optional[str] = Query(None, description="Filter by organization ID"),
    component_id: Optional[str] = Query(None, description="Filter by component ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    include_inactive: bool = Query(False, description="Include inactive assignments"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    controller: SalaryComponentAssignmentController = Depends(get_assignment_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    role: str = Depends(require_superadmin)
) -> Dict[str, Any]:
    """
    Search component assignments with filters.
    
    This endpoint searches for component assignments using various filters.
    Only superadmin can access this endpoint.
    """
    logger.info("API: Searching assignments")
    
    try:
        from app.application.dto.salary_component_assignment_dto import AssignmentQueryRequestDTO
        from app.domain.entities.salary_component_assignment import AssignmentStatus
        
        # Convert status string to enum if provided
        status_enum = None
        if status:
            try:
                status_enum = AssignmentStatus(status.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        request = AssignmentQueryRequestDTO(
            organization_id=organization_id,
            component_id=component_id,
            status=status_enum,
            include_inactive=include_inactive,
            page=page,
            page_size=page_size
        )
        
        result = await controller.search_assignments(
            request=request,
            current_user=convert_user_to_controller_user(current_user)
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error in search_assignments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def health_check(
    controller: SalaryComponentAssignmentController = Depends(get_assignment_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    role: str = Depends(require_superadmin)
) -> Dict[str, Any]:
    """
    Health check for assignment service.
    
    This endpoint provides health status information for the assignment service.
    Only superadmin can access this endpoint.
    """
    logger.info("API: Health check for assignment service")
    
    try:
        # Try to get a small sample of global components to verify connectivity
        result = await controller.get_global_components(
            page=1,
            page_size=1,
            current_user=convert_user_to_controller_user(current_user)
        )
        
        return {
            "success": True,
            "status": "healthy",
            "message": "Assignment service is operational",
            "timestamp": "2024-01-01T00:00:00"  # Could use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "message": f"Assignment service error: {str(e)}",
            "timestamp": "2024-01-01T00:00:00"  # Could use actual timestamp
        } 