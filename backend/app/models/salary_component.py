from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
import uuid

class SalaryComponentBase(BaseModel):
    sc_id: Optional[str] = None
    name: str = Field(..., min_length=2)
    type: Literal['earning', 'deduction']
    key: Optional[str] = None
    formula: Optional[str] = None
    is_active: bool = True
    description: Optional[str] = None

class SalaryComponentCreate(SalaryComponentBase):
    pass

class SalaryComponentUpdate(BaseModel):
    sc_id: str
    name: Optional[str]
    type: Optional[Literal['earning', 'deduction']]
    key: Optional[str]
    formula: Optional[str]
    is_active: Optional[bool]
    description: Optional[str]

class SalaryComponentInDB(SalaryComponentBase):
    sc_id: str
    created_at: datetime

    class Config:
        from_attributes = True

