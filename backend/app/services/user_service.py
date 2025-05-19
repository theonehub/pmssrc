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
    get_users_by_manager_id as db_get_users_by_manager_id,
    update_user_leave_balance as db_update_user_leave_balance
)

logger = logging.getLogger(__name__)

def create_default_user():
    """
    Creates a default user in the user_collection.
    """
    if db_get_user_by_emp_id('superadmin', 'global_database'):
        logger.info("Default user already exists.")
        return
    
    user = UserInfo(emp_id="superadmin", 
                    email="clickankit4u@gmail.com", 
                    name="superadmin", 
                    gender="Male", 
                    dob="1990-01-01", 
                    doj="1990-01-01", 
                    dol='',
                    mobile="1234567890", 
                    password=hash_password("admin123"), 
                    role="superadmin",
                    department="admin",
                    designation="admin",
                    location="admin",
                    manager_id="admin", 
                    is_active=True) 
    msg = db_create_user(user, 'global_database')
    logger.info("User created successfully, inserted_id: %s", msg)
    return msg


def validate_user_data(user: UserInfo):
    if not user.emp_id or not user.email or not user.name or not user.gender or not user.dob or not user.doj or not user.mobile:
        logger.error("Missing required fields in user data.")
        raise HTTPException(status_code=400, detail="Missing required fields in user data.")

def create_user(user: UserInfo, hostname: str):
    """
    Creates a new user in the user_collection.
    """
    user.password = hash_password(user.password)
    try:
        leaves = get_all_leaves(hostname)
        print(leaves)
        for leave in leaves:
            user.leave_balance[leave["name"]] = leave["count"]
        print(user.leave_balance)
        msg = db_create_user(user, hostname)
        logger.info(msg)
        return msg
    except Exception as e:
        logger.exception("Exception occurred during user/login creation.")
        return {"msg": "Internal Server Error", "error": str(e)}

def get_all_users(hostname: str):
    """
    Returns all users from user_collection.
    """
    users = db_get_all_users(hostname)
    logger.info("Fetched all users, count: %d", len(users))
    return users

def get_users_stats(hostname: str):
    stats = db_get_users_stats(hostname)
    logger.info("User stats: %s", stats)
    return stats

def get_user_by_emp_id(emp_id: str, hostname: str):
    """
    Returns user info for a user by emp_id.
    """
    user = db_get_user_by_emp_id(emp_id, hostname)

    return user

def get_users_by_manager_id(manager_id: str, hostname: str):
    """
    Returns user info for a user by manager_id.
    """
    users = db_get_users_by_manager_id(manager_id, hostname)
    users = list(users)
    logger.info("Fetched users by manager_id: %s, count: %d", manager_id, len(users))
    return users

def update_user_leave_balance(emp_id: str, leave_name: str, leave_count: int, hostname: str):
    """
    Updates the leave balance for a user.
    """
    db_update_user_leave_balance(emp_id, leave_name, leave_count, hostname)




