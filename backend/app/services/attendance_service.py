import logging
from datetime import datetime, timedelta
from bson import ObjectId
from models.user_model import User
from models.attendance import Attendance
from database import attendance_collection,user_collection
from datetime import date

logger = logging.getLogger(__name__)

def serialize_attendance(attendance: Attendance):
    print(attendance)
    return {
        "empId": attendance["empId"],
        "checkin_time": attendance["checkin_time"],
        "checkout_time": attendance["checkout_time"],
        "marked_by": attendance["marked_by"]
    }

async def dummy_checkin():
    for i in range(1, 50):
        attendance = Attendance(
            empId=f"emp{2000+i}",
            checkin_time=datetime.now()+timedelta(days=6),
            checkout_time=datetime.now()+timedelta(days=6),
            marked_by=f"emp{2000+i}"
        )
        try:
            attendance_collection.insert_one(attendance.model_dump())
        except Exception as e:
            logger.error(f"Error creating attendance for employee {attendance.empId}: {e}")
            raise e

async def checkin(employee: User):
    attendance = Attendance(
        empId=employee.empId,
        checkin_time=datetime.now(),
        marked_by=employee.empId
    )
    logger.info(f"Checkin for employee {employee.empId} with id {attendance.model_dump()}")
    try:
        attendance_collection.insert_one(attendance.model_dump())
    except Exception as e:
        logger.error(f"Error creating attendance for employee {employee.empId}: {e}")
        raise e

async def checkout(employee: User):
    attendance_collection.update_one({"empId": employee.empId, "date": datetime.today().day, "month": datetime.today().month, "year": datetime.today().year}, \
                                            {"$set": {"checkout_time": datetime.now()}})
    logger.info(f"Checkout for employee {employee.empId}")

async def get_all_attendance():
    attendances = attendance_collection.find()
    return [serialize_attendance(attendance) for attendance in attendances]


async def get_employee_attendance_by_date(empId: str, date: int, month: int, year: int):
    attendance = attendance_collection.find_one({"empId": empId, "date": date, "month": month, "year": year})
    return serialize_attendance(attendance)

async def get_employee_attendance_by_month(empId: str, month: int, year: int):
    attendances = attendance_collection.find({'empId': empId, "month": month, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list]

async def get_employee_attendance_by_year(empId: str, year: int):
    attendances = attendance_collection.find({"empId": empId, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list]

async def get_attendance_by_month(month: int, year: int):
    attendances = attendance_collection.find({"month": month, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list] 

async def get_attendance_by_year(year: int):
    attendances = attendance_collection.find({"year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list]

async def get_attendance_by_date(date: int, month: int, year: int):
    attendances = attendance_collection.find({"date": date, "month": month, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list]


async def get_team_attendance_by_date(user: User, date: int, month: int, year: int):
    team_members = user_collection.find({"manager_id": user.empId})
    team_member_ids = [member["empId"] for member in team_members]
    attendances = attendance_collection.find({"empId": {"$in": team_member_ids}, "date": date, "month": month, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list]

async def get_team_attendance_by_month(user: User, month: int, year: int):
    team_members = user_collection.find({"manager_id": user.empId})
    team_member_ids = [member["empId"] for member in team_members]
    attendances = attendance_collection.find({"empId": {"$in": team_member_ids}, "month": month, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list] 

async def get_team_attendance_by_year(user: User, year: int):
    team_members = user_collection.find({"manager_id": user.empId})
    team_member_ids = [member["empId"] for member in team_members]
    attendances = attendance_collection.find({"empId": {"$in": team_member_ids}, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list]     

async def get_todays_attendance_stats():
    today = datetime.now().date()
    attendances = attendance_collection.find({"date": today.day, "month": today.month, "year": today.year})
    attendance_list = list(attendances)
    return {
        "checkin_count": sum(1 for attendance in attendance_list if attendance["checkin_time"] is not None),
        "checkout_count": sum(1 for attendance in attendance_list if attendance["checkout_time"] is not None)
    }