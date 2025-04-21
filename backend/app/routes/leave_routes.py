from fastapi import APIRouter, Depends, HTTPException
from models.user_model import User
from models.leave_model import EmployeeLeave, LeaveStatus
from services.employee_leave_service import apply_leave, get_user_leaves, get_pending_leaves, update_leave_status, leave_balance, delete_leave_request, get_all_employee_leaves, get_leaves_by_month_for_user, calculate_lwp_for_month
from auth.auth import extract_empId, get_current_user
from typing import List
from auth.dependencies import role_checker

router = APIRouter(prefix="/leaves")

@router.post("/apply", response_model=dict)
async def create_leave_application(leave: EmployeeLeave, empId: str = Depends(extract_empId)):
    """
    Create a new leave application.
    """
    # Set the empId from current user
    leave.empId = empId
    print(leave)
    return apply_leave(leave)

@router.get("/leave-balance", response_model=dict)
async def get_leave_balance(empId: str = Depends(extract_empId)):
    """
    Get the leave balance for the current user.
    """
    return leave_balance(empId)

@router.get("/my-leaves", response_model=List[dict])
async def get_my_leaves(empId: str = Depends(extract_empId)):
    """
    Get all leave applications for the current user.
    """
    leaves = get_user_leaves(empId)
    return leaves

@router.get("/pending", response_model=List[dict])
async def get_manager_pending_leaves(current_user: dict = Depends(get_current_user)):
    """
    Get all pending leave applications for users under the current manager.
    """
    if current_user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can view pending leaves")
    return get_pending_leaves(current_user["empId"])

@router.put("/{leave_id}/status", response_model=dict)
async def update_leave_application_status(
    leave_id: str,
    status: LeaveStatus,
    current_user: User = Depends(get_current_user)
):
    """
    Update the status of a leave application (approve/reject).
    """
    if current_user.role != "manager" and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only managers can update leave status")
    return update_leave_status(leave_id, status, current_user.empId)

@router.delete("/{leave_id}", response_model=dict)
async def delete_leave_application(leave_id: str, empId: str = Depends(extract_empId)):
    """
    Delete a leave application by its ID.
    """
    return delete_leave_request(leave_id)

@router.get("/all", response_model=List[dict])
async def get_all_leaves(
    current_user: dict = Depends(get_current_user),
    role: str = Depends(role_checker("manager", "superadmin"))
):
    """
    Get all leaves for employees under the manager or all employees for superadmin.
    """
    if role == "manager":
        return get_all_employee_leaves(manager_id=current_user["empId"])
    else:  # superadmin
        return get_all_employee_leaves()
    
@router.get("/user/{empId}/{month}/{year}", response_model=List[dict])
async def get_user_leaves_by_month(empId: str, month: int, year: int):
    """
    Get all leaves for a specific employee in a specific month and year.
    """
    return get_leaves_by_month_for_user(empId, month, year)

@router.get("/lwp/{empId}/{month}/{year}")
async def get_lwp(empId: str, month: int, year: int):
    """
    Get Leave Without Pay (LWP) days for a specific month and year.
    LWP is calculated for days where the employee is:
    1. Absent without leave
    2. Has pending leave
    3. Has rejected leave
    Excludes weekends and public holidays.
    """
    try:
        lwp_days = calculate_lwp_for_month(empId, month, year)
        return {"lwp_days": lwp_days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
