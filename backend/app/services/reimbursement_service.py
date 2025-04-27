from fastapi import UploadFile
from bson import ObjectId
from datetime import datetime
from typing import List
import os

from database.reimbursement_database import get_assigned_reimbursements, create_reimbursement, get_reimbursement_requests

async def get_assigned_types(emp_id: str, hostname: str):
    return get_assigned_reimbursements(emp_id, hostname)


async def save_file(file: UploadFile) -> str:
    filename = f"uploads/reimbursements/{datetime.now().timestamp()}_{file.filename}"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        content = file.read()
        f.write(content)
    return f"/{filename}"


async def submit_request(emp_id: str, data, hostname: str, file: UploadFile = None):
    file_url = save_file(file) if file else None
    request_doc = {
        "emp_id": emp_id,
        "reimbursement_type_id": data.reimbursement_type_id,
        "amount": data.amount,
        "note": data.note,
        "status": "Pending",
        "file_url": file_url,
        "submitted_at": datetime.now()
    }
    create_reimbursement(request_doc, hostname)
    return True


async def get_my_requests(emp_id: str, hostname: str):
    return get_reimbursement_requests(emp_id, hostname)
    
