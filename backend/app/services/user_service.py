import logging

from fastapi import HTTPException
from auth.password_handler import hash_password
from models.user_model import UserInfo
from database import user_collection

logger = logging.getLogger(__name__)

def create_default_user():
    """
    Creates a default user in the user_collection.
    """
    if user_collection.find_one({"empId": "superadmin"}):
        logger.info("Default user already exists.")
        return
    user = UserInfo(empId="superadmin", email="clickankit4u@gmail.com", name="superadmin", \
                    gender="Male", dob="1990-01-01", doj="2021-01-01", mobile="1234567890", 
                    password="admin123", role="superadmin", managerId="admin", is_active=True)
    create_user(user)


def validate_user_data(user: UserInfo):
    if not user.empId or not user.email or not user.name or not user.gender or not user.dob or not user.doj or not user.mobile:
        logger.error("Missing required fields in user data.")
        raise HTTPException(status_code=400, detail="Missing required fields in user data.")

def create_user(user: UserInfo):
    """
    Creates a new user in the user_collection.
    """
    user.password = hash_password(user.password)
    try:
        user_result = user_collection.insert_one(user.model_dump())
        logger.info("User created successfully, inserted_id: %s", str(user_result.inserted_id))
        return {"msg": "User created successfully", "inserted_id": str(user_result.inserted_id)}
    except Exception as e:
        logger.exception("Exception occurred during user/login creation.")
        return {"msg": "Internal Server Error", "error": str(e)}

def get_all_users():
    """
    Returns all users from user_collection.
    """
    users = user_collection.find()
    users = list(users)
    logger.info("Fetched all users, count: %d", len(users))
    return users

def get_users_stats():
    total_users = user_collection.count_documents({})
    login_stats = user_collection.aggregate([
        {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ])
    stats = {"total_users": total_users}
    for item in login_stats:
        stats[item["_id"]] = item["count"]
    logger.info("User stats: %s", stats)
    return stats

def get_user_by_empId(empId: str):
    """
    Returns user info for a user by empId.
    """
    user = user_collection.find_one({"empId": empId})
    return user

def get_users_by_managerId(managerId: str):
    """
    Returns user info for a user by managerId.
    """
    users = user_collection.find({"managerId": managerId})
    users = list(users)
    logger.info("Fetched users by managerId: %s, count: %d", managerId, len(users))
    return users

