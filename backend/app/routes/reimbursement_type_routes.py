from fastapi import APIRouter, Depends, HTTPException
from models.reimbursement_type import ReimbursementTypeCreate, ReimbursementTypeUpdate
from services import reimbursement_type_service
from auth.auth import extract_hostname, role_checker

router = APIRouter(prefix="/reimbursement-types", tags=["Reimbursement Types"])

@router.post("/")
async def create_type(data: ReimbursementTypeCreate, 
                      hostname: str = Depends(extract_hostname),
                      role: str = Depends(role_checker(["superadmin"]))):
    return await reimbursement_type_service.create_type(data, hostname)

@router.get("/")
async def list_types(hostname: str = Depends(extract_hostname),
                     role: str = Depends(role_checker(["superadmin", "user"]))):
    return await reimbursement_type_service.get_all_types(hostname)

@router.put("/{type_id}")
async def update_type(type_id: str, data: ReimbursementTypeUpdate,
                      hostname: str = Depends(extract_hostname),
                      role: str = Depends(role_checker(["superadmin"]))):
    await reimbursement_type_service.update_type(type_id, data, hostname)
    return {"message": "Updated"}

@router.delete("/{type_id}")
async def delete_type(type_id: str,
                      hostname: str = Depends(extract_hostname),
                      role: str = Depends(role_checker(["superadmin"]))):
    await reimbursement_type_service.delete_type(type_id)
    
    return {"message": "Deleted"}
