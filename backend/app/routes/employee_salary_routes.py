from fastapi import APIRouter, HTTPException, status
from models.employee_salary import (
    EmployeeSalaryCreate,
    EmployeeSalaryUpdate,
    EmployeeSalaryInDB,
    BulkEmployeeSalaryAssignRequest,
    EmployeeSalaryWithComponentName
)
from services import employee_salary_service
from typing import List
from pydantic import BaseModel

router = APIRouter(
    prefix="/employee-salary",
    tags=["Employee Salary"]
)

# 👇 New request schema for bulk assignment
class EmployeeSalaryBulkAssignRequest(BaseModel):
    components: List[EmployeeSalaryCreate]

@router.post("/", response_model=EmployeeSalaryInDB, status_code=status.HTTP_201_CREATED)
async def create_employee_salary(data: EmployeeSalaryCreate):
    """
    Create a single salary component entry for an employee.
    """
    try:
        return await employee_salary_service.create_employee_salary(data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{employee_id}", response_model=List[EmployeeSalaryInDB])
async def get_employee_salary_by_employee_id(employee_id: str):
    """
    Get all salary components assigned to a specific employee.
    """
    try:
        return await employee_salary_service.get_employee_salary_by_employee_id(employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{salary_id}", response_model=EmployeeSalaryInDB)
async def update_employee_salary(salary_id: str, data: EmployeeSalaryUpdate):
    """
    Update an employee's salary component details.
    """
    try:
        return await employee_salary_service.update_employee_salary(salary_id, data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{salary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee_salary(salary_id: str):
    """
    Delete an employee's salary component entry.
    """
    try:
        await employee_salary_service.delete_employee_salary(salary_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{employee_id}", response_model=dict)
async def check_salary_assignment_status(employee_id: str):
    """
    Check if salary components are already assigned to the employee.
    """
    try:
        assigned_components = await employee_salary_service.get_employee_salary_by_employee_id(employee_id)
        is_assigned = len(assigned_components) > 0
        return {
            "is_assigned": is_assigned,
            "assigned_components": assigned_components if is_assigned else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ NEW ENDPOINT: Bulk salary structure assignment
@router.post("/{employee_id}/salary-structure", status_code=status.HTTP_200_OK)
async def assign_salary_structure(employee_id: str, request: BulkEmployeeSalaryAssignRequest):
    """
    Bulk assign salary components to an employee (insert or update).
    """
    print("Received employee_id:", employee_id)
    print("Received components:", request.components)
    try:
        await employee_salary_service.assign_salary_structure(employee_id, request.components)
        return {"message": "Salary structure updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    


@router.get("/{employee_id}/salary-structure", response_model=List[EmployeeSalaryInDB])
async def get_salary_structure(employee_id: str):
    """
    Get full salary structure assigned to an employee.
    """
    try:
        return await employee_salary_service.get_employee_salary_by_employee_id(employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{employee_id}/salary-structure/view", response_model=List[EmployeeSalaryWithComponentName])
async def get_salary_structure_for_view(employee_id: str):
    """
    View-only endpoint for salary structure (with component names).
    """
    try:
        return await employee_salary_service.get_salary_structure_with_names(employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))