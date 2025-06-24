"""
SOLID-Compliant Project Attributes Routes v2
Clean architecture implementation of project attributes HTTP endpoints
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from datetime import date, datetime

from app.api.controllers.project_attributes_controller import ProjectAttributesController
from app.application.dto.project_attributes_dto import (
    ProjectAttributeCreateRequestDTO,
    ProjectAttributeUpdateRequestDTO,
    ProjectAttributeSearchFiltersDTO,
    ProjectAttributeResponseDTO,
    ProjectAttributeSummaryDTO,
    ProjectAttributeAnalyticsDTO,
    ProjectAttributeValidationError,
    ProjectAttributeBusinessRuleError,
    ProjectAttributeNotFoundError
)
from app.config.dependency_container import get_dependency_container
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/project-attributes", tags=["project-attributes-v2"])

def get_project_attributes_controller() -> ProjectAttributesController:
    """Get project attributes controller instance."""
    try:
        container = get_dependency_container()
        return container.get_project_attributes_controller()
    except Exception as e:
        logger.warning(f"Could not get project attributes controller from container: {e}")
        return ProjectAttributesController()

# Health check endpoint
@router.get("/health")
async def health_check(
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
) -> Dict[str, str]:
    """Health check for project attributes service."""
    return await controller.health_check()

# Project attributes CRUD endpoints
@router.post("", response_model=ProjectAttributeResponseDTO)
async def create_project_attribute(
    request: ProjectAttributeCreateRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
) -> ProjectAttributeResponseDTO:
    """Create a new project attribute."""
    try:
        logger.info(f"Creating project attribute by {current_user.employee_id}")
        return await controller.create_project_attribute(request, current_user.hostname)
    except Exception as e:
        logger.error(f"Error creating project attribute: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProjectAttributeResponseDTO])
async def get_project_attributes(
    key: Optional[str] = Query(None, description="Filter by key"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Get project attributes with optional filters"""
    try:
        logger.info(f"Getting project attributes with filters: key={key}")
        
        filters = ProjectAttributeSearchFiltersDTO(
            key=key,
            skip=skip,
            limit=limit
        )
        
        response = await controller.get_project_attributes(filters, current_user.hostname)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting project attributes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{key}", response_model=ProjectAttributeResponseDTO)
async def get_project_attribute(
    key: str = Path(..., description="Project attribute key"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Get a specific project attribute by key"""
    try:
        logger.info(f"Getting project attribute: {key}")
        
        response = await controller.get_project_attribute(key, current_user.hostname)
        
        if not response:
            raise HTTPException(status_code=404, detail="Project attribute not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project attribute {key}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{key}", response_model=ProjectAttributeResponseDTO)
async def update_project_attribute(
    request: ProjectAttributeUpdateRequestDTO,
    key: str = Path(..., description="Project attribute key"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Update an existing project attribute"""
    try:
        logger.info(f"Updating project attribute: {key} by {current_user.employee_id}")
        
        response = await controller.update_project_attribute(
            key, request, current_user.hostname
        )
        
        return response
        
    except ProjectAttributeNotFoundError as e:
        logger.warning(f"Project attribute not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except ProjectAttributeValidationError as e:
        logger.warning(f"Validation error updating project attribute: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except ProjectAttributeBusinessRuleError as e:
        logger.warning(f"Business rule error updating project attribute: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error updating project attribute: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{key}")
async def delete_project_attribute(
    key: str = Path(..., description="Project attribute key"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Delete a project attribute"""
    try:
        logger.info(f"Deleting project attribute: {key} by {current_user.employee_id}")
        
        await controller.delete_project_attribute(key, current_user.hostname)
        
        return {"message": "Project attribute deleted successfully"}
        
    except ProjectAttributeNotFoundError as e:
        logger.warning(f"Project attribute not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except ProjectAttributeBusinessRuleError as e:
        logger.warning(f"Business rule error deleting project attribute: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error deleting project attribute: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 