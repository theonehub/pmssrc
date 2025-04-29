from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PublicHoliday(BaseModel):
    holiday_id: Optional[str] = None
    name: str
    date: datetime
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    is_active: bool = True 