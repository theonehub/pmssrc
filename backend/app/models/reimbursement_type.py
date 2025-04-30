from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReimbursementTypeBase(BaseModel):
    reimbursement_type_id: Optional[str] = None
    reimbursement_type_name: str
    description: Optional[str] = None
    is_active: bool = True
    max_limit: int

class ReimbursementTypeCreate(ReimbursementTypeBase):
    pass

class ReimbursementTypeUpdate(BaseModel):
    reimbursement_type_id: Optional[str] = None
    reimbursement_type_name: Optional[str]
    description: Optional[str]
    is_active: Optional[bool]
    max_limit: Optional[int]

class ReimbursementTypeInDB(ReimbursementTypeBase):
    reimbursement_type_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReimbursementType(BaseModel):
    reimbursement_type_id: str
    reimbursement_type_name: str
    description: Optional[str] = None
    is_active: bool = True
    max_limit: int