from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReimbursementTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    max_limit: int

class ReimbursementTypeCreate(ReimbursementTypeBase):
    pass

class ReimbursementTypeUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_active: Optional[bool]
    max_limit: Optional[int]

class ReimbursementTypeInDB(ReimbursementTypeBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True
