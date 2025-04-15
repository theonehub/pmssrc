import logging
from database import login_collection, user_collection

logger = logging.getLogger(__name__)

def get_login_info_by_username(username: str):
    """
    Retrieves login information for a given username.
    """
    user = login_collection.find_one({"username": username})
    logger.debug("Fetched login info for username '%s': %s", username, user)
    return user

def create_login_info(username: str, hashed_password: str, role: str):
    """
    Inserts login information into the login_collection.
    """
    login_doc = {"username": username, "password": hashed_password, "role": role}
    result = login_collection.insert_one(login_doc)
    logger.info("Created login info for username '%s', inserted_id: %s", username, result.inserted_id)
    return result

def get_all_login_info():
    """
    Retrieves all login information (username and role) from the collection.
    """
    users = list(login_collection.find({}, {"_id": 0, "username": 1, "role": 1}))
    logger.info("Fetched all login info, count: %d", len(users))
    return users

from bson import ObjectId

def create_user(user_doc: dict, login_doc: dict):
    
    """
    Creates a new user and corresponding login entry with bi-directional references.
    Ensures consistency: if any step fails, rollback is performed to delete inserted documents.
    """
    try:
        if login_doc:
            # Check if username already exists
            if login_collection.find_one({"username": login_doc['username']}):
                logger.warning("Login already exists for username: %s", login_doc['username'])
                return {"msg": "Login already exists."}

            # Step 1: Insert user document first
            user_data_to_insert = {key: value for key, value in user_doc.items() if key in ['name', 'gender', 'dob', 'doj', 'mobile','email','empId']}

            
            user_result = user_collection.insert_one(user_doc)
            
            if not user_result.inserted_id:
                logger.error("User creation failed before login creation.")
                return {"msg": "User creation failed before login creation"}

            user_id = user_result.inserted_id
            logger.info("Inserted user with ID: %s", user_id)

            # Step 2: Insert login document with user_id reference
            login_doc['user_id'] = user_id
            login_result = login_collection.insert_one(login_doc)
            if not login_result.inserted_id:
                logger.error("Login creation failed after user creation. Rolling back user.")
                user_collection.delete_one({"_id": user_id})
                return {"msg": "Login creation failed. User rolled back."}

            login_id = login_result.inserted_id
            logger.info("Inserted login with ID: %s", login_id)

            # Step 3: Update user document with login_id
            update_result = user_collection.update_one(
                {"_id": user_id},
                {"$set": {"login_id": login_id}}
            )
            if update_result.modified_count == 0:
                logger.error("Failed to update user with login_id. Rolling back both.")
                login_collection.delete_one({"_id": login_id})
                user_collection.delete_one({"_id": user_id})
                return {"msg": "User update failed. Rolled back user and login."}

            logger.info("Linked user and login successfully.")
            return {"msg": "User and Login created successfully"}

        # Case: No login, just insert user
        user_data_to_insert = {key: value for key, value in user_doc.items() if key in ['name', 'gender', 'dob', 'doj', 'mobile','email','empId']}
        
        result = user_collection.insert_one(user_data_to_insert)
        if result.inserted_id:
            logger.info("User created successfully. User_id: %s", result.inserted_id)
            return {"msg": "User created successfully"}
        else:
            logger.error("User creation failed.")
            return {"msg": "User creation failed"}

    except Exception as e:
        logger.exception("Exception occurred during user/login creation.")
        return {"msg": "Internal Server Error", "error": str(e)}


def get_all_users():
    """
    Returns merged user and login info by joining user_collection and login_collection.
    Includes users without login data.
    """
    users = []

    # Get all login documents as a dictionary keyed by user_id
    login_docs = {
        login.get("user_id"): {
            "username": login.get("username"),
            "role": login.get("role")
        }
        for login in login_collection.find({}, {"_id": 0, "username": 1, "role": 1, "user_id": 1})
    }

    # Iterate over all users and try to attach login info if it exists
    for user in user_collection.find():
        user_dict = dict(user)
        user_id = user_dict.get("_id")

        login_info = login_docs.get(user_id)
        if login_info:
            user_dict["username"] = login_info["username"]
            user_dict["role"] = login_info["role"]
            user_dict["email"] = user_dict.get("email")
            user_dict["empId"] = user_dict.get("empId")
        else:
            user_dict["username"] = None
            user_dict["role"] = None

        users.append(user_dict)

    logger.info("Fetched all users (with/without login), count: %d", len(users))
    return users

def get_users_stats():
    total_users = user_collection.count_documents({})
    login_stats = login_collection.aggregate([
        {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ])
    stats = {"total_users": total_users}
    for item in login_stats:
        stats[item["_id"]] = item["count"]
    return stats
