import logging
from datetime import datetime, timedelta
from models.leave_model import EmployeeLeave, LeaveStatus
from database.database_connector import connect_to_database
from uuid import uuid4

logger = logging.getLogger(__name__)

def get_employee_leave_collection(hostname: str):
    """
    Returns the employee leave collection for the specified company.
    """
    db = connect_to_database(hostname)
    return db["employee_leave"]

def create_employee_leave(leave: EmployeeLeave, hostname: str):
    """
    Creates a new employee leave in the employee leave collection.
    """
    collection = get_employee_leave_collection(hostname)
    leave_dict = leave.model_dump()
    leave_dict["created_at"] = datetime.now()
    leave_dict["created_by"] = leave.emp_id
    result = collection.insert_one(leave_dict)
    return str(result.inserted_id)

def get_employee_leave_by_id(leave_id: str, hostname: str):
    """
    Retrieves an employee leave by its ID.
    """
    collection = get_employee_leave_collection(hostname)
    leave = collection.find_one({"leave_id": leave_id})
    return EmployeeLeave(**leave) if leave else None

def get_employee_leaves_by_emp_id(emp_id: str, hostname: str):
    """
    Retrieves all employee leaves for a specific employee.
    """
    collection = get_employee_leave_collection(hostname)
    leaves = collection.find({"emp_id": emp_id}).to_list(length=None)
    return [EmployeeLeave(**leave) for leave in leaves]

def update_employee_leave(leave_id: str, update_data: dict, hostname: str):
    """
    Updates an employee leave record in the database.
    """
    try:
        collection = get_employee_leave_collection(hostname)
        result = collection.update_one(
            {"leave_id": leave_id},
            {"$set": update_data}
        )
        return result
    except Exception as e:
        logger.exception(f"Error updating employee leave {leave_id}")
        raise e

def delete_employee_leave(leave_id: str, hostname: str):
    """
    Deletes an employee leave by its ID.
    """
    collection = get_employee_leave_collection(hostname)
    collection.delete_one({"leave_id": leave_id}) 

def get_all_employee_leaves(hostname: str, emp_ids: list = None):
    """
    Retrieves all employee leaves from the employee leave collection.
    """
    collection = get_employee_leave_collection(hostname)
    if emp_ids:
        leaves = collection.find({"emp_id": {"$in": emp_ids}}).to_list(length=None)
    else:
        leaves = collection.find().to_list(length=None)
    return [EmployeeLeave(**leave) for leave in leaves]

def get_employee_leaves_by_manager_id(manager_id: str, hostname: str):
    """
    Retrieves all employee leaves for a specific manager.
    """
    collection = get_employee_leave_collection(hostname)
    leaves = collection.find({"manager_id": manager_id}).to_list(length=None)
    return [EmployeeLeave(**leave) for leave in leaves]


def get_employee_leaves_by_month_for_emp_id(emp_id: str, year: int, month: int, month_start: datetime, month_end: datetime, hostname: str):
    """
    Retrieves all employee leaves for a specific employee in a specific month.
    """
    collection = get_employee_leave_collection(hostname)
    
    month_start_str = month_start.strftime("%Y-%m-%d")
    month_end_str = month_end.strftime("%Y-%m-%d")
    leaves = list(collection.find({
        "emp_id": emp_id,
        "$or": [
            # Leave starts in this month
            {"start_date": {"$gte": month_start_str, "$lte": month_end_str}},
            # Leave ends in this month
            {"end_date": {"$gte": month_start_str, "$lte": month_end_str}},
            # Leave spans over this month
            {"$and": [
                {"start_date": {"$lt": month_start_str}},
                {"end_date": {"$gt": month_end_str}}
            ]}
        ]
    }))
    logger.info(f"Leaves: {leaves}")
        
    return [EmployeeLeave(**leave) for leave in leaves]