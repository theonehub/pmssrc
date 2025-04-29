import logging
from fastapi import HTTPException
from models.company_leave import CompanyLeaveCreate, CompanyLeaveUpdate
from datetime import datetime
from database.company_leave_database import (
    create_leave as db_create_leave, 
    get_all_leaves as db_get_all_leaves, 
    get_leave_by_id as db_get_leave_by_id, 
    update_leave as db_update_leave, 
    delete_leave as db_delete_leave
)

logger = logging.getLogger(__name__)

def create_leave(leave_data: CompanyLeaveCreate, hostname: str):
    """
    Creates a new company leave.
    """
    try:
        doc = leave_data.model_dump()
        doc["created_at"] = datetime.now()
        leave_id_created = db_create_leave(doc, hostname)
        logger.info(f"Created company leave with ID: {leave_id_created}")
        return {"message": "Company leave created successfully", "leave_id": leave_id_created}
    except Exception as e:
        logger.error(f"Error creating company leave: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_all_leaves(hostname: str):
    """
    Retrieves all active company leaves.
    """
    try:
        leaves = db_get_all_leaves(hostname)
        processed_leaves = []
        for leave in leaves:
            if "_id" in leave:
                leave["_id"] = str(leave["_id"])
            processed_leaves.append(leave)
        logger.info(f"Retrieved {len(leaves)} company leaves")
        return processed_leaves
    except Exception as e:
        logger.error(f"Error retrieving company leaves: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_leave_by_id(leave_id: str, hostname: str):
    """
    Retrieves a specific company leave by its ID.
    """
    try:
        leave = db_get_leave_by_id(leave_id, hostname)
        if not leave:
            logger.warning(f"Company leave not found with ID: {leave_id}")
            return None
        if "_id" in leave:
            leave["_id"] = str(leave["_id"])
        logger.info(f"Retrieved company leave with ID: {leave_id}")
        return leave
    except Exception as e:
        logger.error(f"Error retrieving company leave: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def update_leave(leave_id: str, leave_data: CompanyLeaveUpdate, hostname: str):
    """
    Updates an existing company leave.
    """
    try:
        update_data = {k: v for k, v in leave_data.model_dump(exclude_unset=True).items()}
        was_updated = db_update_leave(leave_id, update_data, hostname)
        if not was_updated:
            logger.warning(f"Company leave not found with ID: {leave_id} or no changes made.")
            return False
        logger.info(f"Updated company leave with ID: {leave_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating company leave: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def delete_leave(leave_id: str, hostname: str):
    """
    Soft deletes a company leave.
    """
    try:
        was_deleted = db_delete_leave(leave_id, hostname)
        if not was_deleted:
            logger.warning(f"Company leave not found with ID: {leave_id}")
            return False
        logger.info(f"Deleted company leave with ID: {leave_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting company leave: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 