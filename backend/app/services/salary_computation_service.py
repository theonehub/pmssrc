import logging
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from typing import List
from models.salary_component import SalaryComponentBase
# Configure logger
logger = logging.getLogger(__name__)

def get_salary_computation(emp_id: str, hostname: str) -> dict:
    """
    Get salary computation for a specific employee.

    Args:
        emp_id (str): Employee ID

    Returns:
        Dict with salary computation details
    """ 
    logger.info("API Call: Get salary computation for employee with ID: %s", emp_id)
    # Get employee details
    salary = get_salary_computation(emp_id, hostname)
    if not salary:
        raise HTTPException(status_code=404, detail="Salary computation not found")
    
    return {"message": "Salary computation retrieved successfully"}

