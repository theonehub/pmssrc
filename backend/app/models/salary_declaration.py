from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SalaryDeclarationCreate(BaseModel):
    component_id: str
    declared_amount: float

class SalaryDeclarationResponse(BaseModel):
    component_id: str
    declared_amount: float
    declared_on: datetime
    id: Optional[str] = None
