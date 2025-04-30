from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class EmployeeLeave(BaseModel):
    """
    Model for employee leave applications
    """
    emp_id: Optional[str] = None
    emp_name: Optional[str] = None
    emp_email: Optional[str] = None
    leave_id: Optional[str] = None
    leave_name: str
    start_date: str
    end_date: str
    leave_count: Optional[int] = None
    status: LeaveStatus = LeaveStatus.PENDING
    applied_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    approved_by: Optional[str] = None
    approved_date: Optional[str] = None
    reason: Optional[str] = None
