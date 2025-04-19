import logging
from datetime import datetime
from fastapi import HTTPException
from models.leave_model import EmployeeLeave, LeaveStatus
from database import employee_leave_collection, user_collection

logger = logging.getLogger(__name__)

def apply_leave(leave: EmployeeLeave):
    """
    Creates a new leave application in the employee_leave_collection.
    """
    try:
        # Validate if user exists
        user = user_collection.find_one({"empId": leave.empId})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate if leave type exists in user's leave balance
        if leave.leave_name not in user.get("leave_balance", {}):
            raise HTTPException(status_code=400, detail="Invalid leave type")
        
        # Calculate number of days
        start_date = datetime.strptime(leave.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(leave.end_date, "%Y-%m-%d")
        days = (end_date - start_date).days + 1
        
        # Validate if user has enough leave balance
        if user["leave_balance"][leave.leave_name] < days:
            raise HTTPException(status_code=400, detail="Insufficient leave balance")
        
        # Create leave application
        leave_result = employee_leave_collection.insert_one(leave.model_dump())
        logger.info(f"Leave application created successfully for user {leave.empId}")
        return {"msg": "Leave application submitted successfully", "inserted_id": str(leave_result.inserted_id)}
    except Exception as e:
        logger.exception("Exception occurred during leave application")
        raise HTTPException(status_code=500, detail=str(e))

def get_user_leaves(empId: str):
    """
    Returns all leave applications for a user.
    """
    try:
        leaves = list(employee_leave_collection.find({"empId": empId}))
        return leaves
    except Exception as e:
        logger.exception(f"Error fetching leaves for user {empId}")
        raise HTTPException(status_code=500, detail=str(e))

def get_pending_leaves(managerId: str):
    """
    Returns all pending leave applications for users under a manager.
    """
    try:
        # Get all users under the manager
        users = list(user_collection.find({"managerId": managerId}))
        empIds = [user["empId"] for user in users]
        
        # Get pending leaves for these users
        leaves = list(employee_leave_collection.find({
            "empId": {"$in": empIds},
            "status": LeaveStatus.PENDING
        }))
        return leaves
    except Exception as e:
        logger.exception(f"Error fetching pending leaves for manager {managerId}")
        raise HTTPException(status_code=500, detail=str(e))

def update_leave_status(leave_id: str, status: LeaveStatus, approved_by: str):
    """
    Updates the status of a leave application.
    """
    try:
        update_data = {
            "status": status,
            "approved_by": approved_by,
            "approved_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        result = employee_leave_collection.update_one(
            {"_id": leave_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Leave application not found")
            
        return {"msg": "Leave status updated successfully"}
    except Exception as e:
        logger.exception(f"Error updating leave status for leave {leave_id}")
        raise HTTPException(status_code=500, detail=str(e)) 