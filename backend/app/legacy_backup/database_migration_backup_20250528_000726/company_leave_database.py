import logging
from datetime import datetime
# from models.company_leave import CompanyLeaveCreate, CompanyLeaveUpdate # Model conversion should happen in service/route
from database.database_connector import connect_to_database
import uuid

logger = logging.getLogger(__name__)

def get_company_leave_collection(hostname: str):
    """
    Returns the company leave collection for the specified company.
    """
    db = connect_to_database(hostname)
    return db["company_leaves"]

def create_leave(leave_data: dict, hostname: str):
    """
    Creates a new company leave record.
    """
    collection = get_company_leave_collection(hostname)
    
    if not leave_data.get("company_leave_id"):
        leave_id = str(uuid.uuid4())
    else:
        leave_id = leave_data["company_leave_id"]
    
    # Use the structure from the Pydantic model CompanyLeaveCreate for consistency
    leave_dict = {
        "company_leave_id": leave_id,
        "name": leave_data["name"],
        "count": leave_data["count"],
        "is_active": leave_data.get("is_active", True) # Use provided value or default to True
        # Add created_at if needed by schema/model
    }
    
    result = collection.insert_one(leave_dict)
    return leave_id

def get_all_leaves(hostname: str):
    """
    Retrieves all active company leaves.
    """
    collection = get_company_leave_collection(hostname)
    leaves = []
    cursor = collection.find({"is_active": True})
    for doc in cursor:
        leaves.append(doc)
    return leaves

def get_leave_by_id(leave_id: str, hostname: str):
    """
    Retrieves a specific company leave by its ID.
    """
    collection = get_company_leave_collection(hostname)
    # Ensure we query by the correct field, seems like it should be company_leave_id based on frontend changes and create_leave
    doc = collection.find_one({"company_leave_id": leave_id, "is_active": True})
    # Return the raw dictionary, let the service/route handle model conversion
    # Also removed the CompanyLeave(**doc) conversion which was incorrect
    return doc

def update_leave(leave_id: str, leave_data: dict, hostname: str):
    """
    Updates an existing company leave.
    Returns True if a document was updated, False otherwise.
    """
    collection = get_company_leave_collection(hostname)
    
    # Use CompanyLeaveUpdate structure - get only fields present in leave_data
    update_dict = {}
    if "name" in leave_data:
        update_dict["name"] = leave_data["name"]
    if "count" in leave_data:
        update_dict["count"] = leave_data["count"]
    if "is_active" in leave_data:
        update_dict["is_active"] = leave_data["is_active"]
    # Add updated_at timestamp if needed

    if not update_dict: # Don't update if no fields were provided
        return False

    result = collection.update_one(
        {"company_leave_id": leave_id}, # Query by company_leave_id
        {"$set": update_dict}
    )
    
    return result.matched_count > 0

def delete_leave(leave_id: str, hostname: str):
    """
    Soft deletes a company leave by setting is_active to False.
    Returns True if a document was updated, False otherwise.
    """
    collection = get_company_leave_collection(hostname)
    
    result = collection.update_one(
        {"company_leave_id": leave_id},
        {"$set": {"is_active": False}}
    )
    
    return result.matched_count > 0 