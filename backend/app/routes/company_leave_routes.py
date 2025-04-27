from fastapi import APIRouter, Depends, HTTPException
from models.company_leave import CompanyLeaveCreate, CompanyLeaveUpdate
from services import company_leave_service
from models.user_model import User
from auth.auth import get_current_user, extract_hostname, role_checker

router = APIRouter(prefix="/company-leaves", tags=["Company Leaves"])

@router.post("/")
async def create_leave(data: CompanyLeaveCreate, 
                       role: str = Depends(role_checker(["superadmin", "admin"])), 
                       hostname: str = Depends(extract_hostname)):
    return await company_leave_service.create_leave(data, hostname)

@router.get("/")
async def list_leaves(hostname: str = Depends(extract_hostname)):
    return await company_leave_service.get_all_leaves(hostname)

@router.get("/{leave_id}")
async def get_leave(leave_id: str, 
                    hostname: str = Depends(extract_hostname),
                    role: str = Depends(role_checker(["user", "manager", "admin", "superadmin"]))):
    leave = await company_leave_service.get_leave_by_id(leave_id, hostname)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    return leave

@router.put("/{leave_id}")
async def update_leave(leave_id: str, data: CompanyLeaveUpdate, 
                       hostname: str = Depends(extract_hostname),
                       role: str = Depends(role_checker(["superadmin", "admin"]))):
    leave = await company_leave_service.get_leave_by_id(leave_id, hostname)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    await company_leave_service.update_leave(leave_id, data, hostname)
    return {"message": "Leave updated successfully"}

@router.delete("/{leave_id}")
async def delete_leave(leave_id: str, 
                      hostname: str = Depends(extract_hostname),
                      role: str = Depends(role_checker(["superadmin"]))):
    leave = await company_leave_service.get_leave_by_id(leave_id, hostname)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    await company_leave_service.delete_leave(leave_id, hostname)
    return {"message": "Leave deleted successfully"} 