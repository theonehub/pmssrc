from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List
from services import attendance_service
from auth.auth import extract_hostname, extract_emp_id, role_checker
from models.user_model import User
from pydantic import BaseModel, Field
import logging

routes = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

@routes.post("/checkin")
def checkin(emp_id: str = Depends(extract_emp_id), 
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["user"]))):
    logger.info(f"Checkin request received for employee {emp_id} at {hostname}")
    try:
        return attendance_service.checkin(emp_id, hostname)
    except Exception as e:
        logger.error(f"Error checking in employee {emp_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@routes.post("/checkout")
def checkout(emp_id: str = Depends(extract_emp_id), 
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["user"]))):
    logger.info(f"Checkout request received for employee {emp_id} at {hostname}")
    try:
        return attendance_service.checkout(emp_id, hostname)
    except Exception as e:
        logger.error(f"Error checking out employee {emp_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@routes.get("/user/{emp_id}/{month}/{year}")
def get_attendance(emp_id: str, month: int, year: int, hostname: str = Depends(extract_hostname)):
    attendances = attendance_service.get_employee_attendance_by_month(emp_id, month, year, hostname)
    logger.info(f"Attendances: {attendances}")
    return attendances

@routes.get("/my/month/{month}/{year}")
def get_attendance(month: int, year: int, emp_id: str = Depends(extract_emp_id), hostname: str = Depends(extract_hostname)):
    return attendance_service.get_employee_attendance_by_month(emp_id, month, year, hostname) 

@routes.get("/my/year/{year}")
def get_attendance(year: int, emp_id: str = Depends(extract_emp_id), hostname: str = Depends(extract_hostname)):
    return attendance_service.get_employee_attendance_by_year(emp_id, year, hostname)

@routes.get("/manager/date/{date}/{month}/{year}")
def get_attendance(date: int, month: int, year: int, 
                         emp_id: str = Depends(extract_emp_id), 
                         hostname: str = Depends(extract_hostname),
                         role: str = Depends(role_checker(["manager"]))):
    return attendance_service.get_team_attendance_by_date(emp_id, date, month, year, hostname)

@routes.get("/manager/month/{month}/{year}")
def get_attendance(month: int, year: int, 
                         emp_id: str = Depends(extract_emp_id), 
                         hostname: str = Depends(extract_hostname),
                         role: str = Depends(role_checker(["manager"]))):
    return attendance_service.get_team_attendance_by_month(emp_id, month, year, hostname)    

@routes.get("/manager/year/{year}")
def get_attendance(year: int, emp_id: str = Depends(extract_emp_id), 
                         hostname: str = Depends(extract_hostname),
                         role: str = Depends(role_checker(["manager"]))):
    return attendance_service.get_team_attendance_by_year(emp_id, year, hostname)

@routes.get("/admin/date/{date}/{month}/{year}")
def get_attendance(date: int, month: int, year: int, 
                         hostname: str = Depends(extract_hostname),
                         role: str = Depends(role_checker(["superadmin", "admin"]))):
    return attendance_service.get_attendance_by_date(date, month, year, hostname)

@routes.get("/admin/month/{month}/{year}")
def get_attendance(month: int, year: int, 
                         hostname: str = Depends(extract_hostname),
                         role: str = Depends(role_checker(["superadmin", "admin"]))):
    return attendance_service.get_attendance_by_month(month, year, hostname)    

@routes.get("/admin/year/{year}")
def get_attendance(year: int, 
                         hostname: str = Depends(extract_hostname),
                         role: str = Depends(role_checker(["superadmin", "admin"]))):
    return attendance_service.get_attendance_by_year(year, hostname)

@routes.get("/stats/today")
def get_attendance_stats(hostname: str = Depends(extract_hostname),
                               role: str = Depends(role_checker(["superadmin", "admin"]))):
    return attendance_service.get_todays_attendance_stats(hostname)
