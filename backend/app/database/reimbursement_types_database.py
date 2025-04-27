import logging
from datetime import datetime
from models.reimbursement_type import ReimbursementTypeCreate, ReimbursementTypeUpdate
from database.database_connector import connect_to_database

logger = logging.getLogger(__name__)

def get_reimbursement_types_collection(company_id: str):
    db = connect_to_database(company_id)
    return db["reimbursement_types"]

async def create_type(data: ReimbursementTypeCreate, hostname: str):
    collection = get_reimbursement_types_collection(hostname)
    doc = data.model_dump()
    doc["created_at"] = datetime.now()
    result = collection.insert_one(doc)
    return str(result.inserted_id)
    
async def get_all_types(hostname: str):
    collection = get_reimbursement_types_collection(hostname)
    types = collection.find()
    return list(types)

async def update_type(type_id: str, data: ReimbursementTypeUpdate, hostname: str):
    collection = get_reimbursement_types_collection(hostname)
    collection.update_one(
        {"reimbursement_type_id": type_id},
        {"$set": data.model_dump(exclude_unset=True)},
    )
    return True

async def delete_type(type_id: str, hostname: str):
    collection = get_reimbursement_types_collection(hostname)
    collection.delete_one({"reimbursement_type_id": type_id})
    return True