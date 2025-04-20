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
    empId: Optional[str] = None
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

    class Config:
        json_schema_extra = {
            "example": {
                "empId": "EMP001",
                "leave_name": "Annual Leave",
                "start_date": "2024-03-01",
                "end_date": "2024-03-05",
                "status": "pending",
                "reason": "Family vacation"
            }
        } 