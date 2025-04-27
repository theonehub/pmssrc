from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Attendance(BaseModel):
    emp_id: str
    attendance_id: str
    checkin_time: Optional[datetime] = None
    checkout_time: Optional[datetime] = None
    date: int = datetime.today().day
    month: int = datetime.today().month
    year: int = datetime.today().year
    marked_by: Optional[str] = None

