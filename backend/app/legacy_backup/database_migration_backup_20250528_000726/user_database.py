from fastapi import HTTPException
from auth.password_handler import hash_password
from models.user_model import UserInfo
import logging
from database.database_connector import connect_to_database

logger = logging.getLogger(__name__)


def get_user_collection(company_id: str):
    db = connect_to_database(company_id)
    return db["users_info"]


def create_user(user: UserInfo, hostname: str):
    """
    Creates a new user in the database.
    """
    logger.info(f"Creating user: {user.employee_id}")
    collection = get_user_collection(hostname)
    user_result = collection.insert_one(user.model_dump())
    logger.info(f"User created successfully, inserted_id: {user_result.inserted_id}")
    return {"msg": "User created successfully", "inserted_id": str(user_result.inserted_id)}

def get_all_users(hostname: str):
    """
    Returns all users from user_collection.
    """
    collection = get_user_collection(hostname)
    users = collection.find()
    users = list(users)
    logger.info("Fetched all users, count: %d", len(users))
    return users

def get_users_stats(hostname: str):
    """
    Returns a dictionary with user count grouped by role.
    Example: {"Admin": 5, "Employee": 12}
    """
    collection = get_user_collection(hostname)
    
    pipeline = [
        {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ]
    results = list(collection.aggregate(pipeline))

    stats = {item["_id"]: item["count"] for item in results}
    logger.info("User stats: %s", stats)
    
    return stats


def get_user_by_employee_id(employee_id: str, hostname: str):
    """
    Returns user info for a user by employee_id.
    """
    collection = get_user_collection(hostname)
    user = collection.find_one({"employee_id": employee_id})
    return user

def get_users_by_manager_id(manager_id: str, hostname: str):
    """
    Returns user info for a user by manager_id.
    """
    collection = get_user_collection(hostname)
    users = collection.find({"manager_id": manager_id})
    return users

def get_employee_ids_by_manager_id(manager_id: str, hostname: str):
    """
    Returns all employee IDs for a given manager ID.
    """
    collection = get_user_collection(hostname)
    users = collection.find({"manager_id": manager_id}, {"_id": 0, "employee_id": 1})
    return [user["employee_id"] for user in users]

def update_user(employee_id: str, user: UserInfo, hostname: str):
    """
    Updates an existing user in the database.
    """
    logger.info(f"Updating user: {employee_id}")
    collection = get_user_collection(hostname)
    
    # Check if user exists
    existing_user = collection.find_one({"employee_id": employee_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare update data (exclude employee_id and created_at from updates)
    update_data = user.model_dump(exclude_unset=True)
    if 'employee_id' in update_data:
        del update_data['employee_id']  # Don't allow employee_id to be updated
    
    # Hash password if it's being updated
    if 'password' in update_data and update_data['password']:
        update_data['password'] = hash_password(update_data['password'])
    
    # Add updated_at timestamp
    from datetime import datetime
    update_data['updated_at'] = datetime.now()
    
    result = collection.update_one({"employee_id": employee_id}, {"$set": update_data})
    
    if result.modified_count == 0:
        logger.warning(f"No changes made to user: {employee_id}")
        return {"msg": "No changes were made", "employee_id": employee_id}
    
    logger.info(f"User updated successfully: {employee_id}")
    return {"msg": "User updated successfully", "employee_id": employee_id, "modified_count": result.modified_count}

def update_user_leave_balance(employee_id: str, leave_name: str, leave_count: int, hostname: str):
    """
    Updates the leave balance for a user.
    """
    collection = get_user_collection(hostname)
    collection.update_one({"employee_id": employee_id}, {"$inc": {f"leave_balance.{leave_name}": leave_count}})
    logger.info(f"Updated leave balance for {employee_id} to {leave_name}: {leave_count}")
    return {"msg": "Leave balance updated successfully"}
