from fastapi import APIRouter, Depends, UploadFile, File, Form, Body
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import List

from auth.auth import extract_hostname, extract_emp_id, role_checker
from services import reimbursement_service as service
from models.reimbursements import ReimbursementRequestCreate, ReimbursementRequestOut, ReimbursementStatusUpdate

router = APIRouter(prefix="/reimbursements", tags=["Reimbursements"])

@router.post("/")
def submit_reimbursement_request(
    reimbursement_type_id: str = Form(...),
    amount: float = Form(...),
    note: str = Form(""),
    file: UploadFile = File(None),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    try:
        data = ReimbursementRequestCreate(
            reimbursement_type_id=reimbursement_type_id,
            amount=amount,
            note=note,
            emp_id=emp_id
        )
        service.submit_request(emp_id, data, hostname, file)
        return {
            "message": "Request submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-requests")
def get_my_requests(
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    try:
        results = service.get_my_requests(emp_id, hostname)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{request_id}")
def update_reimbursement_request(
    request_id: str,
    reimbursement_type_id: str = Form(...),
    amount: float = Form(...),
    note: str = Form(""),
    file: UploadFile = File(None),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    try:
        data = ReimbursementRequestCreate(
            reimbursement_type_id=reimbursement_type_id,
            amount=amount,
            note=note,
            emp_id=emp_id
        )
        service.update_request(request_id, data, hostname, file)
        return {
            "message": "Request updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{request_id}")
def delete_reimbursement_request(
    request_id: str,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    try:
        service.delete_request(request_id, hostname)
        return {
            "message": "Request deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending")
def get_pending_reimbursements(
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"]))
):
    try:
        # For manager, we want to filter by their managed employees
        # For admin/superadmin, we want all pending requests
        manager_id = emp_id if role == "manager" else None
        results = service.get_pending_requests(hostname, manager_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{request_id}/status")
def update_reimbursement_status(
    request_id: str,
    data: ReimbursementStatusUpdate,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"]))
):
    try:
        service.update_request_status(
            request_id, 
            data.status.value,
            data.comments, 
            hostname
        )
        return {
            "message": f"Request status updated to {data.status.value}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approved")
def get_approved_reimbursements(
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"]))
):
    try:
        # For manager, we want to filter by their managed employees
        # For admin/superadmin, we want all approved requests
        manager_id = emp_id if role == "manager" else None
        results = service.get_approved_requests(hostname, manager_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
