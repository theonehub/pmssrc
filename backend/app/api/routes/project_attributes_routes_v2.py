"""
SOLID-Compliant Project Attributes Routes
Clean API layer following SOLID principles
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from api.controllers.project_attributes_controller import ProjectAttributesController
from application.dto.project_attributes_dto import (
    ProjectAttributeCreateRequestDTO,
    ProjectAttributeUpdateRequestDTO,
    ProjectAttributeSearchFiltersDTO,
    ProjectAttributeResponseDTO,
    ProjectAttributeValidationError,
    ProjectAttributeBusinessRuleError,
    ProjectAttributeNotFoundError
)
from auth.auth import extract_emp_id, extract_hostname, role_checker

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/project-attributes", tags=["Project Attributes V2 (SOLID)"])


def get_project_attributes_controller() -> ProjectAttributesController:
    """Dependency injection for project attributes controller"""
    from config.dependency_container import get_dependency_container
    container = get_dependency_container()
    return container.get_project_attributes_controller()


# ==================== PROJECT ATTRIBUTES ENDPOINTS ====================

@router.post("/", response_model=ProjectAttributeResponseDTO)
async def create_project_attribute(
    request: ProjectAttributeCreateRequestDTO,
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Create a new project attribute"""
    try:
        logger.info(f"Creating project attribute: {request.key} by {current_emp_id}")
        
        response = await controller.create_project_attribute(request, current_emp_id, hostname)
        
        return response
        
    except ProjectAttributeValidationError as e:
        logger.warning(f"Validation error creating project attribute: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except ProjectAttributeBusinessRuleError as e:
        logger.warning(f"Business rule error creating project attribute: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error creating project attribute: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[ProjectAttributeResponseDTO])
async def get_project_attributes(
    key: Optional[str] = Query(None, description="Filter by key"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    hostname: str = Depends(extract_hostname),
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
        
        response = await controller.get_project_attributes(filters, hostname)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting project attributes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{key}", response_model=ProjectAttributeResponseDTO)
async def get_project_attribute(
    key: str = Path(..., description="Project attribute key"),
    hostname: str = Depends(extract_hostname),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Get a specific project attribute by key"""
    try:
        logger.info(f"Getting project attribute: {key}")
        
        response = await controller.get_project_attribute(key, hostname)
        
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
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Update an existing project attribute"""
    try:
        logger.info(f"Updating project attribute: {key} by {current_emp_id}")
        
        response = await controller.update_project_attribute(
            key, request, current_emp_id, hostname
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
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Delete a project attribute"""
    try:
        logger.info(f"Deleting project attribute: {key} by {current_emp_id}")
        
        await controller.delete_project_attribute(key, current_emp_id, hostname)
        
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


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "project_attributes_v2"} 