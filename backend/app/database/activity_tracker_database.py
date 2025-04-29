import logging
from datetime import datetime
from database.database_connector import connect_to_database
from models.activity_tracker import ActivityTracker

logger = logging.getLogger(__name__)

def get_activity_tracker_collection(hostname: str):
    db = connect_to_database(hostname)
    return db["activity_tracker"]

def create_activity_tracker(hostname: str, activity_tracker: ActivityTracker):
    collection = get_activity_tracker_collection(hostname)
    collection.insert_one(activity_tracker.model_dump())

def get_activity_tracker(hostname: str, activity_tracker_id: str):
    collection = get_activity_tracker_collection(hostname)
    return collection.find_one({"_id": activity_tracker_id})

def get_activity_tracker_by_emp_id(hostname: str, emp_id: str):
    collection = get_activity_tracker_collection(hostname)
    return collection.find_one({"emp_id": emp_id})

def get_activity_tracker_by_date(hostname: str, date: datetime):  
    collection = get_activity_tracker_collection(hostname)
    return collection.find_one({"date": date})

def get_activity_tracker_by_date_range(hostname: str, start_date: datetime, end_date: datetime):
    collection = get_activity_tracker_collection(hostname)
    return collection.find_one({"date": {"$gte": start_date, "$lte": end_date}})

def get_activity_tracker_by_emp_id_and_date(hostname: str, emp_id: str, date: datetime):
    collection = get_activity_tracker_collection(hostname)
    return collection.find_one({"emp_id": emp_id, "date": date})

def get_activity_tracker_by_emp_id_and_date_range(hostname: str, emp_id: str, start_date: datetime, end_date: datetime):
    collection = get_activity_tracker_collection(hostname)
    return collection.find_one({"emp_id": emp_id, "date": {"$gte": start_date, "$lte": end_date}})

def get_activity_tracker_by_emp_id_and_date_range_and_activity(hostname: str, emp_id: str, start_date: datetime, end_date: datetime, activity: str):
    collection = get_activity_tracker_collection(hostname)
    return collection.find_one({"emp_id": emp_id, "date": {"$gte": start_date, "$lte": end_date}, "activity": activity})

def delete_activity_tracker(hostname: str, activity_tracker_id: str):
    collection = get_activity_tracker_collection(hostname)
    collection.delete_one({"_id": activity_tracker_id})