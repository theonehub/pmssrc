from fastapi import APIRouter, Depends, HTTPException
from models.company_leave import CompanyLeaveCreate, CompanyLeaveUpdate
from services import company_leave_service
from models.user_model import User
from auth.auth import get_current_user

router = APIRouter(prefix="/company-leaves", tags=["Company Leaves"])

@router.post("/")
async def create_leave(data: CompanyLeaveCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    return await company_leave_service.create_leave(data)

@router.get("/")
async def list_leaves(current_user: User = Depends(get_current_user)):
    return await company_leave_service.get_all_leaves()

@router.get("/{leave_id}")
async def get_leave(leave_id: str, current_user: User = Depends(get_current_user)):
    leave = await company_leave_service.get_leave_by_id(leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    return leave

@router.put("/{leave_id}")
async def update_leave(leave_id: str, data: CompanyLeaveUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    leave = await company_leave_service.get_leave_by_id(leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    await company_leave_service.update_leave(leave_id, data)
    return {"message": "Leave updated successfully"}

@router.delete("/{leave_id}")
async def delete_leave(leave_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    leave = await company_leave_service.get_leave_by_id(leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    await company_leave_service.delete_leave(leave_id)
    return {"message": "Leave deleted successfully"} 