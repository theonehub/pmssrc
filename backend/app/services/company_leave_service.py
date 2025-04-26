from database import company_leave_collection
from models.company_leave import CompanyLeaveCreate, CompanyLeaveUpdate
from bson import ObjectId
from datetime import datetime

async def create_leave(data: CompanyLeaveCreate):
    doc = data.model_dump()
    doc["created_at"] = datetime.now()
    result = company_leave_collection.insert_one(doc)
    return str(result.inserted_id)

async def get_all_leaves():
    cursor = company_leave_collection.find()
    leaves = list(cursor)
    for leave in leaves:
        del leave["_id"]
    return leaves

async def get_leave_by_id(leave_id: str):
    leave = await company_leave_collection.find_one({"leave_id": leave_id})
    if leave:
        del leave["_id"]
    return leave

async def update_leave(leave_id: str, data: CompanyLeaveUpdate):
    update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
    await company_leave_collection.update_one(
        {"leave_id": leave_id},
        {"$set": update_data},
    )

async def delete_leave(leave_id: str):
    await company_leave_collection.delete_one({"leave_id": leave_id}) 