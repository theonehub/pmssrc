from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class ReimbursementRequestBase(BaseModel):
    emp_id: str
    reimbursement_id: str = str(uuid.uuid4())
    reimbursement_type_id: str
    amount: float
    note: Optional[str] = None


class ReimbursementRequestCreate(ReimbursementRequestBase):
    pass


class ReimbursementRequestOut(BaseModel):
    emp_id: str
    reimbursement_id: str
    reimbursement_type_name: str
    amount: float
    note: Optional[str]
    status: str
    file_url: Optional[str]
    submitted_at: datetime
