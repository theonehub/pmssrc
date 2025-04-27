from fastapi import APIRouter, Depends, Query
from typing import List
from auth.auth import get_current_user
from models.reimbursement_assignment import (
    ReimbursementAssignmentCreate,
    ReimbursementAssignmentOut,
    PaginatedReimbursementAssignmentOut
)
from services.reimbursement_assignment_service import assign_reimbursements_to_user, get_user_reimbursement_assignments, get_all_user_reimbursement_assignments

router = APIRouter(prefix="/reimbursements/assignment", tags=["Reimbursement Assignments"])

@router.post("/assign")
async def assign_reimbursements(payload: ReimbursementAssignmentCreate):
    await assign_reimbursements_to_user(payload)
    return {"msg": "Reimbursements assigned successfully"}

@router.get("/user/{emp_id}", dependencies=[Depends(get_current_user)])
async def get_user_assignments(emp_id: str):
    data = await get_user_reimbursement_assignments(emp_id)
    return data or {}

@router.get("/all", response_model=PaginatedReimbursementAssignmentOut)
async def get_all_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None)
):
    return await get_all_user_reimbursement_assignments(skip, limit, search)