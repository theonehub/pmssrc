from fastapi import UploadFile
from bson import ObjectId
from datetime import datetime
from typing import List
import os

from database.database_connector import reimbursement_assignments_collection, reimbursement_requests_collection


async def get_assigned_types(user_id: str):
    pipeline = [
        {"$match": {"employee_id": user_id}},
        {
            "$lookup": {
                "from": "reimbursement_types",
                "localField": "type_id",
                "foreignField": "_id",
                "as": "type"
            }
        },
        {"$unwind": "$type"},
        {"$project": {"_id": 0, "type_id": "$type._id", "name": "$type.name"}}
    ]
    return reimbursement_assignments_collection.aggregate(pipeline).to_list(None)


async def save_file(file: UploadFile) -> str:
    filename = f"uploads/reimbursements/{datetime.utcnow().timestamp()}_{file.filename}"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        content = file.read()
        f.write(content)
    return f"/{filename}"


async def submit_request(user_id: str, data, file: UploadFile = None):
    file_url = save_file(file) if file else None
    request_doc = {
        "employee_id": user_id,
        "type_id": ObjectId(data.type_id),
        "amount": data.amount,
        "note": data.note,
        "status": "Pending",
        "file_url": file_url,
        "submitted_at": datetime.utcnow()
    }
    reimbursement_requests_collection.insert_one(request_doc)
    return True


async def get_my_requests(user_id: str):
    pipeline = [
        {"$match": {"employee_id": user_id}},
        {
            "$lookup": {
                "from": "reimbursement_types",
                "localField": "type_id",
                "foreignField": "_id",
                "as": "type"
            }
        },
        {"$unwind": "$type"},
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "type_name": "$type.name",
                "amount": 1,
                "note": 1,
                "status": 1,
                "file_url": 1,
                "submitted_at": 1
            }
        },
        {"$sort": {"submitted_at": -1}}
    ]
    return reimbursement_requests_collection.aggregate(pipeline).to_list(None)
