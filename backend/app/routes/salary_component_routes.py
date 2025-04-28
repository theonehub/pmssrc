from fastapi import APIRouter, Depends, status, HTTPException
from auth.auth import extract_emp_id, extract_hostname
from typing import List
from models.salary_component import (
    SalaryComponentCreate,
    SalaryComponentUpdate,
    SalaryComponentInDB,
    SalaryComponentAssignment,
    SalaryComponentDeclaration
)
from services.salary_component_service import (
    create_salary_component,
    get_all_salary_components,
    get_salary_component_by_id,
    update_salary_component,
    delete_salary_component,
    create_salary_component_assignments,
    get_salary_component_assignments,
    create_salary_component_declarations,
    get_salary_component_declarations
)
import logging

router = APIRouter(prefix="/salary-components", tags=["Salary Components"])

# Logger configuration
logger = logging.getLogger(__name__)

@router.post("/", response_model=SalaryComponentInDB, status_code=status.HTTP_201_CREATED)
async def create_component(
    component: SalaryComponentCreate,
    hostname: str = Depends(extract_hostname)
):
    """
    Create a new salary component.
    """
    logger.info("API Call: Create salary component", component)
    return await create_salary_component(component, hostname)

@router.get("/", response_model=List[SalaryComponentInDB])
async def get_components(hostname: str = Depends(extract_hostname)):
    """
    Get all salary components.
    """
    logger.info("API Call: Get all salary components")
    return await get_all_salary_components(hostname)

@router.get("/{sc_id}", response_model=SalaryComponentInDB)
async def get_component(
    sc_id: str,
    hostname: str = Depends(extract_hostname)
):
    """
    Get a specific salary component by ID.
    """
    logger.info("API Call: Get salary component with ID: %s", sc_id)
    return await get_salary_component_by_id(sc_id, hostname)

@router.put("/{sc_id}", response_model=SalaryComponentInDB)
async def update_component(
    sc_id: str,
    component: SalaryComponentUpdate,
    hostname: str = Depends(extract_hostname)
):
    """
    Update a salary component.
    """
    logger.info("API Call: Update salary component with ID: %s", sc_id)
    return await update_salary_component(sc_id, component, hostname)

@router.delete("/{sc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_component(
    sc_id: str,
    hostname: str = Depends(extract_hostname)
):
    """
    Delete a salary component.
    """
    logger.info("API Call: Delete salary component with ID: %s", sc_id)
    await delete_salary_component(sc_id, hostname)
    return None

@router.post("/assignments/{emp_id}", status_code=status.HTTP_201_CREATED)
async def create_assignments(
    emp_id: str,
    components: List[SalaryComponentAssignment],
    hostname: str = Depends(extract_hostname)
):
    """
    Create salary component assignments for an employee.
    """
    logger.info("API Call: Create salary component assignments for employee with ID: %s", emp_id)
    return await create_salary_component_assignments(emp_id, components, hostname)

@router.get("/assignments/{emp_id}", response_model=List[SalaryComponentInDB])
async def get_assignments(
    emp_id: str,
    hostname: str = Depends(extract_hostname)
):
    """
    Get salary component assignments for an employee.
    """
    logger.info("API Call: Get salary component assignments for employee with ID: %s", emp_id)
    return await get_salary_component_assignments(emp_id, hostname)

@router.post("/declarations/{emp_id}", status_code=status.HTTP_201_CREATED)
async def create_declarations(
    emp_id: str,
    components: List[SalaryComponentDeclaration],
    hostname: str = Depends(extract_hostname)
):
    """
    Create salary component declarations for an employee.
    """
    logger.info("API Call: Create salary component declarations for employee with ID: %s", emp_id)
    return await create_salary_component_declarations(emp_id, components, hostname)

@router.get("/declarations/{emp_id}")
async def get_declarations(
    emp_id: str,
    hostname: str = Depends(extract_hostname)
):
    """
    Get salary component declarations for an employee.
    """
    logger.info("API Call: Get salary component declarations for employee with ID: %s", emp_id)
    return await get_salary_component_declarations(emp_id, hostname)

