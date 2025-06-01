from datetime import datetime
from models.activity_tracker import ActivityTracker
import database.activity_tracker_database as ds

def track_activity(activity: ActivityTracker, hostname: str):
    ds.create_activity_tracker(activity, hostname)

def get_activity_by_employee_id(employee_id: str, hostname: str):
    return ds.get_activity_tracker_by_employee_id(employee_id, hostname)

def get_activity_by_date(date: datetime, hostname: str):
    return ds.get_activity_tracker_by_date(date, hostname)

def get_activity_by_date_range(start_date: datetime, end_date: datetime, hostname: str):
    return ds.get_activity_tracker_by_date_range(start_date, end_date, hostname)

def get_activity_by_employee_id_and_date(employee_id: str, date: datetime, hostname: str):
    return ds.get_activity_tracker_by_employee_id_and_date(employee_id, date, hostname)

def get_activity_by_employee_id_and_date_range(employee_id: str, start_date: datetime, end_date: datetime, hostname: str):
    return ds.get_activity_tracker_by_employee_id_and_date_range(employee_id, start_date, end_date, hostname)

def get_activity_by_employee_id_and_date_range_and_activity(employee_id: str, start_date: datetime, end_date: datetime, activity: str, hostname: str):
    return ds.get_activity_tracker_by_employee_id_and_date_range_and_activity(employee_id, start_date, end_date, activity, hostname)

def delete_activity(activityId: str, hostname: str):
    ds.delete_activity_tracker(activityId, hostname)