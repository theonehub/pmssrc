import logging
from datetime import datetime
from models.reimbursements import ReimbursementRequestCreate    
from database.database_connector import connect_to_database

logger = logging.getLogger(__name__)

def get_reimbursement_collection(company_id: str):
    db = connect_to_database(company_id)
    return db["reimbursements"]

def get_assigned_reimbursements(emp_id: str, hostname: str):
    collection = get_reimbursement_collection(hostname)
    pipeline = [
        {"$match": {"emp_id": emp_id}},
        {"$lookup": {"from": "reimbursement_types", "localField": "reimbursement_type_ids", "foreignField": "reimbursement_type_id", "as": "reimbursement_types"}},
        {"$unwind": "$reimbursement_types"},
        {"$project": {"_id": 0, "reimbursement_type_id": "$reimbursement_types.reimbursement_type_id", "reimbursement_type_name": "$reimbursement_types.reimbursement_type_name"}}
    ]
    return list(collection.aggregate(pipeline))

def create_reimbursement(data: ReimbursementRequestCreate, hostname: str):
    collection = get_reimbursement_collection(hostname)
    return collection.insert_one(data)

def get_reimbursement_requests(emp_id: str, hostname: str):
    collection = get_reimbursement_collection(hostname)
    pipeline = [
        {"$match": {"emp_id": emp_id}},
        {"$lookup": {"from": "reimbursement_types", "localField": "reimbursement_type_ids", "foreignField": "reimbursement_type_id", "as": "reimbursement_types"}},
        {"$unwind": "$reimbursement_types"},
        {"$project": {"_id": 0, "reimbursement_type_id": "$reimbursement_types.reimbursement_type_id", "reimbursement_type_name": "$reimbursement_types.reimbursement_type_name"}},
        {"$sort": {"submitted_at": -1}}
    ]
    return collection.aggregate(pipeline).to_list(None)
