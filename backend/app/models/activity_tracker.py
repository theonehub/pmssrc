from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ActivityTracker(BaseModel):
    activity_id: str
    emp_id: str
    activity: str
    date: datetime
    metadata: dict
    
class ActivityTrackerMetadata(BaseModel):
    emp_id: str
    activity: str
    date: datetime
    metadata: dict
    