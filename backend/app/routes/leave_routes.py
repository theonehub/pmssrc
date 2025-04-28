from fastapi import APIRouter, Depends, HTTPException
from models.user_model import User
from models.leave_model import EmployeeLeave, LeaveStatus
from services.employee_leave_service import apply_leave, get_user_leaves, get_pending_leaves, update_leave_status, leave_balance, delete_leave_request, get_all_employee_leaves, get_leaves_by_month_for_user, calculate_lwp_for_month
from auth.auth import extract_emp_id, get_current_user
from typing import List
from auth.auth import role_checker, extract_hostname

router = APIRouter(prefix="/leaves")

@router.post("/apply", response_model=dict)
async def create_leave_application(leave: EmployeeLeave, 
                                    emp_id: str = Depends(extract_emp_id),
                                    hostname: str = Depends(extract_hostname)):
    """
    Create a new leave application.
    """
    # Set the emp_id from current user
    leave.emp_id = emp_id
    print(leave)
    return apply_leave(leave, hostname)

@router.get("/leave-balance", response_model=dict)
async def get_leave_balance(emp_id: str = Depends(extract_emp_id), 
                            hostname: str = Depends(extract_hostname)):
    """
    Get the leave balance for the current user.
    """
    return leave_balance(emp_id, hostname)

@router.get("/my-leaves", response_model=List[dict])
async def get_my_leaves(emp_id: str = Depends(extract_emp_id), 
                        hostname: str = Depends(extract_hostname)):
    """
    Get all leave applications for the current user.
    """
    leaves = get_user_leaves(emp_id, hostname)
    return leaves

@router.get("/pending", response_model=List[dict])
async def get_manager_pending_leaves(emp_id: str = Depends(extract_emp_id),     
                                     hostname: str = Depends(extract_hostname),
                                     role: str = Depends(role_checker("manager"))):
    """
    Get all pending leave applications for users under the current manager.
    """
    return get_pending_leaves(emp_id, hostname)

@router.put("/{leave_id}/status", response_model=dict)
async def update_leave_application_status(
    leave_id: str,
    status: LeaveStatus,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "superadmin"]))
):
    """
    Update the status of a leave application (approve/reject).
    """
    return update_leave_status(leave_id, status, emp_id, hostname)

@router.delete("/{leave_id}", response_model=dict)
async def delete_leave_application(leave_id: str, 
                                   emp_id: str = Depends(extract_emp_id),
                                   hostname: str = Depends(extract_hostname)):
    """
    Delete a leave application by its ID.
    """
    return delete_leave_request(leave_id, hostname)

@router.get("/all", response_model=List[dict])
async def get_all_leaves(
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "superadmin"]))
):
    """
    Get all leaves for employees under the manager or all employees for superadmin.
    """
    if role == "manager":
        return get_all_employee_leaves(hostname=hostname, manager_id=emp_id)
    else:  # superadmin
        return get_all_employee_leaves(hostname=hostname)
    
@router.get("/user/{emp_id}/{month}/{year}", response_model=List[dict])
async def get_user_leaves_by_month(emp_id: str, month: int, year: int,
                                   hostname: str = Depends(extract_hostname)):
    """
    Get all leaves for a specific employee in a specific month and year.
    """
    return get_leaves_by_month_for_user(emp_id, month, year, hostname)

@router.get("/lwp/{emp_id}/{month}/{year}")
async def get_lwp(emp_id: str, month: int, year: int,
                  hostname: str = Depends(extract_hostname)):
    """
    Get Leave Without Pay (LWP) days for a specific month and year.
    LWP is calculated for days where the employee is:
    1. Absent without leave
    2. Has pending leave
    3. Has rejected leave
    Excludes weekends and public holidays.
    """
    try:
        lwp_days = calculate_lwp_for_month(emp_id, month, year, hostname)
        return {"lwp_days": lwp_days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
