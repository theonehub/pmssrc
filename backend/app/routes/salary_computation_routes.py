from fastapi import APIRouter, Depends, status, HTTPException
from auth.auth import extract_emp_id
from services.salary_computation_service import get_salary_computation

from typing import List
import logging

router = APIRouter(prefix="/salary-computation", tags=["Salary Computation"])

logger = logging.getLogger(__name__)

@router.get("/")
async def salary_computation(emp_id: str = Depends(extract_emp_id)):
    return await get_salary_computation(emp_id)