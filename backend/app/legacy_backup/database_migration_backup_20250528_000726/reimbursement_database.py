import logging
from datetime import datetime
from models.reimbursements import ReimbursementRequestCreate    
from database.database_connector import connect_to_database
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

def get_reimbursement_collection(company_id: str):
    db = connect_to_database(company_id)
    return db["reimbursements"]

def create_reimbursement(data: dict, hostname: str):
    collection = get_reimbursement_collection(hostname)
    return collection.insert_one(data)

def get_reimbursement_requests(employee_id: str, hostname: str):
    try:
        collection = get_reimbursement_collection(hostname)
        pipeline = [
            {"$match": {"employee_id": employee_id}},
            {"$lookup": {
                "from": "reimbursement_types",
                "localField": "reimbursement_type_id",
                "foreignField": "reimbursement_type_id",
                "as": "type_info"
            }},
            {"$unwind": {
                "path": "$type_info",
                "preserveNullAndEmptyArrays": True
            }},
            {"$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "type_name": "$type_info.reimbursement_type_name",
                "reimbursement_type_id": 1,
                "amount": 1,
                "note": 1,
                "status": 1,
                "file_url": 1,
                "created_at": 1
            }},
            {"$sort": {"created_at": -1}}
        ]
        results = list(collection.aggregate(pipeline))
        logger.info(f"Found {len(results)} reimbursement requests for employee_id: {employee_id}")
        return results
    except Exception as e:
        logger.error(f"Error fetching reimbursement requests: {str(e)}")
        raise

def update_reimbursement(reimbursement_id: str, data: dict, hostname: str):
    try:
        collection = get_reimbursement_collection(hostname)
        result = collection.update_one(
            {"_id": ObjectId(reimbursement_id)},
            {"$set": data}
        )
        if result.matched_count == 0:
            raise Exception("Reimbursement request not found")
        return True
    except Exception as e:
        logger.error(f"Error updating reimbursement request: {str(e)}")
        raise

def delete_reimbursement(reimbursement_id: str, hostname: str):
    try:
        collection = get_reimbursement_collection(hostname)
        result = collection.delete_one({"_id": ObjectId(reimbursement_id)})
        if result.deleted_count == 0:
            raise Exception("Reimbursement request not found")
        return True
    except Exception as e:
        logger.error(f"Error deleting reimbursement request: {str(e)}")
        raise

def get_pending_reimbursements(hostname: str, manager_id: str = None):
    try:
        collection = get_reimbursement_collection(hostname)
        
        pipeline = [
            {"$match": {"status": "PENDING"}},
            {"$lookup": {
                "from": "users",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee_info"
            }},
            {"$unwind": {
                "path": "$employee_info",
                "preserveNullAndEmptyArrays": True
            }},
            {"$lookup": {
                "from": "reimbursement_types",
                "localField": "reimbursement_type_id",
                "foreignField": "reimbursement_type_id",
                "as": "type_info"
            }},
            {"$unwind": {
                "path": "$type_info",
                "preserveNullAndEmptyArrays": True
            }},
            {"$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "employee_id": 1,
                "employee_name": {"$concat": ["$employee_info.first_name", " ", "$employee_info.last_name"]},
                "type_name": "$type_info.reimbursement_type_name",
                "reimbursement_type_id": 1,
                "amount": 1,
                "note": 1,
                "status": 1,
                "comments": 1,
                "file_url": 1,
                "created_at": 1
            }},
            {"$sort": {"created_at": -1}}
        ]
        
        # If manager_id is provided, filter for employees under this manager
        if manager_id:
            # Insert an additional match at the beginning that filters by manager_id
            # This requires that users have a manager_id field
            pipeline.insert(1, {
                "$match": {
                    "$or": [
                        {"employee_info.manager_id": manager_id},
                        {"employee_info.employee_id": manager_id}  # Include manager's own requests
                    ]
                }
            })
            
        results = list(collection.aggregate(pipeline))
        logger.info(f"Found {len(results)} pending reimbursement requests")
        return results
    except Exception as e:
        logger.error(f"Error fetching pending reimbursement requests: {str(e)}")
        raise

def update_reimbursement_status(reimbursement_id: str, status: str, comments: str, hostname: str):
    try:
        collection = get_reimbursement_collection(hostname)
        update_data = {
            "status": status,
            "comments": comments,
            "updated_at": datetime.now()
        }
        
        result = collection.update_one(
            {"_id": ObjectId(reimbursement_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise Exception("Reimbursement request not found")
            
        return True
    except Exception as e:
        logger.error(f"Error updating reimbursement status: {str(e)}")
        raise

def get_approved_reimbursements(hostname: str, manager_id: str = None):
    try:
        collection = get_reimbursement_collection(hostname)
        
        pipeline = [
            {"$match": {"status": "APPROVED"}},
            {"$lookup": {
                "from": "users",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee_info"
            }},
            {"$unwind": {
                "path": "$employee_info",
                "preserveNullAndEmptyArrays": True
            }},
            {"$lookup": {
                "from": "reimbursement_types",
                "localField": "reimbursement_type_id",
                "foreignField": "reimbursement_type_id",
                "as": "type_info"
            }},
            {"$unwind": {
                "path": "$type_info",
                "preserveNullAndEmptyArrays": True
            }},
            {"$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "employee_id": 1,
                "employee_name": {"$concat": ["$employee_info.first_name", " ", "$employee_info.last_name"]},
                "type_name": "$type_info.reimbursement_type_name",
                "reimbursement_type_id": 1,
                "amount": 1,
                "note": 1,
                "status": 1,
                "comments": 1,
                "file_url": 1,
                "created_at": 1
            }},
            {"$sort": {"created_at": -1}}
        ]
        
        # If manager_id is provided, filter for employees under this manager
        if manager_id:
            # Insert an additional match at the beginning that filters by manager_id
            # This requires that users have a manager_id field
            pipeline.insert(1, {
                "$match": {
                    "$or": [
                        {"employee_info.manager_id": manager_id},
                        {"employee_info.employee_id": manager_id}  # Include manager's own requests
                    ]
                }
            })
            
        results = list(collection.aggregate(pipeline))
        logger.info(f"Found {len(results)} approved reimbursement requests")
        return results
    except Exception as e:
        logger.error(f"Error fetching approved reimbursement requests: {str(e)}")
        raise
