import logging
from datetime import datetime
from database.user_database import get_emp_ids_by_manager_id
from models.attendance import Attendance
from database.database_connector import connect_to_database
import uuid

logger = logging.getLogger(__name__)

async def get_attendance_collection(hostname: str):
    """
    Returns the attendance collection for the specified company.
    """
    db = connect_to_database(hostname)
    return db["attendance"]

async def create_attendance(emp_id: str, hostname: str, check_in: bool = True):
    """
    Creates a new attendance record.
    """
    collection = await get_attendance_collection(hostname)
    
    now = datetime.now()
    attendance_id = str(uuid.uuid4())
    
    attendance_dict = {
        "attendance_id": attendance_id,
        "emp_id": emp_id,
        "date": now.date(),
        "day": now.day,
        "month": now.month,
        "year": now.year,
        "check_in_time": now if check_in else None,
        "check_out_time": None if check_in else now,
        "created_at": now,
        "is_active": True
    }
    
    result = await collection.insert_one(attendance_dict)
    return attendance_id

async def get_all_attendance(hostname: str):
    """
    Retrieves all active attendance records.
    """
    collection = await get_attendance_collection(hostname)
    attendances = []
    cursor = collection.find({"is_active": True})
    async for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

async def get_employee_attendance_by_month(emp_id: str, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for a specific employee in a given month and year.
    """
    collection = await get_attendance_collection(hostname)
    attendances = []
    cursor = collection.find({
        "emp_id": emp_id,
        "month": month,
        "year": year,
        "is_active": True
    })
    async for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

async def get_employee_attendance_by_year(emp_id: str, year: int, hostname: str):
    """
    Retrieves attendance records for a specific employee in a given year.
    """
    collection = await get_attendance_collection(hostname)
    attendances = []
    cursor = collection.find({
        "emp_id": emp_id,
        "year": year,
        "is_active": True
    })
    async for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

async def get_team_attendance_by_date(manager_id: str, date: int, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for all team members on a specific date.
    """
    collection = await get_attendance_collection(hostname)
    emp_ids = await get_emp_ids_by_manager_id(manager_id, hostname)
    attendances = []
    cursor = collection.find({
        "emp_id": {"$in": emp_ids},
        "day": date,
        "month": month,
        "year": year,
        "is_active": True
    })
    async for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

async def get_team_attendance_by_month(manager_id: str, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for all team members in a given month.
    """
    collection = await get_attendance_collection(hostname)
    emp_ids = await get_emp_ids_by_manager_id(manager_id, hostname)
    attendances = []
    cursor = collection.find({
        "emp_id": {"$in": emp_ids},
        "month": month,
        "year": year,
        "is_active": True
    })
    async for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

async def get_team_attendance_by_year(manager_id: str, year: int, hostname: str):
    """
    Retrieves attendance records for all team members in a given year.
    """
    collection = await get_attendance_collection(hostname)
    emp_ids = await get_emp_ids_by_manager_id(manager_id, hostname)
    attendances = []
    cursor = collection.find({
        "emp_id": {"$in": emp_ids},
        "year": year,
        "is_active": True
    })
    async for doc in cursor:
        attendances.append(Attendance(**doc))
    return attendances

async def get_todays_attendance_stats(hostname: str):
    """
    Retrieves today's attendance statistics.
    """
    collection = await get_attendance_collection(hostname)
    today = datetime.now().date()
    
    total_employees = await collection.count_documents({
        "date": today,
        "is_active": True
    })
    
    checked_in = await collection.count_documents({
        "date": today,
        "check_in_time": {"$ne": None},
        "is_active": True
    })
    
    checked_out = await collection.count_documents({
        "date": today,
        "check_out_time": {"$ne": None},
        "is_active": True
    })
    
    return {
        "total_employees": total_employees,
        "checked_in": checked_in,
        "checked_out": checked_out,
        "pending_check_in": total_employees - checked_in,
        "pending_check_out": checked_in - checked_out
    } 