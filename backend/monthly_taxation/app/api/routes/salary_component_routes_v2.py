"""
Salary Component API Routes v2
Implements RESTful endpoints for salary component management
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, status, Depends
from pydantic import BaseModel, Field

from app.application.dto.salary_component_dto import (
    CreateSalaryComponentDTO,
    UpdateSalaryComponentDTO,
    SalaryComponentSearchFiltersDTO
)
from app.config.dependency_container import container
from app.api.controllers.salary_component_controller import SalaryComponentController
from app.auth.auth_integration import get_current_user_dict, CurrentUser, get_current_user
from app.api.controllers.salary_component_controller import CurrentUser as ControllerCurrentUser

logger = logging.getLogger(__name__)

# Router instance
router = APIRouter(
    prefix="/api/v2/salary-components",
    tags=["salary-components"],
    responses={404: {"description": "Not found"}}
)


class FormulaValidationRequest(BaseModel):
    """Request model for formula validation"""
    formula: str = Field(..., description="Formula to validate")


def get_controller() -> SalaryComponentController:
    """Dependency injection for controller"""
    return container.get_salary_component_controller()


def convert_user_dict_to_object(user_dict: Dict[str, Any]) -> ControllerCurrentUser:
    """Convert user dictionary to CurrentUser object"""
    return ControllerCurrentUser(
        employee_id=user_dict["employee_id"],
        hostname=user_dict["hostname"],
        role=user_dict["role"]
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_salary_component(
    dto: CreateSalaryComponentDTO,
    controller: SalaryComponentController = Depends(get_controller),
    current_user: Dict[str, Any] = Depends(get_current_user_dict)
) -> Dict[str, Any]:
    """
    Create a new salary component
    
    - **code**: Unique component code (e.g., BASIC, HRA)
    - **name**: Human readable name
    - **component_type**: EARNING, DEDUCTION, or BENEFIT
    - **value_type**: FIXED, PERCENTAGE, or FORMULA
    - **is_taxable**: Whether component is taxable
    - **exemption_section**: Tax exemption section if applicable
    """
    logger.info(f"API: Creating salary component {dto.code}")
    
    return await controller.create_component(
        dto=dto,
        current_user=convert_user_dict_to_object(current_user)
    )


@router.get("/{component_id}")
async def get_salary_component(
    component_id: str = Path(..., description="Component ID"),
    controller: SalaryComponentController = Depends(get_controller),
    current_user: Dict[str, Any] = Depends(get_current_user_dict)
) -> Dict[str, Any]:
    """Get salary component by ID"""
    logger.info(f"API: Getting salary component {component_id}")
    
    return await controller.get_component(
        component_id=component_id,
        current_user=convert_user_dict_to_object(current_user)
    )


@router.get("/code/{code}")
async def get_salary_component_by_code(
    code: str = Path(..., description="Component code"),
    controller: SalaryComponentController = Depends(get_controller),
    current_user: Dict[str, Any] = Depends(get_current_user_dict)
) -> Dict[str, Any]:
    """Get salary component by code"""
    logger.info(f"API: Getting salary component by code {code}")
    
    return await controller.get_component_by_code(
        code=code,
        current_user=convert_user_dict_to_object(current_user)
    )


@router.put("/{component_id}")
async def update_salary_component(
    component_id: str,
    dto: UpdateSalaryComponentDTO,
    controller: SalaryComponentController = Depends(get_controller),
    current_user: Dict[str, Any] = Depends(get_current_user_dict)
) -> Dict[str, Any]:
    """Update salary component"""
    logger.info(f"API: Updating salary component {component_id}")
    
    return await controller.update_component(
        component_id=component_id,
        dto=dto,
        current_user=convert_user_dict_to_object(current_user)
    )


@router.delete("/{component_id}")
async def delete_salary_component(
    component_id: str = Path(..., description="Component ID"),
    controller: SalaryComponentController = Depends(get_controller),
    current_user: Dict[str, Any] = Depends(get_current_user_dict)
) -> Dict[str, Any]:
    """Delete salary component"""
    logger.info(f"API: Deleting salary component {component_id}")
    
    return await controller.delete_component(
        component_id=component_id,
        current_user=convert_user_dict_to_object(current_user)
    )


@router.get("/")
async def search_salary_components(
    # Search parameters
    search_term: Optional[str] = Query(None, description="Search term"),
    component_type: Optional[str] = Query(None, description="Component type filter"),
    value_type: Optional[str] = Query(None, description="Value type filter"),
    is_taxable: Optional[bool] = Query(None, description="Taxable filter"),
    is_active: Optional[bool] = Query(True, description="Active filter"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    
    # Sort
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order"),
    
    controller: SalaryComponentController = Depends(get_controller),
    current_user: Dict[str, Any] = Depends(get_current_user_dict)
) -> Dict[str, Any]:
    """
    Search salary components with filters and pagination
    
    **Filters:**
    - search_term: Search in code, name, description
    - component_type: EARNING, DEDUCTION, BENEFIT
    - value_type: FIXED, PERCENTAGE, FORMULA
    - is_taxable: true/false
    - is_active: true/false
    
    **Pagination:**
    - page: Page number (starts from 1)
    - page_size: Items per page (1-100)
    
    **Sorting:**
    - sort_by: Field to sort by
    - sort_order: asc/desc
    """
    logger.info("API: Searching salary components")
    
    filters = SalaryComponentSearchFiltersDTO(
        search_term=search_term,
        component_type=component_type,
        value_type=value_type,
        is_taxable=is_taxable,
        is_active=is_active,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return await controller.search_components(
        filters=filters,
        current_user=convert_user_dict_to_object(current_user)
    )


@router.get("/active/all")
async def get_active_components(
    controller: SalaryComponentController = Depends(get_controller),
    current_user: Dict[str, Any] = Depends(get_current_user_dict)
) -> Dict[str, Any]:
    """Get all active salary components"""
    logger.info("API: Getting all active salary components")
    
    return await controller.get_active_components(
        current_user=convert_user_dict_to_object(current_user)
    )


@router.get("/type/{component_type}")
async def get_components_by_type(
    component_type: str = Path(..., description="Component type"),
    controller: SalaryComponentController = Depends(get_controller),
    current_user: Dict[str, Any] = Depends(get_current_user_dict)
) -> Dict[str, Any]:
    """Get components by type"""
    logger.info(f"API: Getting components by type {component_type}")
    
    return await controller.get_components_by_type(
        component_type=component_type,
        current_user=convert_user_dict_to_object(current_user)
    )


@router.post("/validate-formula")
async def validate_formula(
    request: FormulaValidationRequest,
    controller: SalaryComponentController = Depends(get_controller)
) -> Dict[str, Any]:
    """
    Validate a formula
    
    Request body:
    ```json
    {
        "formula": "BASIC * 0.5"
    }
    ```
    """
    logger.info("API: Validating formula")
    
    return await controller.validate_formula(formula=request.formula) 