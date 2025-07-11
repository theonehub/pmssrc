"""
SOLID-Compliant Project Attributes Routes v2
Clean architecture implementation of project attributes HTTP endpoints with enhanced type support
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
    ProjectAttributeNotFoundError,
    ValueType
)
from app.config.dependency_container import get_dependency_container
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v2/project-attributes", tags=["project-attributes-v2"])

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

# Value types endpoint
@router.get("/value-types")
async def get_supported_value_types(
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
) -> List[Dict[str, Any]]:
    """Get list of supported value types."""
    return await controller.get_supported_value_types()

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
    except ProjectAttributeValidationError as e:
        logger.warning(f"Validation error creating project attribute: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    except ProjectAttributeBusinessRuleError as e:
        logger.warning(f"Business rule error creating project attribute: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    except Exception as e:
        logger.error(f"Error creating project attribute: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[ProjectAttributeResponseDTO])
async def get_project_attributes(
    key: Optional[str] = Query(None, description="Filter by key"),
    value_type: Optional[ValueType] = Query(None, description="Filter by value type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Filter by system-managed status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Get project attributes with optional filters"""
    try:
        logger.info(f"Getting project attributes with filters: key={key}, type={value_type}, category={category}")
        
        filters = ProjectAttributeSearchFiltersDTO(
            key=key,
            value_type=value_type,
            category=category,
            is_active=is_active,
            is_system=is_system,
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
        
        success = await controller.delete_project_attribute(key, current_user.hostname)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project attribute not found")
        
        return {"message": "Project attribute deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting project attribute: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Category-based endpoints
@router.get("/category/{category}", response_model=List[ProjectAttributeResponseDTO])
async def get_attributes_by_category(
    category: str = Path(..., description="Category name"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Get all attributes in a specific category"""
    try:
        logger.info(f"Getting attributes by category: {category}")
        
        response = await controller.get_attributes_by_category(category, current_user.hostname)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting attributes by category: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Summary endpoint
@router.get("/summary", response_model=ProjectAttributeSummaryDTO)
async def get_attributes_summary(
    current_user: CurrentUser = Depends(get_current_user),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Get summary statistics for project attributes"""
    try:
        logger.info("Getting project attributes summary")
        
        response = await controller.get_attributes_summary(current_user.hostname)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting attributes summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Utility endpoints for getting typed values
@router.get("/boolean/{key}")
async def get_boolean_attribute(
    key: str = Path(..., description="Attribute key"),
    default: bool = Query(False, description="Default value if not found"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Get a boolean attribute value"""
    try:
        logger.info(f"Getting boolean attribute: {key}")
        
        value = await controller.get_boolean_attribute(key, current_user.hostname, default)
        
        return {"key": key, "value": value, "type": "boolean"}
        
    except Exception as e:
        logger.error(f"Error getting boolean attribute: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/numeric/{key}")
async def get_numeric_attribute(
    key: str = Path(..., description="Attribute key"),
    default: float = Query(0.0, description="Default value if not found"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Get a numeric attribute value"""
    try:
        logger.info(f"Getting numeric attribute: {key}")
        
        value = await controller.get_numeric_attribute(key, current_user.hostname, default)
        
        return {"key": key, "value": value, "type": "numeric"}
        
    except Exception as e:
        logger.error(f"Error getting numeric attribute: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/string/{key}")
async def get_string_attribute(
    key: str = Path(..., description="Attribute key"),
    default: str = Query("", description="Default value if not found"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Get a string attribute value"""
    try:
        logger.info(f"Getting string attribute: {key}")
        
        value = await controller.get_string_attribute(key, current_user.hostname, default)
        
        return {"key": key, "value": value, "type": "string"}
        
    except Exception as e:
        logger.error(f"Error getting string attribute: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Bulk operations endpoint
@router.post("/bulk")
async def create_bulk_attributes(
    requests: List[ProjectAttributeCreateRequestDTO],
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    controller: ProjectAttributesController = Depends(get_project_attributes_controller)
):
    """Create multiple project attributes in bulk"""
    try:
        logger.info(f"Creating {len(requests)} project attributes by {current_user.employee_id}")
        
        results = []
        errors = []
        
        for request in requests:
            try:
                result = await controller.create_project_attribute(request, current_user.hostname)
                results.append(result)
            except Exception as e:
                errors.append({"key": request.key, "error": str(e)})
        
        return {
            "created": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Error in bulk creation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 