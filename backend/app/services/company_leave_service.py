from database import company_leave_collection
from models.company_leave import CompanyLeaveCreate, CompanyLeaveUpdate
from bson import ObjectId
from datetime import datetime

async def create_leave(data: CompanyLeaveCreate):
    doc = data.dict()
    doc["created_at"] = datetime.utcnow()
    result = company_leave_collection.insert_one(doc)
    return str(result.inserted_id)

def get_all_leaves():
    cursor = company_leave_collection.find().to_list(length=1000)
    leaves = []
    for leave in cursor:
        leave["id"] = str(leave["_id"])
        del leave["_id"]
        leaves.append(leave)
    return leaves

async def get_leave_by_id(leave_id: str):
    leave = await company_leave_collection.find_one({"_id": ObjectId(leave_id)})
    if leave:
        leave["id"] = str(leave["_id"])
        del leave["_id"]
    return leave

async def update_leave(leave_id: str, data: CompanyLeaveUpdate):
    update_data = {k: v for k, v in data.dict(exclude_unset=True).items()}
    await company_leave_collection.update_one(
        {"_id": ObjectId(leave_id)},
        {"$set": update_data},
    )

async def delete_leave(leave_id: str):
    await company_leave_collection.delete_one({"_id": ObjectId(leave_id)}) 