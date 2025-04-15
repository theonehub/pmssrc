from fastapi import APIRouter, Depends
from typing import List
from auth.auth import get_current_user
from models.reimbursement_assignment import ReimbursementAssignmentCreate, ReimbursementAssignmentOut
from services import reimbursement_assignment_service

router = APIRouter(prefix="/reimbursements/assignment", tags=["Reimbursement Assignments"])

@router.post("/assign")
async def assign_reimbursements(payload: ReimbursementAssignmentCreate):
    print(payload)
    await reimbursement_assignment_service.assign_reimbursements_to_user(payload.dict())
    return {"msg": "Reimbursements assigned successfully"}

@router.get("/user/{user_id}", dependencies=[Depends(get_current_user)])
async def get_user_assignments(user_id: str):
    data = await reimbursement_assignment_service.get_user_reimbursement_assignments(user_id)
    return data or {}

@router.get("/all", response_model=List[ReimbursementAssignmentOut])
async def get_all_assignments():
    return await reimbursement_assignment_service.get_all_user_reimbursement_assignments()