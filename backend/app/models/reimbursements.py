from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReimbursementRequestBase(BaseModel):
    type_id: str
    amount: float
    note: Optional[str] = None


class ReimbursementRequestCreate(ReimbursementRequestBase):
    pass


class ReimbursementRequestOut(BaseModel):
    id: str
    type_name: str
    amount: float
    note: Optional[str]
    status: str
    file_url: Optional[str]
    submitted_at: datetime
