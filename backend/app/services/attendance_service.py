import logging
from fastapi import HTTPException
from models.attendance import Attendance
from database.attendance_database import (
    create_attendance as create_attendance_db,
    get_employee_attendance_by_month as get_employee_attendance_by_month_db,
    get_employee_attendance_by_year as get_employee_attendance_by_year_db,
    get_team_attendance_by_date as get_team_attendance_by_date_db,
    get_team_attendance_by_month as get_team_attendance_by_month_db,
    get_team_attendance_by_year as get_team_attendance_by_year_db,
    get_todays_attendance_stats as get_todays_attendance_stats_db
)

logger = logging.getLogger(__name__)

def checkin(emp_id: str, hostname: str):
    """
    Creates a check-in record for the user with the given emp_id.
    """
    try:
        attendance_id = create_attendance_db(emp_id, hostname, check_in=True)
        logger.info(f"Check-in created for user {emp_id} with ID: {attendance_id}")
        return {"message": "Check-in recorded successfully", "attendance_id": attendance_id}
    except Exception as e:
        logger.error(f"Error creating check-in: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def checkout(emp_id: str, hostname: str):
    """
    Creates a check-out record for the user.
    """
    try:
        attendance_id = create_attendance_db(emp_id, hostname, check_in=False)
        logger.info(f"Check-out created for user {emp_id} with ID: {attendance_id}")
        return {"message": "Check-out recorded successfully", "attendance_id": attendance_id}
    except Exception as e:
        logger.error(f"Error creating check-out: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

def get_employee_attendance_by_month(emp_id: str, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for a specific employee in a given month and year.
    """
    try:
        logger.info(f"Attendance for {emp_id} month {month} year {year} hostname {hostname}")
        attendances = get_employee_attendance_by_month_db(emp_id, month, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for employee {emp_id} in {month}/{year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving employee attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_employee_attendance_by_year(emp_id: str, year: int, hostname: str):
    """
    Retrieves attendance records for a specific employee in a given year.
    """
    try:
        attendances = get_employee_attendance_by_year_db(emp_id, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for employee {emp_id} in {year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving employee attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_team_attendance_by_date(manager_id: str, date: int, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for all team members on a specific date.
    """
    try:
        attendances = get_team_attendance_by_date_db(manager_id, date, month, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for date {date}/{month}/{year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving team attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_team_attendance_by_month(manager_id: str, month: int, year: int, hostname: str):
    """
    Retrieves attendance records for all team members in a given month.
    """
    try:
        attendances = get_team_attendance_by_month_db(manager_id, month, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for month {month}/{year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving team attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_team_attendance_by_year(manager_id: str, year: int, hostname: str):
    """
    Retrieves attendance records for all team members in a given year.
    """
    try:
        attendances = get_team_attendance_by_year_db(manager_id, year, hostname)
        logger.info(f"Retrieved {len(attendances)} attendance records for year {year}")
        return attendances
    except Exception as e:
        logger.error(f"Error retrieving team attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_todays_attendance_stats(hostname: str):
    """
    Retrieves today's attendance statistics.
    """
    try:
        stats = get_todays_attendance_stats_db(hostname)
        logger.info(f"Retrieved today's attendance statistics: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error retrieving attendance statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))