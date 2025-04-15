from fastapi import APIRouter, Depends
from typing import List
from auth.auth import get_current_user
from models.salary_declaration import SalaryDeclarationCreate, SalaryDeclarationResponse
from services.salary_declaration_service import (
    get_assigned_components_for_employee,
    submit_salary_declaration
)

router = APIRouter()

@router.get("/employee/salary-components", response_model=List[dict])
async def get_employee_components(user=Depends(get_current_user)):
    return await get_assigned_components_for_employee(user)

@router.post("/employee/declare", response_model=SalaryDeclarationResponse)
async def declare_salary_component(payload: SalaryDeclarationCreate, user=Depends(get_current_user)):
    return await submit_salary_declaration(user, payload)
