from fastapi import APIRouter, Depends, HTTPException
from models.reimbursement_type import ReimbursementTypeCreate, ReimbursementTypeUpdate
from services import reimbursement_type_service
from models.user_model import User
from auth.auth import get_current_user

router = APIRouter(prefix="/reimbursement-types", tags=["Reimbursement Types"])

@router.post("/")
async def create_type(data: ReimbursementTypeCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    return await reimbursement_type_service.create_type(data)

@router.get("/")
async def list_types(current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin" and current_user.role != "user":
        raise HTTPException(status_code=403, detail="Access denied")
    return await reimbursement_type_service.get_all_types()

@router.put("/{type_id}")
async def update_type(type_id: str, data: ReimbursementTypeUpdate,current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin" or current_user.role != "user":
        raise HTTPException(status_code=403, detail="Access denied")
    await reimbursement_type_service.update_type(type_id, data)
    
    return {"message": "Updated"}

@router.delete("/{type_id}")
async def delete_type(type_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    await reimbursement_type_service.delete_type(type_id)
    
    return {"message": "Deleted"}
