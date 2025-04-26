from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime
import uuid

class SalaryComponentBase(BaseModel):
    sc_id: Optional[str] = None
    name: str = Field(..., min_length=2)
    type: Literal['earning', 'deduction']
    key: Optional[str] = None
    max_value: Optional[float] = None
    declared_value: Optional[float] = None
    actual_value: Optional[float] = None
    is_active: bool = False
    is_visible: bool = False
    is_mandatory: bool = False
    declaration_required: bool = False
    description: Optional[str] = None

class SalaryComponentCreate(SalaryComponentBase):
    pass

class SalaryComponentUpdate(BaseModel):
    sc_id: str
    name: Optional[str]
    type: Optional[Literal['earning', 'deduction']]
    key: Optional[str]
    max_value: Optional[float]      # Maximum value for the component - On Assignment
    declared_value: Optional[float] # Declared value for the component - On Declaration
    actual_value: Optional[float]   # Actual value for the component - On Actual Calculation
    is_active: Optional[bool]       # Whether the component is active
    is_visible: Optional[bool]      # Whether the component is visible
    is_mandatory: Optional[bool]    # Whether the component is mandatory
    declaration_required: Optional[bool] # Whether the component is editable by the employee
    description: Optional[str]      # Description for the component

class SalaryComponentInDB(SalaryComponentBase):
    sc_id: str

    class Config:
        from_attributes = True

class SalaryComponentAssignment(BaseModel):
    sc_id: str
    max_value: float = Field(ge=0)

class SalaryComponentAssignmentRequest(BaseModel):
    components: List[SalaryComponentAssignment]

class SalaryComponentDeclaration(BaseModel):
    sc_id: str
    declared_value: float = Field(ge=0)

class SalaryComponentDeclarationRequest(BaseModel):
    components: List[SalaryComponentDeclaration]

