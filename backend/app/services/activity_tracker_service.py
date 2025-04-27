from datetime import datetime
from models.activity_tracker import ActivityTracker
import database.activity_tracker_database as ds

def track_activity(activity: ActivityTracker):
    ds.create_activity_tracker(activity)

def get_activity_by_emp_id(emp_id: str):
    return ds.get_activity_tracker_by_emp_id(emp_id)

def get_activity_by_date(date: datetime):
    return ds.get_activity_tracker_by_date(date)

def get_activity_by_date_range(start_date: datetime, end_date: datetime):
    return ds.get_activity_tracker_by_date_range(start_date, end_date)

def get_activity_by_emp_id_and_date(emp_id: str, date: datetime):
    return ds.get_activity_tracker_by_emp_id_and_date(emp_id, date)

def get_activity_by_emp_id_and_date_range(emp_id: str, start_date: datetime, end_date: datetime):
    return ds.get_activity_tracker_by_emp_id_and_date_range(emp_id, start_date, end_date)

def get_activity_by_emp_id_and_date_range_and_activity(emp_id: str, start_date: datetime, end_date: datetime, activity: str):
    return ds.get_activity_tracker_by_emp_id_and_date_range_and_activity(emp_id, start_date, end_date, activity)

def delete_activity(activityId: str):
    ds.delete_activity_tracker(activityId)