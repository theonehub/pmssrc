import logging
from fastapi import HTTPException
from models.attendance import Attendance
from database.attendance_database import (
    create_attendance,
    get_all_attendance,
    get_employee_attendance_by_month,
    get_employee_attendance_by_year,
    get_team_attendance_by_date,
    get_team_attendance_by_month,
    get_team_attendance_by_year,
    get_todays_attendance_stats
)

logger = logging.getLogger(__name__)

async def checkin(emp_id: str, hostname: str):
    """
    Creates a check-in record for the user with the given emp_id.
    """
    try:
        attendance_id = await create_attendance(emp_id, hostname, check_in=True)
        logger.info(f"Check-in created for user {emp_id} with ID: {attendance_id}")
        return {"message": "Check-in recorded successfully", "attendance_id": attendance_id}
    except Exception as e:
        logger.error(f"Error creating check-in: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def checkout(user, hostname: str):
    """
    Creates a check-out record for the user.
    """
    try:
        attendance_id = await create_attendance(user.emp_id, hostname, check_in=False)
        logger.info(f"Check-out created for user {user.emp_id} with ID: {attendance_id}")
        return {"message": "Check-out recorded successfully", "attendance_id": attendance_id}
    except Exception as e:
        logger.error(f"Error creating check-out: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_all_attendance(hostname: str):
    """
    Retrieves all attendance records.
    """
    try:
        attendances = await get_all_attendance(hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving attendance records: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_employee_attendance_by_month(emp_id: str, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for a specific employee in a given month and year.
    """
    try:
        attendances = await get_employee_attendance_by_month(emp_id, month, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for employee {emp_id} in {month}/{year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving employee attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_employee_attendance_by_year(emp_id: str, year: int, hostname: str):
    """
    Retrieves attendance records for a specific employee in a given year.
    """
    try:
        attendances = await get_employee_attendance_by_year(emp_id, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for employee {emp_id} in {year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving employee attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_team_attendance_by_date(manager_id: str, date: int, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for all team members on a specific date.
    """
    try:
        attendances = await get_team_attendance_by_date(manager_id, date, month, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for date {date}/{month}/{year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving team attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_team_attendance_by_month(manager_id: str, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for all team members in a given month.
    """
    try:
        attendances = await get_team_attendance_by_month(manager_id, month, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for month {month}/{year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving team attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_team_attendance_by_year(manager_id: str, year: int, hostname: str):
    """
    Retrieves attendance records for all team members in a given year.
    """
    try:
        attendances = await get_team_attendance_by_year(manager_id, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for year {year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving team attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_todays_attendance_stats(hostname: str):
    """
    Retrieves today's attendance statistics.
    """
    try:
        stats = await get_todays_attendance_stats(hostname)
        logger.info(f"Retrieved today's attendance statistics: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error retrieving attendance statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))