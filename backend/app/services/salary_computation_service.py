import logging
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from database.database_connector import salary_component_assignments_collection, user_collection
import uuid
from typing import List
from models.salary_component import SalaryComponentBase
# Configure logger
logger = logging.getLogger(__name__)

async def get_salary_computation(emp_id: str) -> dict:
    """
    Get salary computation for a specific employee.

    Args:
        emp_id (str): Employee ID

    Returns:
        Dict with salary computation details
    """ 
    logger.info("API Call: Get salary computation for employee with ID: %s", emp_id)
    try:
        # Get employee details
        employee = user_collection.find_one({"emp_id": emp_id})
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get salary component assignments
        assignments = salary_component_assignments_collection.find_one({"emp_id": emp_id})
        if not assignments:
            raise HTTPException(status_code=404, detail="Salary component assignments not found")
        
        components = assignments.get("components", [])

        logger.info("Employee details: %s", employee)
        logger.info("Salary component assignments: %s", assignments)
        logger.info("Salary components: %s", components)
        for component in components:
            logger.info("Component: %s", component)
        logger.info("Salary component assignments retrieved successfully")
    except Exception as e:
        logger.error("Error retrieving salary computation: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


    return {"message": "Salary computation retrieved successfully"}

