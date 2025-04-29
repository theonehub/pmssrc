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
    logger.info(f"Creating user: {user.emp_id}")
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
    Returns stats of users from user_collection.
    """
    collection = get_user_collection(hostname)
    stats = collection.aggregate([
        {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ])
    logger.info("User stats: %s", stats)
    for item in stats:
        stats[item["_id"]] = item["count"]
    return stats

def get_user_by_emp_id(emp_id: str, hostname: str):
    """
    Returns user info for a user by emp_id.
    """
    collection = get_user_collection(hostname)
    user = collection.find_one({"emp_id": emp_id})
    return user

def get_users_by_manager_id(manager_id: str, hostname: str):
    """
    Returns user info for a user by manager_id.
    """
    collection = get_user_collection(hostname)
    users = collection.find({"manager_id": manager_id})
    return users

def get_emp_ids_by_manager_id(manager_id: str, hostname: str):
    """
    Returns all employee IDs for a given manager ID.
    """
    collection = get_user_collection(hostname)
    users = collection.find({"manager_id": manager_id}, {"_id": 0, "emp_id": 1})
    return [user["emp_id"] for user in users]

def update_user_leave_balance(emp_id: str, leave_name: str, leave_count: int, hostname: str):
    """
    Updates the leave balance for a user.
    """
    collection = get_user_collection(hostname)
    collection.update_one({"emp_id": emp_id}, {"$inc": {f"leave_balance.{leave_name}": leave_count}})
    logger.info(f"Updated leave balance for {emp_id} to {leave_name}: {leave_count}")
    return {"msg": "Leave balance updated successfully"}
