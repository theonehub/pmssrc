from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime
import uuid

class SalaryComponentBase(BaseModel):
    sc_id: Optional[str] = None
    name: str = Field(..., min_length=2)
    type: Literal['earning', 'deduction']
    key: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    declared_value: Optional[float] = None
    actual_value: Optional[float] = None
    formula: Optional[str] = None
    is_active: bool = True
    is_visible: bool = True
    description: Optional[str] = None

class SalaryComponentCreate(SalaryComponentBase):
    pass

class SalaryComponentUpdate(BaseModel):
    sc_id: str
    name: Optional[str]
    type: Optional[Literal['earning', 'deduction']]
    key: Optional[str]
    min_value: Optional[float]      # Minimum value for the component - On Assignment
    max_value: Optional[float]      # Maximum value for the component - On Assignment
    declared_value: Optional[float] # Declared value for the component - On Declaration
    actual_value: Optional[float]   # Actual value for the component - On Actual Calculation
    formula: Optional[str]          # Formula for the component
    is_active: Optional[bool]       # Whether the component is active
    is_visible: Optional[bool]      # Whether the component is visible
    description: Optional[str]      # Description for the component

class SalaryComponentInDB(SalaryComponentBase):
    sc_id: str

    class Config:
        from_attributes = True

class SalaryComponentAssignment(BaseModel):
    sc_id: str
    min_value: float = Field(ge=0)
    max_value: float = Field(ge=0)

class SalaryComponentAssignmentRequest(BaseModel):
    components: List[SalaryComponentAssignment]

class SalaryComponentDeclaration(BaseModel):
    sc_id: str
    declared_value: float = Field(ge=0)

class SalaryComponentDeclarationRequest(BaseModel):
    components: List[SalaryComponentDeclaration]

