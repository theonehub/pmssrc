from fastapi import APIRouter, Depends, status
from models.salary_component import (
    SalaryComponentCreate,
    SalaryComponentUpdate,
    SalaryComponentInDB
)
from services.salary_component_service import (
    create_salary_component,
    get_all_salary_components,
    get_salary_component_by_id,
    update_salary_component,
    delete_salary_component
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
    logger.info("API Call: Create salary component")
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
