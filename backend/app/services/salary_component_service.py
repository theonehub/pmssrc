import logging
from datetime import datetime
from fastapi import HTTPException, status
from database.salary_component_database import (
    create_salary_component_db,
    get_all_salary_components_db,
    get_salary_component_by_id_db,
    update_salary_component_db,
    delete_salary_component_db,
    create_salary_component_assignments_db,
    get_salary_component_assignments_db,
    create_salary_component_declarations_db,
    get_salary_component_declarations_db,
    serialize_salary_component
)
from models.salary_component import (
    SalaryComponentCreate,
    SalaryComponentUpdate,
    SalaryComponentInDB,
    SalaryComponentAssignment,
    SalaryComponentDeclaration
)
from typing import List

# Configure logger
logger = logging.getLogger(__name__)

async def create_salary_component(component: SalaryComponentCreate, hostname: str) -> SalaryComponentInDB:
    """
    Create a new salary component in the database.

    Args:
        component: SalaryComponentCreate Pydantic model with input data.
        hostname: The hostname to identify the database.

    Returns:
        SalaryComponentInDB: The created salary component.
    """
    logger.info("Creating a new salary component: %s", component.name)
    doc = await create_salary_component_db(component, hostname)
    return serialize_salary_component(doc)

async def get_all_salary_components(hostname: str) -> list[SalaryComponentInDB]:
    """
    Retrieve all salary components from the database.

    Args:
        hostname: The hostname to identify the database.

    Returns:
        List of SalaryComponentInDB
    """
    logger.info("Fetching all salary components")
    docs = await get_all_salary_components_db(hostname)
    results = [serialize_salary_component(doc) for doc in docs]
    logger.info("Fetched %d salary components", len(results))
    return results

async def get_salary_component_by_id(sc_id: str, hostname: str) -> SalaryComponentInDB:
    """
    Get a salary component by its ID.

    Args:
        sc_id: The ID of the component to fetch.
        hostname: The hostname to identify the database.

    Returns:
        SalaryComponentInDB
    """
    logger.info("Fetching salary component with ID: %s", sc_id)
    doc = await get_salary_component_by_id_db(sc_id, hostname)
    return serialize_salary_component(doc)

async def update_salary_component(sc_id: str, update_data: SalaryComponentUpdate, hostname: str) -> SalaryComponentInDB:
    """
    Update an existing salary component.

    Args:
        sc_id: ID of the component to update.
        update_data: Fields to update.
        hostname: The hostname to identify the database.

    Returns:
        Updated SalaryComponentInDB
    """
    logger.info("Updating salary component with ID: %s", sc_id)
    update_fields = {k: v for k, v in update_data.dict().items() if v is not None}
    if not update_fields:
        logger.warning("No valid fields to update for ID: %s", sc_id)
        raise HTTPException(status_code=400, detail="No fields to update")

    doc = await update_salary_component_db(sc_id, update_fields, hostname)
    return serialize_salary_component(doc)

async def delete_salary_component(sc_id: str, hostname: str) -> dict:
    """
    Delete a salary component from the database.

    Args:
        sc_id: ID of the component to delete.
        hostname: The hostname to identify the database.

    Returns:
        Dict with success message.
    """
    logger.info("Deleting salary component with ID: %s", sc_id)
    await delete_salary_component_db(sc_id, hostname)
    return {"msg": "Salary component deleted successfully"}

async def create_salary_component_assignments(emp_id: str, components: List[SalaryComponentAssignment], hostname: str) -> dict:
    """
    Create salary component assignments for an employee.
    Stores all components in a single document with the employee ID.

    Args:
        emp_id (str): Employee ID
        components (List[SalaryComponentAssignment]): List of components with min/max values
        hostname: The hostname to identify the database.

    Returns:
        dict: Created assignment document
    """
    try:
        logger.info(f"Creating salary component assignments for employee {emp_id}")
        
        # Convert Pydantic models to dictionaries
        components_array = [
            {
                "sc_id": str(component.sc_id),
                "max_value": float(component.max_value)
            }
            for component in components
        ]

        return await create_salary_component_assignments_db(emp_id, components_array, hostname)

    except Exception as e:
        logger.error(f"Error creating salary component assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating salary component assignments: {str(e)}"
        )

async def get_salary_component_assignments(emp_id: str, hostname: str) -> List[SalaryComponentInDB]:
    """
    Get salary component assignments for an employee.

    Args:
        emp_id (str): Employee ID
        hostname: The hostname to identify the database.

    Returns:
        List[SalaryComponentInDB]: List of assigned salary components with their values
    """
    try:
        assignments = await get_salary_component_assignments_db(emp_id, hostname)
        if not assignments:
            return []
        return [serialize_salary_component(assignment) for assignment in assignments]
        
    except Exception as e:
        logger.error(f"Error fetching salary component assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching salary component assignments: {str(e)}"
        )

async def create_salary_component_declarations(emp_id: str, components: List[SalaryComponentDeclaration], hostname: str) -> dict:
    """
    Create salary component declarations for an employee.
    Updates the declared_value in the existing assignments.

    Args:
        emp_id (str): Employee ID
        components (List[SalaryComponentDeclaration]): List of components with declared values
        hostname: The hostname to identify the database.

    Returns:
        dict: Updated assignment document
    """
    try:
        logger.info(f"Creating salary component declarations for employee {emp_id}")
        
        # Convert Pydantic models to dictionaries
        components_array = [
            {
                "sc_id": str(component.sc_id),
                "declared_value": float(component.declared_value)
            }
            for component in components
        ]

        return await create_salary_component_declarations_db(emp_id, components_array, hostname)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating salary component declarations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating salary component declarations: {str(e)}"
        )

async def get_salary_component_declarations(emp_id: str, hostname: str) -> List[dict]:
    """
    Get salary component declarations for an employee.

    Args:
        emp_id (str): Employee ID
        hostname: The hostname to identify the database.

    Returns:
        List[dict]: List of assigned salary components with their declared values
    """
    try:
        declarations = await get_salary_component_declarations_db(emp_id, hostname)
        if not declarations:
            return []
        return [serialize_salary_component(declaration) for declaration in declarations]
        
    except Exception as e:
        logger.error(f"Error fetching salary component declarations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching salary component declarations: {str(e)}"
        )


