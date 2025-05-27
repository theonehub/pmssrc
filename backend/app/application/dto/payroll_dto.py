"""
Payroll Application Layer DTOs
Data Transfer Objects for payroll operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import date, datetime
from enum import Enum


class PayoutStatusEnum(str, Enum):
    """Payout status enumeration for DTOs"""
    PENDING = "pending"
    CALCULATED = "calculated"
    PROCESSED = "processed"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PayslipFormatEnum(str, Enum):
    """Payslip format enumeration for DTOs"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"


# ==================== REQUEST DTOs ====================

class PayoutCalculationRequestDTO(BaseModel):
    """Request DTO for payout calculation"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    override_salary: Optional[Dict[str, float]] = None
    force_recalculate: bool = False
    
    @validator('override_salary')
    def validate_override_salary(cls, v):
        if v is not None:
            for key, value in v.items():
                if value < 0:
                    raise ValueError(f"Override salary component {key} cannot be negative")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "month": 3,
                "year": 2024,
                "override_salary": {
                    "basic_salary": 50000.0,
                    "hra": 25000.0
                },
                "force_recalculate": False
            }
        }


class PayoutCreateRequestDTO(BaseModel):
    """Request DTO for creating payout record"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    pay_period_start: date
    pay_period_end: date
    payout_date: date
    gross_salary: float = Field(..., ge=0)
    net_salary: float = Field(..., ge=0)
    total_deductions: float = Field(..., ge=0)
    status: PayoutStatusEnum = PayoutStatusEnum.PENDING
    notes: Optional[str] = None
    
    @validator('pay_period_end')
    def validate_pay_period(cls, v, values):
        if 'pay_period_start' in values and v < values['pay_period_start']:
            raise ValueError("Pay period end cannot be before start date")
        return v
    
    @validator('net_salary')
    def validate_net_salary(cls, v, values):
        if 'gross_salary' in values and 'total_deductions' in values:
            expected_net = values['gross_salary'] - values['total_deductions']
            if abs(v - expected_net) > 0.01:  # Allow for rounding differences
                raise ValueError("Net salary should equal gross salary minus total deductions")
        return v


class PayoutUpdateRequestDTO(BaseModel):
    """Request DTO for updating payout record"""
    status: Optional[PayoutStatusEnum] = None
    gross_salary: Optional[float] = Field(None, ge=0)
    net_salary: Optional[float] = Field(None, ge=0)
    total_deductions: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    updated_by: str = Field(..., min_length=1)


class BulkPayoutRequestDTO(BaseModel):
    """Request DTO for bulk payout processing"""
    employee_ids: List[str] = Field(..., min_items=1, max_items=1000)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    auto_calculate_tax: bool = True
    auto_approve: bool = False
    override_salary: Optional[Dict[str, Dict[str, float]]] = None  # employee_id -> salary components
    notes: Optional[str] = None
    
    @validator('employee_ids')
    def validate_employee_ids(cls, v):
        if len(set(v)) != len(v):
            raise ValueError("Duplicate employee IDs found")
        return v


class PayoutSearchFiltersDTO(BaseModel):
    """Request DTO for payout search filters"""
    employee_id: Optional[str] = None
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2020, le=2030)
    status: Optional[PayoutStatusEnum] = None
    min_gross_salary: Optional[float] = Field(None, ge=0)
    max_gross_salary: Optional[float] = Field(None, ge=0)
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    
    @validator('max_gross_salary')
    def validate_salary_range(cls, v, values):
        if v is not None and 'min_gross_salary' in values and values['min_gross_salary'] is not None:
            if v < values['min_gross_salary']:
                raise ValueError("Max gross salary cannot be less than min gross salary")
        return v


class PayslipGenerationRequestDTO(BaseModel):
    """Request DTO for payslip generation"""
    payout_id: str = Field(..., min_length=1)
    format: PayslipFormatEnum = PayslipFormatEnum.PDF
    include_company_logo: bool = True
    custom_template: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAYOUT_123",
                "format": "pdf",
                "include_company_logo": True
            }
        }


class PayslipEmailRequestDTO(BaseModel):
    """Request DTO for emailing payslip"""
    payout_id: str = Field(..., min_length=1)
    recipient_email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    custom_subject: Optional[str] = None
    custom_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "payout_id": "PAYOUT_123",
                "recipient_email": "employee@company.com",
                "custom_subject": "Your Salary Slip for March 2024"
            }
        }


