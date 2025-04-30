from fastapi import APIRouter, Depends, HTTPException
from models.company_leave import CompanyLeaveCreate, CompanyLeaveUpdate
from services import company_leave_service
from auth.auth import extract_hostname, role_checker

router = APIRouter(prefix="/company-leaves", tags=["Company Leaves"])

@router.post("/")
def create_leave(data: CompanyLeaveCreate, 
                       role: str = Depends(role_checker(["superadmin", "admin"])), 
                       hostname: str = Depends(extract_hostname)):
    print(data)
    return company_leave_service.create_leave(data, hostname)

@router.get("/")
def list_leaves(hostname: str = Depends(extract_hostname)):
    return company_leave_service.get_all_leaves(hostname)

@router.get("/{leave_id}")
def get_leave(leave_id: str, 
                    hostname: str = Depends(extract_hostname),
                    role: str = Depends(role_checker(["user", "manager", "admin", "superadmin"]))):
    leave = company_leave_service.get_leave_by_id(leave_id, hostname)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    return leave

@router.put("/{leave_id}")
def update_leave(leave_id: str, data: CompanyLeaveUpdate, 
                       hostname: str = Depends(extract_hostname),
                       role: str = Depends(role_checker(["superadmin", "admin"]))):
    existing_leave = company_leave_service.get_leave_by_id(leave_id, hostname)
    if not existing_leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    updated = company_leave_service.update_leave(leave_id, data, hostname)
    if not updated:
        raise HTTPException(status_code=304, detail="Leave not modified")
    return {"message": "Leave updated successfully"}

@router.delete("/{leave_id}")
def delete_leave(leave_id: str, 
                      hostname: str = Depends(extract_hostname),
                      role: str = Depends(role_checker(["superadmin"]))):
    existing_leave = company_leave_service.get_leave_by_id(leave_id, hostname)
    if not existing_leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    company_leave_service.delete_leave(leave_id, hostname)
    return {"message": "Leave deleted successfully"} 