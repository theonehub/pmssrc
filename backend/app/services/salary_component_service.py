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

def create_salary_component(component: SalaryComponentCreate, hostname: str) -> SalaryComponentInDB:
    """
    Create a new salary component in the database.

    Args:
        component: SalaryComponentCreate Pydantic model with input data.
        hostname: The hostname to identify the database.

    Returns:
        SalaryComponentInDB: The created salary component.
    """
    logger.info("Creating a new salary component: %s", component.name)
    doc = create_salary_component_db(component, hostname)
    return serialize_salary_component(doc)

def get_all_salary_components(hostname: str) -> list[SalaryComponentInDB]:
    """
    Retrieve all salary components from the database.

    Args:
        hostname: The hostname to identify the database.

    Returns:
        List of SalaryComponentInDB
    """
    logger.info("Fetching all salary components")
    docs = get_all_salary_components_db(hostname)
    results = [serialize_salary_component(doc) for doc in docs]
    logger.info("Fetched %d salary components", len(results))
    return results

def get_salary_component_by_id(sc_id: str, hostname: str) -> SalaryComponentInDB:
    """
    Get a salary component by its ID.

    Args:
        sc_id: The ID of the component to fetch.
        hostname: The hostname to identify the database.

    Returns:
        SalaryComponentInDB
    """
    logger.info("Fetching salary component with ID: %s", sc_id)
    doc = get_salary_component_by_id_db(sc_id, hostname)
    return serialize_salary_component(doc)

def update_salary_component(sc_id: str, update_data: SalaryComponentUpdate, hostname: str) -> SalaryComponentInDB:
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

    doc = update_salary_component_db(sc_id, update_fields, hostname)
    return serialize_salary_component(doc)

def delete_salary_component(sc_id: str, hostname: str) -> dict:
    """
    Delete a salary component from the database.

    Args:
        sc_id: ID of the component to delete.
        hostname: The hostname to identify the database.

    Returns:
        Dict with success message.
    """
    logger.info("Deleting salary component with ID: %s", sc_id)
    delete_salary_component_db(sc_id, hostname)
    return {"msg": "Salary component deleted successfully"}

def create_salary_component_assignments(emp_id: str, components: List[SalaryComponentAssignment], hostname: str) -> dict:
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

        return create_salary_component_assignments_db(emp_id, components_array, hostname)

    except Exception as e:
        logger.error(f"Error creating salary component assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating salary component assignments: {str(e)}"
        )

def get_salary_component_assignments(emp_id: str, hostname: str) -> List[SalaryComponentInDB]:
    """
    Get salary component assignments for an employee.

    Args:
        emp_id (str): Employee ID
        hostname: The hostname to identify the database.

    Returns:
        List[SalaryComponentInDB]: List of assigned salary components with their values
    """
    try:
        assignments = get_salary_component_assignments_db(emp_id, hostname)
        if not assignments:
            return []
        return [serialize_salary_component(assignment) for assignment in assignments]
        
    except Exception as e:
        logger.error(f"Error fetching salary component assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching salary component assignments: {str(e)}"
        )

def create_salary_component_declarations(emp_id: str, components: List[SalaryComponentDeclaration], hostname: str) -> dict:
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

        return create_salary_component_declarations_db(emp_id, components_array, hostname)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating salary component declarations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating salary component declarations: {str(e)}"
        )

def get_salary_component_declarations(emp_id: str, hostname: str) -> List[dict]:
    """
    Get salary component declarations for an employee.

    Args:
        emp_id (str): Employee ID
        hostname: The hostname to identify the database.

    Returns:
        List[dict]: List of assigned salary components with their declared values
    """
    try:
        declarations = get_salary_component_declarations_db(emp_id, hostname)
        if not declarations:
            return []
        return [serialize_salary_component(declaration) for declaration in declarations]
        
    except Exception as e:
        logger.error(f"Error fetching salary component declarations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching salary component declarations: {str(e)}"
        )

def import_salary_component_assignments_from_file(assignments_data: list, hostname: str) -> dict:
    """
    Import salary component assignments from a file.
    
    Args:
        assignments_data (list): List of dictionaries containing assignment data
            Expected format:
            [
                {
                    "emp_id": "employee_id",
                    "sc_id": "salary_component_id",
                    "max_value": 5000.0
                },
                ...
            ]
        hostname (str): The hostname to identify the database.
        
    Returns:
        dict: Summary of import results
    """
    logger.info(f"Importing salary component assignments from file")
    
    try:
        # Track import statistics
        stats = {
            "total": len(assignments_data),
            "imported": 0,
            "failed": 0,
            "errors": []
        }
        
        # Group assignments by employee
        employee_assignments = {}
        for row in assignments_data:
            # Validate required fields
            if not all(key in row for key in ["emp_id", "sc_id", "max_value"]):
                error_msg = f"Missing required fields in row: {row}"
                stats["errors"].append(error_msg)
                stats["failed"] += 1
                logger.error(error_msg)
                continue
                
            emp_id = str(row["emp_id"])
            sc_id = str(row["sc_id"])
            
            # Validate salary component exists
            try:
                get_salary_component_by_id_db(sc_id, hostname)
            except HTTPException as e:
                error_msg = f"Invalid salary component ID {sc_id} for employee {emp_id}: {str(e)}"
                stats["errors"].append(error_msg)
                stats["failed"] += 1
                logger.error(error_msg)
                continue
            
            # Convert max_value to float
            try:
                max_value = float(row["max_value"])
                if max_value < 0:
                    raise ValueError("Max value must be non-negative")
            except (ValueError, TypeError) as e:
                error_msg = f"Invalid max_value for employee {emp_id}, component {sc_id}: {str(e)}"
                stats["errors"].append(error_msg)
                stats["failed"] += 1
                logger.error(error_msg)
                continue
            
            # Group by employee
            if emp_id not in employee_assignments:
                employee_assignments[emp_id] = []
                
            employee_assignments[emp_id].append({
                "sc_id": sc_id,
                "max_value": max_value
            })
        
        # Process each employee's assignments
        for emp_id, components in employee_assignments.items():
            try:
                create_salary_component_assignments_db(emp_id, components, hostname)
                stats["imported"] += len(components)
            except Exception as e:
                error_msg = f"Failed to create assignments for employee {emp_id}: {str(e)}"
                stats["errors"].append(error_msg)
                stats["failed"] += len(components)
                logger.error(error_msg)
        
        logger.info(f"Import complete: {stats['imported']} imported, {stats['failed']} failed")
        return stats
        
    except Exception as e:
        logger.error(f"Error importing salary component assignments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error importing salary component assignments: {str(e)}"
        )


