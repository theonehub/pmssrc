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
        "emp_id": attendance["emp_id"],
        "checkin_time": attendance["checkin_time"],
        "checkout_time": attendance["checkout_time"],
        "marked_by": attendance["marked_by"]
    }

async def dummy_checkin():
    for i in range(1, 50):
        attendance = Attendance(
            emp_id=f"emp{2000+i}",
            checkin_time=datetime.now()+timedelta(days=6),
            checkout_time=datetime.now()+timedelta(days=6),
            marked_by=f"emp{2000+i}"
        )
        try:
            attendance_collection.insert_one(attendance.model_dump())
        except Exception as e:
            logger.error(f"Error creating attendance for employee {attendance.emp_id}: {e}")
            raise e

async def checkin(employee: User):
    attendance = Attendance(
        emp_id=employee.emp_id,
        checkin_time=datetime.now(),
        marked_by=employee.emp_id
    )
    logger.info(f"Checkin for employee {employee.emp_id} with id {attendance.model_dump()}")
    try:
        attendance_collection.insert_one(attendance.model_dump())
    except Exception as e:
        logger.error(f"Error creating attendance for employee {employee.emp_id}: {e}")
        raise e

async def checkout(employee: User):
    attendance_collection.update_one({"emp_id": employee.emp_id, "date": datetime.today().day, "month": datetime.today().month, "year": datetime.today().year}, \
                                            {"$set": {"checkout_time": datetime.now()}})
    logger.info(f"Checkout for employee {employee.emp_id}")

async def get_all_attendance():
    attendances = attendance_collection.find()
    return [serialize_attendance(attendance) for attendance in attendances]


async def get_employee_attendance_by_date(emp_id: str, date: int, month: int, year: int):
    attendance = attendance_collection.find_one({"emp_id": emp_id, "date": date, "month": month, "year": year})
    return serialize_attendance(attendance)

async def get_employee_attendance_by_month(emp_id: str, month: int, year: int):
    attendances = attendance_collection.find({'emp_id': emp_id, "month": month, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list]

async def get_employee_attendance_by_year(emp_id: str, year: int):
    attendances = attendance_collection.find({"emp_id": emp_id, "year": year})
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
    team_members = user_collection.find({"manager_id": user.emp_id})
    team_member_ids = [member["emp_id"] for member in team_members]
    attendances = attendance_collection.find({"emp_id": {"$in": team_member_ids}, "date": date, "month": month, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list]

async def get_team_attendance_by_month(user: User, month: int, year: int):
    team_members = user_collection.find({"manager_id": user.emp_id})
    team_member_ids = [member["emp_id"] for member in team_members]
    attendances = attendance_collection.find({"emp_id": {"$in": team_member_ids}, "month": month, "year": year})
    attendance_list = list(attendances)
    return [serialize_attendance(attendance) for attendance in attendance_list] 

async def get_team_attendance_by_year(user: User, year: int):
    team_members = user_collection.find({"manager_id": user.emp_id})
    team_member_ids = [member["emp_id"] for member in team_members]
    attendances = attendance_collection.find({"emp_id": {"$in": team_member_ids}, "year": year})
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