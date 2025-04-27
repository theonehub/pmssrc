from datetime import datetime
from bson import ObjectId
from database.database_connector import reimbursement_assignments_collection, user_collection, reimbursement_types_collection

async def assign_reimbursements_to_user(data):
    user_id = data["user_id"]
    existing = reimbursement_assignments_collection.find_one({"user_id": user_id})

    if existing:
        reimbursement_assignments_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "reimbursement_type_ids": data["reimbursement_type_ids"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
    else:
        new_data = {
            "user_id": user_id,
            "reimbursement_type_ids": data["reimbursement_type_ids"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        reimbursement_assignments_collection.insert_one(new_data)

async def get_user_reimbursement_assignments(user_id: str):
    return reimbursement_assignments_collection.find_one({"user_id": user_id})

async def get_all_user_reimbursement_assignments(skip: int = 0, limit: int = 10, search: str = None):
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
    assignment_lookup = {str(a["user_id"]): a["reimbursement_type_ids"] for a in assignments}

    response = []

    for user in users:
        user_id = str(user["_id"])
        assigned_ids = assignment_lookup.get(user_id, [])
        assigned_types = [
            {
                "type_id": tid,
                "name": type_lookup[tid]["name"],
                "description": type_lookup[tid].get("description", ""),
                "monthly_limit": type_lookup[tid].get("max_limit"),
                "required_docs": type_lookup[tid].get("required_docs", False)
            }
            for tid in assigned_ids if tid in type_lookup
        ]

        response.append({
            "id": user_id,
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