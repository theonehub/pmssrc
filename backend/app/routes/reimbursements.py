from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import List

from auth.auth import get_current_user
from services import reimbursements as service
from models.reimbursements import ReimbursementRequestCreate, ReimbursementRequestOut

router = APIRouter(prefix="/reimbursements", tags=["Reimbursements"])


@router.get("/assigned", dependencies=[Depends(get_current_user)])
async def get_assigned_reimbursement_types(user=Depends(get_current_user)):
    return await service.get_assigned_types(str(user.id))


@router.post("/request", dependencies=[Depends(get_current_user)])
async def submit_reimbursement_request(
    type_id: str = Form(...),
    amount: float = Form(...),
    note: str = Form(""),
    file: UploadFile = File(None),
    user=Depends(get_current_user)
):
    data = ReimbursementRequestCreate(type_id=type_id, amount=amount, note=note)
    await service.submit_request(str(user.id), data, file)
    return {"message": "Request submitted successfully"}


@router.get("/my-requests", response_model=List[ReimbursementRequestOut], dependencies=[Depends(get_current_user)])
async def get_my_requests(user=Depends(get_current_user)):
    return await service.get_my_requests(str(user.id))
