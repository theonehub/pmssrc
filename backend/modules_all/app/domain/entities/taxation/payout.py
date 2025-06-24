from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class PayoutStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    APPROVED = "approved"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PayoutFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

# Base Payout Model
class PayoutBase(BaseModel):
    employee_id: str
    pay_period_start: date
    pay_period_end: date
    payout_date: date
    frequency: PayoutFrequency = PayoutFrequency.MONTHLY
    
    # Salary Components
    basic_salary: float = Field(0.0, ge=0)
    da: float = Field(0.0, ge=0)
    hra: float = Field(0.0, ge=0)
    special_allowance: float = Field(0.0, ge=0)
    overtime: float = Field(0.0, ge=0)
    arrears: float = Field(0.0, ge=0)
    bonus: float = Field(0.0, ge=0)
    commission: float = Field(0.0, ge=0)
    
    # Deductions
    epf_employee: float = Field(0.0, ge=0)
    epf_employer: float = Field(0.0, ge=0)
    esi_employee: float = Field(0.0, ge=0)
    esi_employer: float = Field(0.0, ge=0)
    professional_tax: float = Field(0.0, ge=0)
    tds: float = Field(0.0, ge=0)
    advance_deduction: float = Field(0.0, ge=0)
    loan_deduction: float = Field(0.0, ge=0)
    other_deductions: float = Field(0.0, ge=0)
    
    # Tax Calculations
    gross_salary: float = Field(0.0, ge=0)
    total_deductions: float = Field(0.0, ge=0)
    net_salary: float = Field(0.0, ge=0)
    
    # Annual Tax Projections
    annual_gross_salary: float = Field(0.0, ge=0)
    annual_tax_liability: float = Field(0.0, ge=0)
    monthly_tds: float = Field(0.0, ge=0)
    
    # Tax Details for Payslip
    tax_regime: Optional[str] = "new"
    tax_exemptions: float = Field(0.0, ge=0)
    standard_deduction: float = Field(0.0, ge=0)
    section_80c_claimed: float = Field(0.0, ge=0)
    
    # Reimbursements
    reimbursements: float = Field(0.0, ge=0)
    
    # Attendance and Working Days
    total_days_in_month: int = Field(0, ge=0)
    working_days_in_period: int = Field(0, ge=0)
    lwp_days: int = Field(0, ge=0)
    effective_working_days: int = Field(0, ge=0)
    
    # Status and Notes
    status: PayoutStatus = PayoutStatus.PENDING
    notes: Optional[str] = None
    remarks: Optional[str] = None
    
    @validator("net_salary", always=True)
    def calculate_net_salary(cls, v, values):
        gross = values.get("gross_salary", 0)
        total_ded = values.get("total_deductions", 0)
        return max(0, gross - total_ded)
    
    @validator("gross_salary", always=True)
    def calculate_gross_salary(cls, v, values):
        components = [
            "basic_salary", "da", "hra", "special_allowance", "overtime", 
            "arrears", "bonus", "commission", "reimbursements"
        ]
        return sum(values.get(comp, 0) for comp in components)
    
    @validator("total_deductions", always=True)
    def calculate_total_deductions(cls, v, values):
        deductions = [
            "epf_employee", "esi_employee", "professional_tax", "tds",
            "advance_deduction", "loan_deduction", "other_deductions"
        ]
        return sum(values.get(ded, 0) for ded in deductions)
    
class PayoutMonthlyProjection(PayoutBase):
    pass

class PayoutCreate(PayoutBase):
    pass

class PayoutUpdate(BaseModel):
    basic_salary: Optional[float] = Field(None, ge=0)
    da: Optional[float] = Field(None, ge=0)
    hra: Optional[float] = Field(None, ge=0)
    special_allowance: Optional[float] = Field(None, ge=0)
    overtime: Optional[float] = Field(None, ge=0)
    arrears: Optional[float] = Field(None, ge=0)
    bonus: Optional[float] = Field(None, ge=0)
    commission: Optional[float] = Field(None, ge=0)
    
    epf_employee: Optional[float] = Field(None, ge=0)
    epf_employer: Optional[float] = Field(None, ge=0)
    esi_employee: Optional[float] = Field(None, ge=0)
    esi_employer: Optional[float] = Field(None, ge=0)
    professional_tax: Optional[float] = Field(None, ge=0)
    tds: Optional[float] = Field(None, ge=0)
    advance_deduction: Optional[float] = Field(None, ge=0)
    loan_deduction: Optional[float] = Field(None, ge=0)
    other_deductions: Optional[float] = Field(None, ge=0)
    
    reimbursements: Optional[float] = Field(None, ge=0)
    status: Optional[PayoutStatus] = None
    notes: Optional[str] = None
    remarks: Optional[str] = None

class PayoutInDB(PayoutBase):
    id: str
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    processed_by: Optional[str] = None
    
    class Config:
        from_attributes = True

# Payslip Model for Download
class PayslipData(BaseModel):
    employee_id: str
    employee_name: str
    employee_code: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    pan_number: Optional[str] = None
    uan_number: Optional[str] = None
    bank_account: Optional[str] = None
    
    pay_period: str
    payout_date: str
    days_in_month: int = 30
    days_worked: int = 30
    lwp_days: int = 0
    effective_working_days: int = 30
    
    # Earnings
    earnings: Dict[str, float] = {}
    total_earnings: float = 0.0
    
    # Deductions
    deductions: Dict[str, float] = {}
    total_deductions: float = 0.0
    
    # Net Pay
    net_pay: float = 0.0
    
    # Tax Information
    tax_regime: str = "new"
    ytd_gross: float = 0.0
    ytd_tax_deducted: float = 0.0
    
    # Company Information
    company_name: str
    company_address: Optional[str] = None

# Bulk Payout Processing
class BulkPayoutRequest(BaseModel):
    employee_ids: List[str]
    pay_period_start: date
    pay_period_end: date
    payout_date: date
    auto_calculate_tax: bool = True
    auto_approve: bool = False
    notes: Optional[str] = None

class BulkPayoutResponse(BaseModel):
    total_employees: int
    successful_payouts: int
    failed_payouts: int
    payout_ids: List[str]
    errors: List[Dict[str, Any]] = []

# Payout Summary for Dashboard
class PayoutSummary(BaseModel):
    month: str
    year: int
    total_employees: int
    total_gross_amount: float
    total_net_amount: float
    total_tax_deducted: float
    pending_payouts: int
    processed_payouts: int
    approved_payouts: int
    paid_payouts: int

# Monthly Payout Schedule
class PayoutSchedule(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2050)
    payout_date: int = Field(30, ge=1, le=31)  # Default 30th of every month
    auto_process: bool = Field(True)
    auto_approve: bool = Field(False)
    is_active: bool = Field(True)
    created_at: datetime = Field(default_factory=datetime.now)

# Employee Salary Slip History
class PayoutHistory(BaseModel):
    employee_id: str
    year: int
    payouts: List[PayoutInDB]
    annual_gross: float
    annual_net: float
    annual_tax_deducted: float 