import logging
from datetime import datetime
from bson import ObjectId
from database import attendance_collection, user_collection
from pymongo import ReturnDocument

logger = logging.getLogger(__name__)

def upsert_lwp_for_user(user_id: str, month: str, lwp_days: int):
    """
    Upserts the LWP value for a given user and month.
    If record exists, update it. Else, insert a new one.
    """
    try:
        result = attendance_collection.update_one(
            {"user_id": ObjectId(user_id), "month": month},
            {
                "$set": {
                    "lwp_days": lwp_days,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        logger.info("Upserted LWP for user_id=%s, month=%s, lwp_days=%d", user_id, month, lwp_days)
        return {"msg": "LWP updated successfully"}
    except Exception as e:
        logger.exception("Failed to upsert LWP for user_id=%s, month=%s", user_id, month)
        return {"msg": "Failed to update LWP", "error": str(e)}


def get_lwp_by_month(month: str):
    """
    Returns all users with their LWP data for the given month.
    If a user doesn't have an entry in attendance_collection, defaults to 0 days.
    """
    try:
        users = list(user_collection.find({}, {"_id": 1, "name": 1, "email": 1}))
        lwp_records = list(attendance_collection.find({"month": month}))
        print(lwp_records)
        print(users)

        # Build a lookup map for quick access
        lwp_map = {str(rec["user_id"]): rec["lwp_days"] for rec in lwp_records}

        result = []
        for user in users:
            user_id = str(user["_id"])
            result.append({
                "user_id": user_id,
                "name": user.get("name", "Unknown"),
                "email": user.get("email", "Unknown"),
                "month": month,
                "lwp_days": lwp_map.get(user_id, 0)
            })

        logger.info("Fetched LWP view for %d users for month=%s", len(result), month)
        return result
    except Exception as e:
        logger.exception("Failed to fetch LWP data for month=%s", month)
        return {"msg": "Failed to fetch data", "error": str(e)}


def get_lwp_for_user(user_id: str):
    """
    Fetches all LWP records for a specific user.
    """
    try:
        records = list(attendance_collection.find({"user_id": ObjectId(user_id)}))
        logger.info("Fetched %d LWP records for user_id=%s", len(records), user_id)

        return [
            {
                "month": record["month"],
                "lwp_days": record["lwp_days"],
                "updated_at": record.get("updated_at")
            }
            for record in records
        ]
    except Exception as e:
        logger.exception("Failed to fetch LWP for user_id=%s", user_id)
        return {"msg": "Failed to fetch user LWP", "error": str(e)}



def upsert_lwp_for_user(user_id: str, month: str, lwp_days: int):
    try:
        now = datetime.utcnow()
        result = attendance_collection.find_one_and_update(
            {"user_id": ObjectId(user_id), "month": month},
            {
                "$set": {
                    "lwp_days": lwp_days,
                    "updated_at": now
                },
                "$setOnInsert": {
                    "created_at": now
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        logger.info("Upserted LWP for user_id=%s, month=%s, lwp_days=%d", user_id, month, lwp_days)
        return {"msg": "LWP updated successfully"}
    except Exception as e:
        logger.exception("Failed to upsert LWP")
        return {"msg": "Failed to update LWP", "error": str(e)}