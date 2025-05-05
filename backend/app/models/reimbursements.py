from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum

class ReimbursementStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ReimbursementRequestBase(BaseModel):
    reimbursement_type_id: str
    amount: float
    note: Optional[str] = None


class ReimbursementRequestCreate(ReimbursementRequestBase):
    emp_id: Optional[str] = None


class ReimbursementStatusUpdate(BaseModel):
    status: ReimbursementStatus
    comments: Optional[str] = None


class ReimbursementRequestOut(BaseModel):
    id: str
    type_name: str
    reimbursement_type_id: str
    amount: float
    note: Optional[str]
    status: str
    file_url: Optional[str]
    created_at: datetime
    comments: Optional[str] = None
    employee_name: Optional[str] = None

    class Config:
        from_attributes = True
