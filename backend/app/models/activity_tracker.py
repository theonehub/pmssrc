from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ActivityTracker(BaseModel):
    activityId: str
    empId: str
    activity: str
    date: datetime
    metadata: dict
    
class ActivityTrackerMetadata(BaseModel):
    empId: str
    activity: str
    date: datetime
    metadata: dict
    