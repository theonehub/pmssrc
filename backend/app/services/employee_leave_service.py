import logging
from datetime import datetime, timedelta
from fastapi import HTTPException
from models.leave_model import EmployeeLeave, LeaveStatus
#from database.database_connector import employee_leave_collection, user_collection, public_holidays_collection, attendance_collection
from uuid import uuid4
from services.public_holiday_service import is_public_holiday
from services.attendance_service import get_employee_attendance_by_month
from services.user_service import get_user_by_emp_id, update_user_leave_balance, get_users_by_manager_id
from database.employee_leave_database import(
     create_employee_leave as create_employee_leave_db,
     get_employee_leave_by_id as get_employee_leave_by_id_db,
     get_employee_leaves_by_emp_id as get_employee_leaves_by_emp_id_db,
     update_employee_leave as update_employee_leave_db,
     delete_employee_leave as delete_employee_leave_db,
     get_all_employee_leaves as get_all_employee_leaves_db,
     get_employee_leaves_by_manager_id as get_employee_leaves_by_manager_id_db,
     get_employee_leaves_by_month_for_emp_id as get_employee_leaves_by_month_for_emp_id_db
     )

logger = logging.getLogger(__name__)

def is_weekend(date):
    """Check if a date is a weekend (Saturday or Sunday)"""
    return date.weekday() >= 5  # 5 is Saturday, 6 is Sunday


