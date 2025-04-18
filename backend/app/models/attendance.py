from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Attendance(BaseModel):
    empId: str
    checkin_time: Optional[datetime] = None
    checkout_time: Optional[datetime] = None
    date: int = datetime.today().day
    month: int = datetime.today().month
    year: int = datetime.today().year
    marked_by: Optional[str] = None

