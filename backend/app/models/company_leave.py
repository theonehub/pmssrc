from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanyLeaveBase(BaseModel):
    name: str
    count: int
    is_active: bool = True

class CompanyLeaveCreate(CompanyLeaveBase):
    pass

class CompanyLeaveUpdate(BaseModel):
    name: Optional[str]
    count: Optional[int]
    is_active: Optional[bool]

class CompanyLeaveInDB(CompanyLeaveBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True 