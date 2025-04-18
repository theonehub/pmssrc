from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List
from models.attendance import Attendance
from services import attendance_service
from auth.auth import get_current_user
from models.user_model import User
from pydantic import BaseModel, Field
import logging

routes = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

@routes.post("/dummy/checkin")
async def dummy_checkin():
    return await attendance_service.dummy_checkin()

@routes.post("/checkin")
async def checkin(user: User = Depends(get_current_user)):
    return await attendance_service.checkin(user)

@routes.post("/checkout")
async def checkout(user: User = Depends(get_current_user)):
    return await attendance_service.checkout(user)

@routes.post("/all")
async def get_attendance(user: User = Depends(get_current_user)):
    if user.role == "superadmin":
        return await attendance_service.get_all_attendance()
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

@routes.get("/user/{empId}/{month}/{year}")
async def get_attendance(empId: str, month: int, year: int, user: User = Depends(get_current_user)):
    return await attendance_service.get_employee_attendance_by_month(empId, month, year)

@routes.get("/my/month/{month}/{year}")
async def get_attendance(month: int, year: int, user: User = Depends(get_current_user)):
    return await attendance_service.get_employee_attendance_by_month(user.empId, month, year) 

@routes.get("/my/year/{year}")
async def get_attendance(year: int, user: User = Depends(get_current_user)):
    return await attendance_service.get_employee_attendance_by_year(user.empId, year)


@routes.get("/manager/date/{date}/{month}/{year}")
async def get_attendance(date: int, month: int, year: int, user: User = Depends(get_current_user)):
    return await attendance_service.get_team_attendance_by_date(date, month, year)

@routes.get("/manager/month/{month}/{year}")
async def get_attendance(month: int, year: int, user: User = Depends(get_current_user)):
    return await attendance_service.get_team_attendance_by_month(month, year)    

@routes.get("/manager/year/{year}")
async def get_attendance(year: int, user: User = Depends(get_current_user)):
    return await attendance_service.get_team_attendance_by_year(year)

@routes.get("/admin/date/{date}/{month}/{year}")
async def get_attendance(date: int, month: int, year: int, user: User = Depends(get_current_user)):
    return await attendance_service.get_attendance_by_date(date, month, year)

@routes.get("/admin/month/{month}/{year}")
async def get_attendance(month: int, year: int, user: User = Depends(get_current_user)):
    return await attendance_service.get_attendance_by_month(month, year)    

@routes.get("/admin/year/{year}")
async def get_attendance(year: int, user: User = Depends(get_current_user)):
    return await attendance_service.get_attendance_by_year(year)