def get_working_days(start_date, end_date, hostname: str):
    """
    Calculate the number of working days between two dates,
    excluding weekends and public holidays.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Initialize counter for working days
    working_days = 0
    
    # Iterate through each day in the range
    current_date = start
    while current_date <= end:
        # Check if the current day is not a weekend and not a public holiday
        if not is_weekend(current_date) and not is_public_holiday(current_date, hostname):
            working_days += 1
        
        # Move to the next day
        current_date += timedelta(days=1)
    
    return working_days

def apply_leave(leave: EmployeeLeave, hostname: str):
    """
    Creates a new leave application in the employee_leave_collection.
    """
    try:
        if not leave.leave_id:
            leave.leave_id = str(uuid4())
        # Validate if user exists
        user = get_user_by_emp_id(leave.emp_id, hostname)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate if leave type exists in user's leave balance
        if leave.leave_name not in user.get("leave_balance", {}):
            raise HTTPException(status_code=400, detail="Invalid leave type")
        
        # Calculate number of working days (excluding weekends and public holidays)
        working_days = get_working_days(leave.start_date, leave.end_date)
        leave.leave_count = working_days
        
        # Validate if user has enough leave balance
        if user.get("leave_balance", {}).get(leave.leave_name, 0) < working_days:
            raise HTTPException(status_code=400, detail="Insufficient leave balance")
        
        # Create leave application
        leave_result = create_employee_leave_db(leave, hostname)  
        logger.info(f"Leave application created successfully for user {leave.emp_id}")
        return {"msg": "Leave application submitted successfully", "inserted_id": str(leave_result.inserted_id)}
    except Exception as e:
        logger.exception("Exception occurred during leave application")
        raise HTTPException(status_code=500, detail=str(e))

def leave_balance(emp_id: str, hostname: str):
    """
    Returns the leave balance for a user.
    """
    try:
        user = get_user_by_emp_id(emp_id, hostname)
        leave_balance = {}

        print(user.get("leave_balance", {}))
        for leave_type, balance in user.get("leave_balance", {}).items():
            print(leave_type, balance)
            leave_balance[leave_type] = balance
        
        return leave_balance
        
    except Exception as e:
        logger.exception(f"Error fetching leave balance for user {emp_id}")
        raise HTTPException(status_code=500, detail=str(e))


def get_user_leaves(emp_id: str, hostname: str):
    """
    Returns all leave applications for a user.
    """
    try:
        leaves = get_employee_leaves_by_emp_id_db(emp_id, hostname)
        for leave in leaves:
            del leave["_id"]
        return leaves
    except Exception as e:
        logger.exception(f"Error fetching leaves for user {emp_id}")
        raise HTTPException(status_code=500, detail=str(e))

def get_pending_leaves(manager_id: str, hostname: str):
    """
    Returns all pending leave applications for users under a manager.
    """
    try:
        # Get pending leaves for these users
        leaves = get_employee_leaves_by_manager_id_db(manager_id, hostname)
        for leave in leaves:
            del leave["_id"]
        return leaves
    except Exception as e:
        logger.exception(f"Error fetching pending leaves for manager {manager_id}")
        raise HTTPException(status_code=500, detail=str(e))

def update_leave_status(leave_id: str, status: LeaveStatus, approved_by: str, hostname: str):
    """
    Updates the status of a leave application.
    """
    try:
        update_data = {
            "status": status,
            "approved_by": approved_by,
            "approved_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        result = update_employee_leave_db(leave_id, update_data, hostname)

        # Only deduct leaves from balance if approved
        if status == LeaveStatus.APPROVED:
            leave = get_employee_leave_by_id_db(leave_id, hostname)
            if leave:
                # Recalculate working days to ensure accuracy
                working_days = get_working_days(leave["start_date"], leave["end_date"])
                
                # Update user's leave balance
                user = get_user_by_emp_id(leave["emp_id"], hostname)
                if user and "leave_balance" in user and leave["leave_name"] in user["leave_balance"]:
                    user["leave_balance"][leave["leave_name"]] -= working_days
                    update_user_leave_balance(leave["emp_id"], leave["leave_name"], working_days, hostname)
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Leave application not found")
            
        return {"msg": "Leave status updated successfully"}
    except Exception as e:
        logger.exception(f"Error updating leave status for leave {leave_id}")
        raise HTTPException(status_code=500, detail=str(e))

def update_leave_request(leave_id: str, leave_data: dict, hostname: str):
    """
    Updates an existing leave request.
    """
    try:
        # Get the existing leave request
        existing_leave = get_employee_leave_by_id_db(leave_id, hostname)
        if not existing_leave:
            raise HTTPException(status_code=404, detail="Leave request not found")
            
        # Check if leave has already started
        start_date = datetime.strptime(existing_leave["start_date"], "%Y-%m-%d")
        if start_date < datetime.now():
            raise HTTPException(status_code=400, detail="Cannot modify leave request that has already started")
            
        # Calculate new number of working days (excluding weekends and public holidays)
        new_working_days = get_working_days(leave_data["start_date"], leave_data["end_date"])
        
        # Validate if user has enough leave balance
        user = get_user_by_emp_id(existing_leave["emp_id"], hostname)
        if user["leave_balance"][leave_data["leave_name"]] < new_working_days:
            raise HTTPException(status_code=400, detail="Insufficient leave balance")
            
        # Update leave request
        update_data = {
            "leave_name": leave_data["leave_name"],
            "start_date": leave_data["start_date"],
            "end_date": leave_data["end_date"],
            "reason": leave_data["reason"],
            "leave_count": new_working_days,
            "status": LeaveStatus.PENDING,  # Reset status to pending
            "approved_by": None,
            "approved_date": None
        }
        
        result = update_employee_leave_db(leave_id, update_data, hostname)
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Leave request not found")
            
        return {"msg": "Leave request updated successfully"}
    except Exception as e:
        logger.exception(f"Error updating leave request {leave_id}")
        raise HTTPException(status_code=500, detail=str(e))

def delete_leave_request(leave_id: str, hostname: str):
    """
    Deletes a leave request.
    """
    try:
        # Get the existing leave request
        existing_leave = get_employee_leave_by_id_db(leave_id, hostname)
        if not existing_leave:
            raise HTTPException(status_code=404, detail="Leave request not found")
            
        # Check if leave has already started
        start_date = datetime.strptime(existing_leave["start_date"], "%Y-%m-%d")
        if start_date < datetime.now():
            raise HTTPException(status_code=400, detail="Cannot delete leave request that has already started")
            
        # Delete leave request
        result = delete_employee_leave_db(leave_id, hostname)
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Leave request not found")
            
        return {"msg": "Leave request deleted successfully"}
    except Exception as e:
        logger.exception(f"Error deleting leave request {leave_id}")
        raise HTTPException(status_code=500, detail=str(e))

def get_all_employee_leaves(hostname: str, manager_id: str = None):
    """
    Returns all leave applications for all employees or employees under a specific manager.
    """
    try:
        query = {}
        if manager_id:
            # Get all users under the manager
            users = get_users_by_manager_id(manager_id, hostname)
            emp_ids = [user["emp_id"] for user in users]
            query["emp_id"] = {"$in": emp_ids}
            
        leaves = get_all_employee_leaves_db(hostname)
        for leave in leaves:
            leave["id"] = str(leave["_id"])
            del leave["_id"]
            # Add employee details
            user = get_user_by_emp_id(leave["emp_id"], hostname)
            if user:
                leave["employee_name"] = user.get("name", "")
                leave["employee_email"] = user.get("email", "")
        return leaves
    except Exception as e:
        logger.exception(f"Error fetching all leaves for manager {manager_id}")
        raise HTTPException(status_code=500, detail=str(e)) 
    
def get_leaves_by_month_for_user(emp_id: str, month: int, year: int, hostname: str):
    """
    Returns all leaves for a specific employee in a specific month and year.
    This also includes leaves that span across months.
    """
    try:
        month_start = datetime(year, month, 1)
        
        # Calculate month end (first day of next month minus 1 day)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)

        leaves = get_employee_leaves_by_month_for_emp_id_db(emp_id, year, month, month_start, month_end, hostname)
        
        for leave in leaves:
            del leave["_id"]
            
            # Calculate working days in the specified month for this leave
            start_date = datetime.strptime(leave["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(leave["end_date"], "%Y-%m-%d")
            
            # Adjust start and end date to be within the month if needed
            start_in_month = max(start_date, month_start)
            end_in_month = min(end_date, month_end)
            
            # Convert back to string format for our function
            start_in_month_str = start_in_month.strftime("%Y-%m-%d")
            end_in_month_str = end_in_month.strftime("%Y-%m-%d")
            
            # Calculate working days for this part of the leave in this month
            leave["days_in_month"] = get_working_days(start_in_month_str, end_in_month_str)
            
        return leaves
    except Exception as e:
        logger.exception(f"Error fetching leaves for user {emp_id} in month {month} and year {year}")
        raise HTTPException(status_code=500, detail=str(e))

def calculate_lwp_for_month(emp_id: str, month: int, year: int, hostname: str):
    """
    Calculate Leave Without Pay (LWP) for a specific month.
    LWP is counted for days where employee is:
    1. Absent without leave
    2. Has pending leave
    3. Has rejected leave
    Excludes weekends and public holidays.
    """
    try:
        # Get month start and end dates
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)

        month_start_str = month_start.strftime("%Y-%m-%d")
        month_end_str = month_end.strftime("%Y-%m-%d")

        month = month_start.month
        year = month_start.year

        # Get attendance records for the month
        attendance_records = get_employee_attendance_by_month(emp_id, month, year,hostname)
        
        # Get leaves for the month
        leaves = get_employee_leaves_by_month_for_emp_id_db(emp_id, year, month, hostname)

        lwp_days = 0
        current_date = month_start

        print("************************************************")
        print("emp_id", emp_id)
        print("leaves", leaves)
        print("attendance_records", attendance_records)
        print("month_start", month_start)
        print("month_end", month_end)
        print("************************************************")


        while current_date <= month_end:
            current_date_str = current_date.strftime("%Y-%m-%d")
            
            # Skip weekends and public holidays
            if is_weekend(current_date) or is_public_holiday(current_date, hostname):
                current_date += timedelta(days=1)
                continue

            # Check if present on this day
            is_present = any(
                datetime.strptime(att["checkin_time"], "%Y-%m-%d").date() == current_date.date()
                for att in attendance_records
            )

            if not is_present:
                # Check if on approved leave
                has_approved_leave = any(
                    datetime.strptime(leave["start_date"], "%Y-%m-%d").date() <= current_date.date() <= 
                    datetime.strptime(leave["end_date"], "%Y-%m-%d").date() and
                    leave["status"] == LeaveStatus.APPROVED
                    for leave in leaves
                )

                if not has_approved_leave:
                    # Check if day has pending or rejected leave
                    has_pending_rejected_leave = any(
                        datetime.strptime(leave["start_date"], "%Y-%m-%d").date() <= current_date.date() <= 
                        datetime.strptime(leave["end_date"], "%Y-%m-%d").date() and
                        leave["status"] in [LeaveStatus.PENDING, LeaveStatus.REJECTED]
                        for leave in leaves
                    )

                    # Count as LWP if absent without approved leave
                    if not has_approved_leave or has_pending_rejected_leave:
                        lwp_days += 1

            current_date += timedelta(days=1)

        return lwp_days
    except Exception as e:
        logger.exception(f"Error calculating LWP for user {emp_id}")
        raise HTTPException(status_code=500, detail=str(e))