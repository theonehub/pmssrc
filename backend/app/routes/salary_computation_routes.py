from fastapi import APIRouter, Depends, status, HTTPException
from auth.auth import extract_emp_id, extract_hostname
from services.salary_computation_service import get_salary_computation

from typing import List
import logging

router = APIRouter(prefix="/salary-computation", tags=["Salary Computation"])

logger = logging.getLogger(__name__)

@router.get("/")
def salary_computation(emp_id: str = Depends(extract_emp_id), hostname: str = Depends(extract_hostname)):
    return get_salary_computation(emp_id, hostname)