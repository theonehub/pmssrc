from fastapi import UploadFile
from bson import ObjectId
from datetime import datetime
from typing import List
import os
import logging

from database.reimbursement_database import (
    create_reimbursement, 
    get_reimbursement_requests,
    update_reimbursement,
    delete_reimbursement,
    get_pending_reimbursements,
    update_reimbursement_status,
    get_approved_reimbursements
)

logger = logging.getLogger(__name__)

def save_file(file: UploadFile) -> str:
    try:
        filename = f"uploads/reimbursements/{datetime.now().timestamp()}_{file.filename}"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        content = file.read()
        with open(filename, "wb") as f:
            f.write(content)
        return f"/{filename}"
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise


def submit_request(emp_id: str, data, hostname: str, file: UploadFile = None):
    try:
        file_url = save_file(file) if file else None
        request_doc = {
            "emp_id": emp_id,
            "reimbursement_type_id": data.reimbursement_type_id,
            "amount": float(data.amount),
            "note": data.note,
            "status": "PENDING",
            "file_url": file_url,
            "created_at": datetime.now()
        }
        result = create_reimbursement(request_doc, hostname)
        logger.info(f"Created reimbursement request for emp_id: {emp_id}")
        return True
    except Exception as e:
        logger.error(f"Error submitting reimbursement request: {str(e)}")
        raise


def get_my_requests(emp_id: str, hostname: str):
    try:
        results = get_reimbursement_requests(emp_id, hostname)
        return results
    except Exception as e:
        logger.error(f"Error getting reimbursement requests: {str(e)}")
        raise

def update_request(request_id: str, data, hostname: str, file: UploadFile = None):
    try:
        update_data = {
            "reimbursement_type_id": data.reimbursement_type_id,
            "amount": float(data.amount),
            "note": data.note,
            "updated_at": datetime.now()
        }
        
        if file:
            file_url = save_file(file)
            update_data["file_url"] = file_url
            
        result = update_reimbursement(request_id, update_data, hostname)
        logger.info(f"Updated reimbursement request {request_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating reimbursement request: {str(e)}")
        raise

def delete_request(request_id: str, hostname: str):
    try:
        result = delete_reimbursement(request_id, hostname)
        logger.info(f"Deleted reimbursement request {request_id}")
        return result
    except Exception as e:
        logger.error(f"Error deleting reimbursement request: {str(e)}")
        raise

def get_pending_requests(hostname: str, manager_id: str = None):
    try:
        results = get_pending_reimbursements(hostname, manager_id)
        return results
    except Exception as e:
        logger.error(f"Error getting pending reimbursement requests: {str(e)}")
        raise

def update_request_status(request_id: str, status: str, comments: str, hostname: str):
    try:
        result = update_reimbursement_status(request_id, status, comments, hostname)
        logger.info(f"Updated reimbursement request {request_id} to status {status}")
        return result
    except Exception as e:
        logger.error(f"Error updating reimbursement status: {str(e)}")
        raise

def get_approved_requests(hostname: str, manager_id: str = None):
    try:
        results = get_approved_reimbursements(hostname, manager_id)
        return results
    except Exception as e:
        logger.error(f"Error getting approved reimbursement requests: {str(e)}")
        raise
    