class BulkPayslipRequestDTO(BaseModel):
    """Request DTO for bulk payslip generation"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    format: PayslipFormatEnum = PayslipFormatEnum.PDF
    employee_ids: Optional[List[str]] = None  # If None, process all employees
    status_filter: Optional[PayoutStatusEnum] = PayoutStatusEnum.PROCESSED
    auto_email: bool = False
    
    @validator('employee_ids')
    def validate_employee_ids(cls, v):
        if v is not None and len(set(v)) != len(v):
            raise ValueError("Duplicate employee IDs found")
        return v


# ==================== RESPONSE DTOs ====================

class SalaryComponentsResponseDTO(BaseModel):
    """Response DTO for salary components"""
    basic: float
    dearness_allowance: float
    hra: float
    special_allowance: float
    bonus: float
    commission: float = 0.0
    transport_allowance: float = 0.0
    medical_allowance: float = 0.0
    other_allowances: float = 0.0
    total_earnings: float


class DeductionComponentsResponseDTO(BaseModel):
    """Response DTO for deduction components"""
    epf_employee: float
    esi_employee: float
    professional_tax: float
    tds: float
    advance_deduction: float = 0.0
    loan_deduction: float = 0.0
    other_deductions: float = 0.0
    total_deductions: float


class AttendanceInfoResponseDTO(BaseModel):
    """Response DTO for attendance information"""
    total_days_in_month: int
    working_days_in_period: int
    lwp_days: int
    effective_working_days: int
    working_ratio: float
    effective_working_ratio: float
    overtime_hours: float = 0.0


class TaxInfoResponseDTO(BaseModel):
    """Response DTO for tax information"""
    regime: str
    annual_tax_liability: float
    monthly_tds: float
    exemptions_claimed: float = 0.0
    standard_deduction: float = 0.0
    section_80c_claimed: float = 0.0


class PayoutResponseDTO(BaseModel):
    """Response DTO for payout data"""
    id: str
    employee_id: str
    pay_period_start: date
    pay_period_end: date
    payout_date: date
    salary_components: SalaryComponentsResponseDTO
    deduction_components: DeductionComponentsResponseDTO
    attendance_info: AttendanceInfoResponseDTO
    tax_info: TaxInfoResponseDTO
    gross_salary: float
    total_deductions: float
    net_salary: float
    status: PayoutStatusEnum
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "PAYOUT_123",
                "employee_id": "EMP001",
                "pay_period_start": "2024-03-01",
                "pay_period_end": "2024-03-31",
                "payout_date": "2024-03-31",
                "gross_salary": 100000.0,
                "total_deductions": 25000.0,
                "net_salary": 75000.0,
                "status": "processed"
            }
        }


class PayslipResponseDTO(BaseModel):
    """Response DTO for payslip data"""
    payslip_id: str
    payout_id: str
    employee_id: str
    format: PayslipFormatEnum
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: datetime
    download_url: Optional[str] = None


class PayslipEmailResponseDTO(BaseModel):
    """Response DTO for payslip email operation"""
    payslip_id: str
    payout_id: str
    employee_id: str
    recipient_email: str
    email_status: str
    sent_at: datetime
    message: str


class BulkPayoutResponseDTO(BaseModel):
    """Response DTO for bulk payout processing"""
    batch_id: str
    month: int
    year: int
    total_employees: int
    successful_count: int
    failed_count: int
    successful_payouts: List[str]  # List of payout IDs
    failed_employees: List[Dict[str, str]]  # List of {employee_id, error}
    processing_duration: float
    created_at: datetime


class BulkPayslipResponseDTO(BaseModel):
    """Response DTO for bulk payslip generation"""
    batch_id: str
    month: int
    year: int
    total_payslips: int
    successful_generations: int
    failed_generations: int
    successful_payslips: List[PayslipResponseDTO]
    failed_payslips: List[Dict[str, str]]  # List of {payout_id, error}
    processing_duration: float
    created_at: datetime


class PayoutSummaryResponseDTO(BaseModel):
    """Response DTO for payout summary"""
    month: int
    year: int
    total_employees: int
    total_gross_salary: float
    total_deductions: float
    total_net_salary: float
    average_gross_salary: float
    average_net_salary: float
    status_breakdown: Dict[str, int]  # status -> count
    created_at: datetime


class PayoutHistoryResponseDTO(BaseModel):
    """Response DTO for payout history"""
    employee_id: str
    year: int
    payouts: List[PayoutResponseDTO]
    yearly_summary: Dict[str, float]  # gross, deductions, net, etc.
    months_paid: int
    average_monthly_gross: float
    average_monthly_net: float


class PayslipHistoryResponseDTO(BaseModel):
    """Response DTO for payslip history"""
    employee_id: str
    year: int
    payslips: List[PayslipResponseDTO]
    total_downloads: int
    last_generated: Optional[datetime] = None


# ==================== ANALYTICS DTOs ====================

class PayrollAnalyticsRequestDTO(BaseModel):
    """Request DTO for payroll analytics"""
    start_month: int = Field(..., ge=1, le=12)
    start_year: int = Field(..., ge=2020, le=2030)
    end_month: int = Field(..., ge=1, le=12)
    end_year: int = Field(..., ge=2020, le=2030)
    department: Optional[str] = None
    include_inactive_employees: bool = False
    
    @validator('end_year')
    def validate_date_range(cls, v, values):
        if 'start_year' in values:
            start_date = (values['start_year'], values.get('start_month', 1))
            end_date = (v, values.get('end_month', 12))
            if end_date < start_date:
                raise ValueError("End date cannot be before start date")
        return v


class PayrollAnalyticsResponseDTO(BaseModel):
    """Response DTO for payroll analytics"""
    period: str
    total_payouts: int
    total_gross_amount: float
    total_net_amount: float
    total_deductions: float
    average_gross_per_employee: float
    average_net_per_employee: float
    department_wise_breakdown: Dict[str, Dict[str, float]]
    monthly_trends: List[Dict[str, Any]]
    top_earners: List[Dict[str, Any]]
    deduction_analysis: Dict[str, float]
    compliance_metrics: Dict[str, Any]
    generated_at: datetime


# ==================== ERROR DTOs ====================

class PayrollErrorResponseDTO(BaseModel):
    """Response DTO for payroll errors"""
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: Optional[str] = None


class ValidationErrorResponseDTO(BaseModel):
    """Response DTO for validation errors"""
    field: str
    message: str
    invalid_value: Any


class BulkOperationErrorResponseDTO(BaseModel):
    """Response DTO for bulk operation errors"""
    operation: str
    total_items: int
    successful_items: int
    failed_items: int
    errors: List[Dict[str, Any]]
    timestamp: datetime 