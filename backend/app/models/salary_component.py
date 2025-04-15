from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class SalaryComponentBase(BaseModel):
    name: str = Field(..., min_length=2)
    type: Literal['earning', 'deduction']
    description: Optional[str] = None

class SalaryComponentCreate(SalaryComponentBase):
    pass

class SalaryComponentUpdate(BaseModel):
    name: Optional[str]
    type: Optional[Literal['earning', 'deduction']]
    description: Optional[str]

class SalaryComponentInDB(SalaryComponentBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

