from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import List

from auth.auth import extract_hostname, extract_emp_id
from services import reimbursement_service as service
from models.reimbursements import ReimbursementRequestCreate, ReimbursementRequestOut

router = APIRouter(prefix="/reimbursements", tags=["Reimbursements"])


@router.get("/assigned")
async def get_assigned_reimbursement_types(emp_id: str = Depends(extract_emp_id),
                                           hostname: str = Depends(extract_hostname)):
    return await service.get_assigned_types(emp_id, hostname)


@router.post("/request")
async def submit_reimbursement_request(
    type_id: str = Form(...),
    amount: float = Form(...),
    note: str = Form(""),
    file: UploadFile = File(None),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    data = ReimbursementRequestCreate(type_id=type_id, amount=amount, note=note, emp_id=emp_id)
    await service.submit_request(emp_id, data, hostname,file)
    return {
        "message": "Request submitted successfully"
    }


@router.get("/my-requests")
async def get_my_requests(emp_id: str = Depends(extract_emp_id),
                         hostname: str = Depends(extract_hostname)):
    return await service.get_my_requests(emp_id, hostname)
