import logging

from fastapi import HTTPException
from auth.password_handler import hash_password
from models.user_model import UserInfo
from services.company_leave_service import get_all_leaves
from database.user_database import (
    get_all_users as db_get_all_users,
    create_user as db_create_user,
    get_user_by_emp_id as db_get_user_by_emp_id,
    get_users_stats as db_get_users_stats,
    get_users_by_manager_id as db_get_users_by_manager_id
)

logger = logging.getLogger(__name__)

async def create_default_user():
    """
    Creates a default user in the user_collection.
    """
    if await db_get_user_by_emp_id('superadmin', 'global_database'):
        logger.info("Default user already exists.")
        return
    
    user = UserInfo(emp_id="superadmin", 
                    email="clickankit4u@gmail.com", 
                    name="superadmin", 
                    gender="Male", 
                    dob="1990-01-01", 
                    doj="1990-01-01", 
                    mobile="1234567890", 
                    password="admin123", 
                    role="superadmin",
                    department="admin",
                    designation="admin",
                    location="admin",
                    manager_id="admin", 
                    is_active=True) 
    user_result = await create_user(user, 'global_database')
    logger.info("User created successfully, inserted_id: %s", str(user_result.inserted_id))
    return {"msg": "User created successfully", "inserted_id": str(user_result.inserted_id)}


def validate_user_data(user: UserInfo):
    if not user.emp_id or not user.email or not user.name or not user.gender or not user.dob or not user.doj or not user.mobile:
        logger.error("Missing required fields in user data.")
        raise HTTPException(status_code=400, detail="Missing required fields in user data.")

async def create_user(user: UserInfo, hostname: str):
    """
    Creates a new user in the user_collection.
    """
    user.password = hash_password(user.password)
    try:
        leaves = await get_all_leaves()
        print(leaves)
        for leave in leaves:
            user.leave_balance[leave["name"]] = leave["count"]
        print(user.leave_balance)
        msg = await db_create_user(user, hostname)
        logger.info(msg)
        return msg
    except Exception as e:
        logger.exception("Exception occurred during user/login creation.")
        return {"msg": "Internal Server Error", "error": str(e)}

async def get_all_users(hostname: str):
    """
    Returns all users from user_collection.
    """
    users = await db_get_all_users(hostname)
    logger.info("Fetched all users, count: %d", len(users))
    return users

async def get_users_stats(hostname: str):
    stats = await db_get_users_stats(hostname)
    logger.info("User stats: %s", stats)
    return stats

async def get_user_by_emp_id(emp_id: str, hostname: str):
    """
    Returns user info for a user by emp_id.
    """
    user = await db_get_user_by_emp_id(emp_id, hostname)

    return user

async def get_users_by_manager_id(manager_id: str, hostname: str):
    """
    Returns user info for a user by manager_id.
    """
    users = await db_get_users_by_manager_id(manager_id, hostname)
    users = list(users)
    logger.info("Fetched users by manager_id: %s, count: %d", manager_id, len(users))
    return users


