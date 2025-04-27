from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AssignedReimbursement(BaseModel):
    reimbursement_type_id: str
    monthly_limit: Optional[float] = None
    required_docs: Optional[bool] = False
    description: Optional[str] = None

class ReimbursementAssignmentCreate(BaseModel):
    reimbursement_assignment_id: str
    emp_id: str
    reimbursement_type_ids: List[str]

class ReimbursementAssignmentInDB(ReimbursementAssignmentCreate):
    created_at: datetime
    updated_at: datetime

class ReimbursementAssignmentOut(BaseModel):
    reimbursement_assignment_id: str
    emp_id: str
    assigned_reimbursements: List[AssignedReimbursement] = []

class PaginatedReimbursementAssignmentOut(BaseModel):
    data: List[ReimbursementAssignmentOut]
    total: int
    page: int
    page_size: int
