# schemas/employee_salary.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class EmployeeSalaryBase(BaseModel):
    component_id: str
    max_amount: float = Field(..., gt=0, description="Maximum amount for the component")
    min_amount: float = Field(..., ge=0, description="Minimum amount for the component")
    is_editable: bool = Field(default=False, description="If user can change amount during tax declarations")

    @validator("min_amount")
    def min_less_than_max(cls, v, values):
        max_amt = values.get("max_amount")
        if max_amt is not None and v > max_amt:
            raise ValueError("Minimum amount cannot be greater than maximum amount")
        return v

class EmployeeSalaryCreate(EmployeeSalaryBase):
    employee_id: str

class EmployeeSalaryUpdate(BaseModel):
    max_amount: Optional[float] = Field(None, gt=0)
    min_amount: Optional[float] = Field(None, ge=0)
    is_editable: Optional[bool]

    @validator("min_amount")
    def min_less_than_max(cls, v, values):
        max_amt = values.get("max_amount")
        if max_amt is not None and v is not None and v > max_amt:
            raise ValueError("Minimum amount cannot be greater than maximum amount")
        return v

class EmployeeSalaryInDB(EmployeeSalaryBase):
    id: str
    employee_id: str
    created_at: datetime

    class Config:
        orm_mode = True
        
class BulkEmployeeSalaryCreate(BaseModel):
    components: List[EmployeeSalaryCreate]


class EmployeeSalaryComponentAssignment(BaseModel):
    component_id: str
    max_amount: float = Field(..., gt=0, description="Maximum amount for the component")
    min_amount: float = Field(..., ge=0, description="Minimum amount for the component")
    is_editable: bool = Field(default=False, description="If user can change amount during tax declarations")

    @validator("min_amount")
    def min_less_than_max(cls, v, values):
        max_amt = values.get("max_amount")
        if max_amt is not None and v > max_amt:
            raise ValueError("Minimum amount cannot be greater than maximum amount")
        return v

class BulkEmployeeSalaryAssignRequest(BaseModel):
    components: List[EmployeeSalaryComponentAssignment]
    
class EmployeeSalaryWithComponentName(BaseModel):
    id: str
    employee_id: str
    component_id: str
    component_name: str
    max_amount: float
    min_amount: float
    is_editable: bool
    created_at: datetime

    class Config:
        orm_mode = True
