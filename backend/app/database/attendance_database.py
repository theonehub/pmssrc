import logging
from datetime import datetime, timedelta
from database.user_database import get_emp_ids_by_manager_id
from models.attendance import Attendance
from database.database_connector import connect_to_database
import uuid

logger = logging.getLogger(__name__)

def get_attendance_collection(hostname: str):
    """
    Returns the attendance collection for the specified company.
    """
    db = connect_to_database(hostname)
    return db["attendance"]

def create_attendance(emp_id: str, hostname: str, check_in: bool = True):
    """
    Creates a new attendance record.
    """
    collection = get_attendance_collection(hostname)
    
    now = datetime.now()
    attendance_id = str(uuid.uuid4())
    
    attendance_dict = {
        "attendance_id": attendance_id,
        "emp_id": emp_id,
        "date": now,
        "checkin_time": now if check_in else None,
        "checkout_time": None if check_in else now
    }
    
    result = collection.insert_one(attendance_dict)
    return attendance_id

def get_employee_attendance_by_month(emp_id: str, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for a specific employee in a given month and year.
    """
    collection = get_attendance_collection(hostname)
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    attendances = []
    cursor = collection.find({
        "emp_id": emp_id,
        "date": {"$gte": start_date, "$lt": end_date}
    })
    for doc in cursor:
        print("doc", doc)
        attendances.append(Attendance(**doc))

    for attendance in attendances:
        logger.info(f"Attendance: {attendance}")
        
    return attendances

def get_employee_attendance_by_year(emp_id: str, year: int, hostname: str):
    """
    Retrieves attendance records for a specific employee in a given year.
    """
    collection = get_attendance_collection(hostname)
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    attendances = []
    cursor = collection.find({
        "emp_id": emp_id,
        "date": {"$gte": start_date, "$lt": end_date}
    })
    for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

def get_team_attendance_by_date(manager_id: str, date: int, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for all team members on a specific date.
    """
    collection = get_attendance_collection(hostname)
    emp_ids = get_emp_ids_by_manager_id(manager_id, hostname)
    target_date = datetime(year, month, date)
    next_date = target_date + timedelta(days=1)
    
    attendances = []
    cursor = collection.find({
        "emp_id": {"$in": emp_ids},
        "date": {"$gte": target_date, "$lt": next_date}
    })
    for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

def get_team_attendance_by_month(manager_id: str, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for all team members in a given month.
    """
    collection = get_attendance_collection(hostname)
    emp_ids = get_emp_ids_by_manager_id(manager_id, hostname)
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    attendances = []
    cursor = collection.find({
        "emp_id": {"$in": emp_ids},
        "date": {"$gte": start_date, "$lt": end_date}
    })
    for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

def get_team_attendance_by_year(manager_id: str, year: int, hostname: str):
    """
    Retrieves attendance records for all team members in a given year.
    """
    collection = get_attendance_collection(hostname)
    emp_ids = get_emp_ids_by_manager_id(manager_id, hostname)
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    attendances = []
    cursor = collection.find({
        "emp_id": {"$in": emp_ids},
        "date": {"$gte": start_date, "$lt": end_date}
    })
    for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

def get_todays_attendance_stats(hostname: str):
    """
    Retrieves today's attendance statistics.
    """
    collection = get_attendance_collection(hostname)
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    tomorrow_start = today_start + timedelta(days=1)

    total_employees = collection.count_documents({
        "date": {"$gte": today_start, "$lt": tomorrow_start}
    })
    
    checked_in = collection.count_documents({
        "date": {"$gte": today_start, "$lt": tomorrow_start},
        "checkin_time": {"$ne": None}
    })
    
    checked_out = collection.count_documents({
        "date": {"$gte": today_start, "$lt": tomorrow_start},
        "checkout_time": {"$ne": None},
        "is_active": True
    })
    
    return {
        "total_employees": total_employees,
        "checked_in": checked_in,
        "checked_out": checked_out,
        "pending_check_in": total_employees - checked_in,
        "pending_check_out": checked_in - checked_out
    } 