from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AssignedReimbursement(BaseModel):
    type_id: str
    monthly_limit: Optional[float] = None
    required_docs: Optional[bool] = False
    description: Optional[str] = None

class ReimbursementAssignmentCreate(BaseModel):
    user_id: str
    reimbursement_type_ids: List[str]

class ReimbursementAssignmentInDB(ReimbursementAssignmentCreate):
    created_at: datetime
    updated_at: datetime

class ReimbursementAssignmentOut(BaseModel):
    id: str  # user id
    name: str
    email: str
    assigned_reimbursements: List[AssignedReimbursement] = []
