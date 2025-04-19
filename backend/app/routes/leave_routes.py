from fastapi import APIRouter, Depends, HTTPException
from models.leave_model import EmployeeLeave, LeaveStatus
from services.employee_leave_service import apply_leave, get_user_leaves, get_pending_leaves, update_leave_status
from auth.auth import get_current_user
from typing import List

router = APIRouter()

@router.post("/apply", response_model=dict)
async def create_leave_application(leave: EmployeeLeave, current_user: dict = Depends(get_current_user)):
    """
    Create a new leave application.
    """
    # Set the empId from current user
    leave.empId = current_user["empId"]
    return apply_leave(leave)

@router.get("/my-leaves", response_model=List[dict])
async def get_my_leaves(current_user: dict = Depends(get_current_user)):
    """
    Get all leave applications for the current user.
    """
    return get_user_leaves(current_user["empId"])

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
    current_user: dict = Depends(get_current_user)
):
    """
    Update the status of a leave application (approve/reject).
    """
    if current_user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can update leave status")
    return update_leave_status(leave_id, status, current_user["empId"]) 