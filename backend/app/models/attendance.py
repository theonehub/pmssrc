from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class AttendanceBase(BaseModel):
    employee_id: str
    month: str  # Format: YYYY-MM
    lwp_days: int = Field(ge=0)
    remarks: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    lwp_days: Optional[int] = Field(ge=0)
    remarks: Optional[str] = None

class AttendanceInDB(AttendanceBase):
    id: str
    created_at: datetime
    updated_at: datetime
