from fastapi import APIRouter, Depends, status, HTTPException
from auth.auth import extract_empId, get_current_user

from models.salary_component import (
    SalaryComponentCreate,
    SalaryComponentUpdate,
    SalaryComponentInDB,
    SalaryComponentAssignmentRequest,
    SalaryComponentDeclarationRequest
)
from services.salary_component_service import (
    create_salary_component,
    get_all_salary_components,
    get_salary_component_by_id,
    update_salary_component,
    delete_salary_component,
    get_salary_component_assignments,
    create_salary_component_assignments,
    get_salary_component_declarations,
    create_salary_component_declarations
)
from typing import List
import logging

router = APIRouter(prefix="/salary-components", tags=["Salary Components"])

# Logger configuration
logger = logging.getLogger(__name__)

@router.post("/", response_model=SalaryComponentInDB, status_code=status.HTTP_201_CREATED)
async def create_component(component: SalaryComponentCreate):
    """
    Endpoint to create a new salary component.

    Args:
        component (SalaryComponentCreate): Input data for new component.

    Returns:
        The created SalaryComponentInDB object.
    """
    logger.info("API Call: Create salary component", component)
    return await create_salary_component(component)


@router.get("/", response_model=List[SalaryComponentInDB])
async def list_components():
    """
    Endpoint to retrieve all salary components.

    Returns:
        List of all salary components.
    """
    logger.info("API Call: Get all salary components")
    return await get_all_salary_components()


@router.get("/{sc_id}", response_model=SalaryComponentInDB)
async def get_component(sc_id: str):
    """
    Endpoint to get a salary component by its ID.

    Args:
        sc_id (str): MongoDB ID of the component.

    Returns:
        The SalaryComponentInDB object if found.
    """
    logger.info("API Call: Get salary component with ID: %s", sc_id)
    return await get_salary_component_by_id(sc_id)


@router.put("/{sc_id}", response_model=SalaryComponentInDB)
async def update_component(sc_id: str, update_data: SalaryComponentUpdate):
    """
    Endpoint to update a salary component by ID.

    Args:
        sc_id (str): MongoDB ID of the component.
        update_data (SalaryComponentUpdate): Data to update.

    Returns:
        Updated SalaryComponentInDB object.
    """
    logger.info("API Call: Update salary component with ID: %s", sc_id)
    return await update_salary_component(sc_id, update_data)


@router.delete("/{sc_id}")
async def delete_component(sc_id: str):
    """
    Endpoint to delete a salary component by ID.

    Args:
        sc_id (str): MongoDB ID of the component.

    Returns:
        Confirmation message.
    """
    logger.info("API Call: Delete salary component with ID: %s", sc_id)
    return await delete_salary_component(sc_id)


@router.get("/assignments/{emp_id}", response_model=List[SalaryComponentInDB])
async def salary_component_assignments(emp_id: str):
    """
    Endpoint to get salary component assignments for a specific employee.

    Args:
        emp_id (str): Employee ID.

    Returns:
        List of salary component assignments.
    """
    logger.info("API Call: Get salary component assignments for employee with ID: %s", emp_id)
    return await get_salary_component_assignments(emp_id)


@router.post("/assignments/{emp_id}", status_code=status.HTTP_201_CREATED)
async def salary_component_assignments(
    emp_id: str,
    assignment_data: SalaryComponentAssignmentRequest
):
    """
    Endpoint to create salary component assignments for a specific employee.

    Args:
        emp_id (str): Employee ID
        assignment_data (SalaryComponentAssignmentRequest): List of components with min/max values

    Returns:
        Dict with success message and assigned components
    """
    logger.info("API Call: Create salary component assignments for employee with ID: %s", emp_id)
    result = await create_salary_component_assignments(emp_id, assignment_data.components)
    return {"message": "Components assigned successfully", "assignments": result}


@router.get("/declarations/self", response_model=List[SalaryComponentInDB])
async def get_salary_declarations(emp_id: str = Depends(extract_empId)):
    """
    Endpoint to get salary component declarations for the current user.

    Returns:
        List of salary component declarations.
    """
    logger.info("API Call: Get salary component declarations for current user")
    return await get_salary_component_declarations(emp_id)


@router.post("/declarations/self", status_code=status.HTTP_201_CREATED)
async def create_salary_declarations(
    declaration_data: SalaryComponentDeclarationRequest,
    emp_id: str = Depends(extract_empId)
):
    """
    Endpoint to create salary component declarations for the current user.

    Args:
        declaration_data (SalaryComponentDeclarationRequest): List of components with declared values

    Returns:
        Dict with success message and declared components
    """
    logger.info("API Call: Create salary component declarations for current user")
    result = await create_salary_component_declarations(emp_id, declaration_data.components)
    return {"message": "Components declared successfully", "declarations": result}
