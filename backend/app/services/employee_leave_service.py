import logging
from datetime import datetime
from fastapi import HTTPException
from models.leave_model import EmployeeLeave, LeaveStatus
from database import employee_leave_collection, user_collection
from uuid import uuid4

logger = logging.getLogger(__name__)

def apply_leave(leave: EmployeeLeave):
    """
    Creates a new leave application in the employee_leave_collection.
    """
    try:
        if not leave.leave_id:
            leave.leave_id = str(uuid4())
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
        leave.leave_count = days
        
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

def leave_balance(empId: str):
    """
    Returns the leave balance for a user.
    """
    try:
        user = user_collection.find_one({"empId": empId})
        leave_balance = {}

        print(user.get("leave_balance", {}))
        for leave_type, balance in user.get("leave_balance", {}).items():
            print(leave_type, balance)
            leave_balance[leave_type] = balance
        
        return leave_balance
        
    except Exception as e:
        logger.exception(f"Error fetching leave balance for user {empId}")
        raise HTTPException(status_code=500, detail=str(e))


def get_user_leaves(empId: str):
    """
    Returns all leave applications for a user.
    """
    try:
        leaves = list(employee_leave_collection.find({"empId": empId}))
        for leave in leaves:
            leave["id"] = str(leave["_id"])
            del leave["_id"]
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
            {"leave_id": leave_id},
            {"$set": update_data}
        )

        leave = employee_leave_collection.find_one({"leave_id": leave_id})
        user = user_collection.find_one({"empId": leave["empId"]})
        user["leave_balance"][leave["leave_name"]] -= leave["leave_count"]
        user_collection.update_one({"empId": leave["empId"]}, {"$set": {"leave_balance": user["leave_balance"]}})
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Leave application not found")
            
        return {"msg": "Leave status updated successfully"}
    except Exception as e:
        logger.exception(f"Error updating leave status for leave {leave_id}")
        raise HTTPException(status_code=500, detail=str(e))

def update_leave_request(leave_id: str, leave_data: dict):
    """
    Updates an existing leave request.
    """
    try:
        # Get the existing leave request
        existing_leave = employee_leave_collection.find_one({"leave_id": leave_id})
        if not existing_leave:
            raise HTTPException(status_code=404, detail="Leave request not found")
            
        # Check if leave has already started
        start_date = datetime.strptime(existing_leave["start_date"], "%Y-%m-%d")
        if start_date < datetime.now():
            raise HTTPException(status_code=400, detail="Cannot modify leave request that has already started")
            
        # Calculate new number of days
        new_start_date = datetime.strptime(leave_data["start_date"], "%Y-%m-%d")
        new_end_date = datetime.strptime(leave_data["end_date"], "%Y-%m-%d")
        new_days = (new_end_date - new_start_date).days + 1
        
        # Validate if user has enough leave balance
        user = user_collection.find_one({"empId": existing_leave["empId"]})
        if user["leave_balance"][leave_data["leave_name"]] < new_days:
            raise HTTPException(status_code=400, detail="Insufficient leave balance")
            
        # Update leave request
        update_data = {
            "leave_name": leave_data["leave_name"],
            "start_date": leave_data["start_date"],
            "end_date": leave_data["end_date"],
            "reason": leave_data["reason"],
            "leave_count": new_days,
            "status": LeaveStatus.PENDING,  # Reset status to pending
            "approved_by": None,
            "approved_date": None
        }
        
        result = employee_leave_collection.update_one(
            {"_id": leave_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Leave request not found")
            
        return {"msg": "Leave request updated successfully"}
    except Exception as e:
        logger.exception(f"Error updating leave request {leave_id}")
        raise HTTPException(status_code=500, detail=str(e))

def delete_leave_request(leave_id: str):
    """
    Deletes a leave request.
    """
    try:
        # Get the existing leave request
        existing_leave = employee_leave_collection.find_one({"leave_id": leave_id})
        if not existing_leave:
            raise HTTPException(status_code=404, detail="Leave request not found")
            
        # Check if leave has already started
        start_date = datetime.strptime(existing_leave["start_date"], "%Y-%m-%d")
        if start_date < datetime.now():
            raise HTTPException(status_code=400, detail="Cannot delete leave request that has already started")
            
        # Delete leave request
        result = employee_leave_collection.delete_one({"leave_id": leave_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Leave request not found")
            
        return {"msg": "Leave request deleted successfully"}
    except Exception as e:
        logger.exception(f"Error deleting leave request {leave_id}")
        raise HTTPException(status_code=500, detail=str(e))

def get_all_employee_leaves(manager_id: str = None):
    """
    Returns all leave applications for all employees or employees under a specific manager.
    """
    try:
        query = {}
        if manager_id:
            # Get all users under the manager
            users = list(user_collection.find({"managerId": manager_id}))
            empIds = [user["empId"] for user in users]
            query["empId"] = {"$in": empIds}
            
        leaves = list(employee_leave_collection.find(query))
        for leave in leaves:
            leave["id"] = str(leave["_id"])
            del leave["_id"]
            # Add employee details
            user = user_collection.find_one({"empId": leave["empId"]})
            if user:
                leave["employee_name"] = user.get("name", "")
                leave["employee_email"] = user.get("email", "")
        return leaves
    except Exception as e:
        logger.exception(f"Error fetching all leaves for manager {manager_id}")
        raise HTTPException(status_code=500, detail=str(e)) 