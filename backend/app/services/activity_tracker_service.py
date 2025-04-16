from datetime import datetime
from database import activity_tracker_collection
from models.activity_tracker import ActivityTracker


def track_activity(activity: ActivityTracker):
    activity_tracker_collection.insert_one(activity.model_dump())

def get_activity_by_empId(empId: str):
    return activity_tracker_collection.find({"empId": empId})

def get_activity_by_date(date: datetime):
    return activity_tracker_collection.find({"date": date})

def get_activity_by_date_range(start_date: datetime, end_date: datetime):
    return activity_tracker_collection.find({"date": {"$gte": start_date, "$lte": end_date}})

def get_activity_by_empId_and_date(empId: str, date: datetime):
    return activity_tracker_collection.find({"empId": empId, "date": date})

def get_activity_by_empId_and_date_range(empId: str, start_date: datetime, end_date: datetime):
    return activity_tracker_collection.find({"empId": empId, "date": {"$gte": start_date, "$lte": end_date}})

def get_activity_by_empId_and_date_range_and_activity(empId: str, start_date: datetime, end_date: datetime, activity: str):
    return activity_tracker_collection.find({"empId": empId, "date": {"$gte": start_date, "$lte": end_date}, "activity": activity})

def delete_activity(activityId: str):
    activity_tracker_collection.delete_one({"activityId": activityId})