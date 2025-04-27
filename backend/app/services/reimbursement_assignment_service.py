from datetime import datetime
from models.reimbursement_assignment import ReimbursementAssignmentCreate
from database.reimbursement_assignment_database import create_assignment, get_user_assignments, get_all_assignments


async def assign_reimbursements_to_user(data: ReimbursementAssignmentCreate, hostname: str):
    return await create_assignment(data, hostname)

async def get_user_reimbursement_assignments(emp_id: str, hostname: str):
    return await get_user_assignments(emp_id, hostname)

async def get_all_user_reimbursement_assignments(skip: int = 0, limit: int = 10, search: str = None, hostname: str = None):
    return await get_all_assignments(skip, limit, search, hostname)