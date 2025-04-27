import logging
from datetime import datetime
from models.company_leave import CompanyLeaveCreate, CompanyLeaveUpdate
from database.database_connector import connect_to_database

logger = logging.getLogger(__name__)

async def get_company_leave_collection(hostname: str):
    """
    Returns the company leave collection for the specified company.
    """
    db = connect_to_database(hostname)
    return db["company_leaves"]

async def create_leave(leave_data: dict, hostname: str):
    """
    Creates a new company leave record.
    """
    collection = await get_company_leave_collection(hostname)
    
    now = datetime.now()
    leave_id = f"CL-{now.strftime('%Y%m%d%H%M%S')}"
    
    leave_dict = {
        "leave_id": leave_id,
        "name": leave_data["name"],
        "description": leave_data.get("description", ""),
        "start_date": leave_data["start_date"],
        "end_date": leave_data["end_date"],
        "created_at": now,
        "is_active": True
    }
    
    result = await collection.insert_one(leave_dict)
    return leave_id

async def get_all_leaves(hostname: str):
    """
    Retrieves all active company leaves.
    """
    collection = await get_company_leave_collection(hostname)
    leaves = []
    cursor = collection.find({"is_active": True})
    async for doc in cursor:
        leaves.append(CompanyLeave(**doc))
    return leaves

async def get_leave_by_id(leave_id: str, hostname: str):
    """
    Retrieves a specific company leave by its ID.
    """
    collection = await get_company_leave_collection(hostname)
    doc = await collection.find_one({"leave_id": leave_id, "is_active": True})
    if doc:
        return CompanyLeave(**doc)
    return None

async def update_leave(leave_id: str, leave_data: dict, hostname: str):
    """
    Updates an existing company leave.
    Returns True if a document was updated, False otherwise.
    """
    collection = await get_company_leave_collection(hostname)
    
    update_dict = {
        "name": leave_data["name"],
        "description": leave_data.get("description", ""),
        "start_date": leave_data["start_date"],
        "end_date": leave_data["end_date"]
    }
    
    result = await collection.update_one(
        {"leave_id": leave_id},
        {"$set": update_dict}
    )
    
    return result.matched_count > 0

async def delete_leave(leave_id: str, hostname: str):
    """
    Soft deletes a company leave by setting is_active to False.
    Returns True if a document was updated, False otherwise.
    """
    collection = await get_company_leave_collection(hostname)
    
    result = await collection.update_one(
        {"leave_id": leave_id},
        {"$set": {"is_active": False}}
    )
    
    return result.matched_count > 0 