import logging
from datetime import datetime
from models.reimbursement_assignment import ReimbursementAssignmentCreate
from database.database_connector import connect_to_database

logger = logging.getLogger(__name__)

def get_reimbursement_assignments_collection(company_id: str):
    db = connect_to_database(company_id)
    return db["reimbursement_assignments"]

def get_user_collection(company_id: str):
    db = connect_to_database(company_id)
    return db["users"]

def get_reimbursement_types_collection(company_id: str):
    db = connect_to_database(company_id)
    return db["reimbursement_types"]

def create_assignment(data: ReimbursementAssignmentCreate, hostname: str):
    collection = get_reimbursement_assignments_collection(hostname)
    employee_id = data["employee_id"]
    existing = collection.find_one({"employee_id": employee_id})

    if existing:
        collection.update_one(
            {"employee_id": employee_id},
            {
                "$set": {
                    "reimbursement_type_ids": data["reimbursement_type_ids"],
                    "updated_at": datetime.now()
                }
            }
        )
    else:
        new_data = {
            "employee_id": employee_id,
            "reimbursement_type_ids": data["reimbursement_type_ids"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        collection.insert_one(new_data)
    return True

def get_user_assignments(employee_id: str, hostname: str):
    collection = get_reimbursement_assignments_collection(hostname)
    assignments = collection.find_one({"employee_id": employee_id})
    return assignments

def get_all_assignments(skip: int = 0, limit: int = 10, search: str = None, hostname: str = None):
    reimbursement_assignments_collection = get_reimbursement_assignments_collection(hostname)
    user_collection = get_user_collection(hostname)
    reimbursement_types_collection = get_reimbursement_types_collection(hostname)
     # Build the query for search
    query = {}
    if search:
        query = {
            "$or": [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        }

    # Get total count for pagination
    total_users = user_collection.count_documents(query)
    
    # Get paginated users
    users = user_collection.find(query).skip(skip).limit(limit).to_list(length=None)
    assignments = reimbursement_assignments_collection.find().to_list(length=None)
    types = reimbursement_types_collection.find().to_list(length=None)

    type_lookup = {str(rt["_id"]): rt for rt in types}
    assignment_lookup = {str(a["employee_id"]): a["reimbursement_type_ids"] for a in assignments}

    response = []

    for user in users:
        employee_id = str(user["employee_id"])
        assigned_ids = assignment_lookup.get(employee_id, [])
        assigned_types = [
            {
                "reimbursement_type_id": tid,
                "name": type_lookup[tid]["name"],
                "description": type_lookup[tid].get("description", ""),
                "monthly_limit": type_lookup[tid].get("max_limit"),
                "required_docs": type_lookup[tid].get("required_docs", False)
            }
            for tid in assigned_ids if tid in type_lookup
        ]

        response.append({
            "employee_id": employee_id,
            "name": user["name"],
            "email": user.get("email", ""),
            "assigned_reimbursements": assigned_types
        })

    return {
        "data": response,
        "total": total_users,
        "page": skip // limit + 1,
        "page_size": limit
    }                  