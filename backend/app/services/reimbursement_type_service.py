from database.database_connector import reimbursement_types_collection
from models.reimbursement_type import ReimbursementTypeCreate, ReimbursementTypeUpdate
from bson import ObjectId
from datetime import datetime

async def create_type(data: ReimbursementTypeCreate):
    doc = data.dict()
    doc["created_at"] = datetime.utcnow()
    result = reimbursement_types_collection.insert_one(doc)
    return str(result.inserted_id)

async def get_all_types():
    types = reimbursement_types_collection.find().to_list(1000)
    for t in types:
        t["id"] = str(t["_id"])
        del t["_id"]
    return types

async def update_type(type_id: str, data: ReimbursementTypeUpdate):
    reimbursement_types_collection.update_one(
        {"_id": ObjectId(type_id)},
        {"$set": data.dict(exclude_unset=True)},
    )

async def delete_type(type_id: str):
    reimbursement_types_collection.delete_one({"_id": ObjectId(type_id)})
