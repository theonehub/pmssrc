from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class SalaryChangeReason(str, Enum):
    PROMOTION = "promotion"
    ANNUAL_INCREMENT = "annual_increment"
    PERFORMANCE_BONUS = "performance_bonus"
    MARKET_ADJUSTMENT = "market_adjustment"
    ROLE_CHANGE = "role_change"
    CORRECTION = "correction"
    OTHER = "other"

class SalaryHistoryBase(BaseModel):
    employee_id: str
    effective_date: date = Field(..., description="Date from which the salary change is effective")
    reason: SalaryChangeReason = Field(..., description="Reason for salary change")
    
    # Salary Components (Annual amounts)
    basic_salary: float = Field(..., ge=0, description="Annual basic salary")
    dearness_allowance: float = Field(0.0, ge=0, description="Annual dearness allowance")
    hra: float = Field(0.0, ge=0, description="Annual house rent allowance")
    special_allowance: float = Field(0.0, ge=0, description="Annual special allowance")
    bonus: float = Field(0.0, ge=0, description="Annual bonus")
    commission: float = Field(0.0, ge=0, description="Annual commission")
    
    # Additional fields
    remarks: Optional[str] = Field(None, description="Additional remarks for the change")
    approved_by: Optional[str] = Field(None, description="Employee ID of approver")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    
    # Tax recalculation flag
    tax_recalculation_required: bool = Field(True, description="Whether tax recalculation is needed")
    tax_recalculated_at: Optional[datetime] = Field(None, description="When tax was recalculated")

class SalaryHistoryCreate(SalaryHistoryBase):
    pass

class SalaryHistoryUpdate(BaseModel):
    effective_date: Optional[date] = None
    reason: Optional[SalaryChangeReason] = None
    basic_salary: Optional[float] = Field(None, ge=0)
    dearness_allowance: Optional[float] = Field(None, ge=0)
    hra: Optional[float] = Field(None, ge=0)
    special_allowance: Optional[float] = Field(None, ge=0)
    bonus: Optional[float] = Field(None, ge=0)
    commission: Optional[float] = Field(None, ge=0)
    remarks: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    tax_recalculation_required: Optional[bool] = None
    tax_recalculated_at: Optional[datetime] = None

class SalaryHistoryInDB(SalaryHistoryBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SalaryChangeRequest(BaseModel):
    """Model for requesting salary changes"""
    employee_id: str
    effective_date: date
    reason: SalaryChangeReason
    new_salary_components: dict = Field(..., description="New salary components as key-value pairs")
    remarks: Optional[str] = None
    
class SalaryProjection(BaseModel):
    """Model for projecting annual salary considering mid-year changes"""
    employee_id: str
    tax_year: str
    projected_annual_basic: float
    projected_annual_da: float
    projected_annual_hra: float
    projected_annual_special_allowance: float
    projected_annual_bonus: float
    projected_annual_gross: float
    salary_changes_count: int
    last_change_date: Optional[date]
    calculation_date: datetime 