from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Attendance(BaseModel):
    emp_id: str
    attendance_id: str
    checkin_time: Optional[datetime] = None
    checkout_time: Optional[datetime] = None
    date: datetime
    marked_by: Optional[str] = None

