"""
Payroll Application Layer DTOs
Data Transfer Objects for payroll operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import date, datetime
from enum import Enum
from decimal import Decimal


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
    """Request DTO for bulk monthly payout computation."""
    
    employee_ids: List[str] = Field(..., min_items=1, description="List of employee IDs")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, le=2050, description="Year")
    
    # Employee-specific LWP and deduction details
    employee_lwp_details: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Employee-specific LWP and deduction details"
    )
    
    # Processing options
    auto_approve: bool = Field(False, description="Auto-approve all payouts")
    notes: Optional[str] = Field(None, description="Bulk processing notes")


class PayoutSearchFiltersDTO(BaseModel):
    """DTO for payout search filters."""
    
    employee_id: Optional[str] = Field(None, description="Employee ID filter")
    month: Optional[int] = Field(None, ge=1, le=12, description="Month filter")
    year: Optional[int] = Field(None, ge=2020, le=2050, description="Year filter")
    status: Optional[str] = Field(None, description="Status filter")
    
    # Date range filters
    calculation_date_from: Optional[str] = Field(None, description="Calculation date from")
    calculation_date_to: Optional[str] = Field(None, description="Calculation date to")
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=500, description="Page size")
    
    # Sorting
    sort_by: Optional[str] = Field("calculation_date", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


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


class MonthlyPayoutRequestDTO(BaseModel):
    """Request DTO for computing monthly payout."""
    
    employee_id: str = Field(..., description="Employee ID")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, le=2050, description="Year")
    
    # LWP details
    lwp_days: int = Field(0, ge=0, le=31, description="LWP days in the month")
    total_working_days: int = Field(30, ge=1, le=31, description="Total working days in month")
    
    # Additional deductions
    advance_deduction: float = Field(0.0, ge=0, description="Advance deduction amount")
    loan_deduction: float = Field(0.0, ge=0, description="Loan deduction amount")
    other_deductions: float = Field(0.0, ge=0, description="Other deductions amount")
    
    # Processing options
    auto_approve: bool = Field(False, description="Auto-approve the payout")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @validator("lwp_days")
    def validate_lwp_days(cls, v, values):
        total_days = values.get("total_working_days", 30)
        if v > total_days:
            raise ValueError("LWP days cannot exceed total working days")
        return v


class MonthlyPayoutResponseDTO(BaseModel):
    """Response DTO for monthly payout computation."""
    
    # Identifiers
    payout_id: str = Field(..., description="Payout ID")
    employee_id: str = Field(..., description="Employee ID")
    employee_name: str = Field(..., description="Employee name")
    organization_id: str = Field(..., description="Organization ID")
    month: int = Field(..., description="Month")
    year: int = Field(..., description="Year")
    
    # Salary components (LWP adjusted)
    basic_salary: float = Field(..., description="Basic salary")
    dearness_allowance: float = Field(..., description="Dearness allowance")
    hra: float = Field(..., description="HRA")
    special_allowance: float = Field(..., description="Special allowance")
    transport_allowance: float = Field(..., description="Transport allowance")
    medical_allowance: float = Field(..., description="Medical allowance")
    bonus: float = Field(..., description="Bonus")
    commission: float = Field(..., description="Commission")
    other_allowances: float = Field(..., description="Other allowances")
    
    # Deductions
    epf_employee: float = Field(..., description="EPF employee contribution")
    esi_employee: float = Field(..., description="ESI employee contribution")
    professional_tax: float = Field(..., description="Professional tax")
    tds: float = Field(..., description="TDS")
    advance_deduction: float = Field(..., description="Advance deduction")
    loan_deduction: float = Field(..., description="Loan deduction")
    other_deductions: float = Field(..., description="Other deductions")
    
    # Calculated totals
    base_monthly_gross: float = Field(..., description="Base monthly gross (before LWP)")
    adjusted_monthly_gross: float = Field(..., description="Adjusted monthly gross (after LWP)")
    total_deductions: float = Field(..., description="Total deductions")
    monthly_net_salary: float = Field(..., description="Monthly net salary")
    
    # LWP details
    lwp_days: int = Field(..., description="LWP days")
    effective_working_days: int = Field(..., description="Effective working days")
    lwp_factor: float = Field(..., description="LWP adjustment factor")
    lwp_deduction_amount: float = Field(..., description="Amount deducted due to LWP")
    
    # Tax information
    tax_regime: str = Field(..., description="Tax regime")
    annual_tax_liability: float = Field(..., description="Annual tax liability")
    tax_exemptions: float = Field(..., description="Tax exemptions")
    
    # Status and metadata
    status: str = Field(..., description="Payout status")
    calculation_date: str = Field(..., description="Calculation date")
    processed_date: Optional[str] = Field(None, description="Processing date")
    approved_by: Optional[str] = Field(None, description="Approved by")
    processed_by: Optional[str] = Field(None, description="Processed by")
    notes: Optional[str] = Field(None, description="Notes")


class PayoutUpdateDTO(BaseModel):
    """DTO for updating payout details."""
    
    # Additional deductions that can be updated
    advance_deduction: Optional[float] = Field(None, ge=0, description="Advance deduction")
    loan_deduction: Optional[float] = Field(None, ge=0, description="Loan deduction")
    other_deductions: Optional[float] = Field(None, ge=0, description="Other deductions")
    
    # Status updates
    status: Optional[str] = Field(None, description="New status")
    notes: Optional[str] = Field(None, description="Updated notes")


class PayoutSummaryDTO(BaseModel):
    """DTO for payout summary information."""
    
    month: int = Field(..., description="Month")
    year: int = Field(..., description="Year")
    total_employees: int = Field(..., description="Total employees")
    
    # Financial totals
    total_gross_amount: float = Field(..., description="Total gross amount")
    total_net_amount: float = Field(..., description="Total net amount")
    total_deductions: float = Field(..., description="Total deductions")
    total_lwp_deduction: float = Field(..., description="Total LWP deduction")
    
    # Status breakdown
    status_breakdown: Dict[str, int] = Field(..., description="Status-wise count")
    
    # Processing statistics
    pending_approvals: int = Field(0, description="Pending approvals")
    processed_payouts: int = Field(0, description="Processed payouts")
    failed_payouts: int = Field(0, description="Failed payouts")


class EmployeePayoutHistoryDTO(BaseModel):
    """DTO for employee payout history."""
    
    employee_id: str = Field(..., description="Employee ID")
    employee_name: str = Field(..., description="Employee name")
    year: int = Field(..., description="Year")
    
    # Annual totals
    annual_gross: float = Field(..., description="Annual gross salary")
    annual_net: float = Field(..., description="Annual net salary")
    annual_deductions: float = Field(..., description="Annual deductions")
    annual_lwp_deduction: float = Field(..., description="Annual LWP deduction")
    
    # Monthly breakdown
    monthly_payouts: List[MonthlyPayoutResponseDTO] = Field(..., description="Monthly payouts")
    
    # LWP statistics
    total_lwp_days: int = Field(..., description="Total LWP days in year")
    months_with_lwp: int = Field(..., description="Months with LWP")
    average_monthly_lwp: float = Field(..., description="Average monthly LWP days")


class PayoutApprovalDTO(BaseModel):
    """DTO for payout approval."""
    
    payout_ids: List[str] = Field(..., min_items=1, description="Payout IDs to approve")
    approved_by: str = Field(..., description="User ID who is approving")
    approval_notes: Optional[str] = Field(None, description="Approval notes")


class PayoutProcessingDTO(BaseModel):
    """DTO for payout processing."""
    
    payout_ids: List[str] = Field(..., min_items=1, description="Payout IDs to process")
    processed_by: str = Field(..., description="User ID who is processing")
    processing_notes: Optional[str] = Field(None, description="Processing notes")
    
    # Bank transfer details (optional)
    bank_reference: Optional[str] = Field(None, description="Bank reference number")
    transfer_date: Optional[str] = Field(None, description="Transfer date")


class PayslipDataDTO(BaseModel):
    """DTO for payslip data."""
    
    payout_id: str = Field(..., description="Payout ID")
    employee_id: str = Field(..., description="Employee ID")
    employee_name: str = Field(..., description="Employee name")
    company_name: str = Field(..., description="Company name")
    
    # Pay period
    pay_period: str = Field(..., description="Pay period (MM/YYYY)")
    pay_period_start: str = Field(..., description="Pay period start date")
    pay_period_end: str = Field(..., description="Pay period end date")
    payout_date: str = Field(..., description="Payout date")
    
    # Employee details
    employee_details: Dict[str, Any] = Field(default_factory=dict, description="Employee details")
    
    # Attendance
    attendance: Dict[str, Any] = Field(..., description="Attendance details")
    
    # Salary breakdown
    salary_breakdown: Dict[str, Any] = Field(..., description="Salary breakdown")
    
    # Tax information
    tax_info: Dict[str, Any] = Field(..., description="Tax information")
    
    # LWP impact
    lwp_impact: Dict[str, Any] = Field(..., description="LWP impact details")
    
    # Status
    status: str = Field(..., description="Payout status")
    notes: Optional[str] = Field(None, description="Notes")


class PayoutAnalyticsDTO(BaseModel):
    """DTO for payout analytics."""
    
    period: str = Field(..., description="Analysis period")
    
    # Financial metrics
    total_gross_amount: float = Field(..., description="Total gross amount")
    total_net_amount: float = Field(..., description="Total net amount")
    total_deductions: float = Field(..., description="Total deductions")
    average_gross_per_employee: float = Field(..., description="Average gross per employee")
    average_net_per_employee: float = Field(..., description="Average net per employee")
    
    # LWP metrics
    total_lwp_days: int = Field(..., description="Total LWP days")
    employees_with_lwp: int = Field(..., description="Employees with LWP")
    total_lwp_deduction: float = Field(..., description="Total LWP deduction")
    lwp_impact_percentage: float = Field(..., description="LWP impact percentage")
    
    # Department-wise breakdown
    department_breakdown: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, 
        description="Department-wise breakdown"
    )
    
    # Status distribution
    status_distribution: Dict[str, int] = Field(..., description="Status distribution")
    
    # Trends (if applicable)
    monthly_trends: Optional[List[Dict[str, Any]]] = Field(None, description="Monthly trends")


class PayoutComplianceDTO(BaseModel):
    """DTO for payout compliance metrics."""
    
    period: str = Field(..., description="Compliance period")
    
    # Statutory compliance
    epf_compliance: Dict[str, Any] = Field(..., description="EPF compliance details")
    esi_compliance: Dict[str, Any] = Field(..., description="ESI compliance details")
    tds_compliance: Dict[str, Any] = Field(..., description="TDS compliance details")
    pt_compliance: Dict[str, Any] = Field(..., description="Professional tax compliance")
    
    # Processing compliance
    on_time_processing: float = Field(..., description="On-time processing percentage")
    approval_delays: int = Field(..., description="Number of approval delays")
    processing_delays: int = Field(..., description="Number of processing delays")
    
    # Data quality
    missing_data_count: int = Field(..., description="Missing data count")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Compliance recommendations") 