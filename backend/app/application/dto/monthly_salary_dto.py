"""
Monthly Salary DTOs
Data Transfer Objects for monthly salary processing functionality
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator


class MonthlySalaryRequestDTO(BaseModel):
    """Request DTO for monthly salary operations."""
    
    employee_id: str = Field(..., description="Employee ID")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, le=2030, description="Year")
    tax_year: str = Field(..., description="Tax year (e.g., '2023-24')")
    
    @validator('tax_year')
    def validate_tax_year(cls, v):
        """Validate tax year format."""
        if not v or len(v) != 7 or v[4] != '-':
            raise ValueError("Tax year must be in format 'YYYY-YY'")
        return v


class MonthlySalaryFilterDTO(BaseModel):
    """Filter DTO for monthly salary queries."""
    
    month: Optional[int] = Field(None, ge=1, le=12, description="Month filter")
    year: Optional[int] = Field(None, ge=2020, le=2030, description="Year filter")
    tax_year: Optional[str] = Field(None, description="Tax year filter")
    status: Optional[str] = Field(None, description="Status filter")
    department: Optional[str] = Field(None, description="Department filter")
    skip: int = Field(0, ge=0, description="Skip records")
    limit: int = Field(50, ge=1, le=1000, description="Limit records")


class MonthlySalaryResponseDTO(BaseModel):
    """Response DTO for monthly salary data."""
    
    employee_id: str = Field(..., description="Employee ID")
    month: int = Field(..., description="Month")
    year: int = Field(..., description="Year")
    tax_year: str = Field(..., description="Tax year")
    
    # Employee info
    employee_name: Optional[str] = Field(None, description="Employee name")
    employee_email: Optional[str] = Field(None, description="Employee email")
    department: Optional[str] = Field(None, description="Department")
    designation: Optional[str] = Field(None, description="Designation")
    
    # Salary components
    basic_salary: float = Field(0.0, description="Basic salary")
    da: float = Field(0.0, description="Dearness allowance")
    hra: float = Field(0.0, description="HRA")
    special_allowance: float = Field(0.0, description="Special allowance")
    transport_allowance: float = Field(0.0, description="Transport allowance")
    medical_allowance: float = Field(0.0, description="Medical allowance")
    bonus: float = Field(0.0, description="Bonus")
    commission: float = Field(0.0, description="Commission")
    other_allowances: float = Field(0.0, description="Other allowances")
    
    # Deductions
    epf_employee: float = Field(0.0, description="EPF employee contribution")
    esi_employee: float = Field(0.0, description="ESI employee contribution")
    professional_tax: float = Field(0.0, description="Professional tax")
    tds: float = Field(0.0, description="TDS")
    advance_deduction: float = Field(0.0, description="Advance deduction")
    loan_deduction: float = Field(0.0, description="Loan deduction")
    other_deductions: float = Field(0.0, description="Other deductions")
    
    # Calculated totals
    gross_salary: float = Field(0.0, description="Gross salary")
    total_deductions: float = Field(0.0, description="Total deductions")
    net_salary: float = Field(0.0, description="Net salary")
    
    # Annual projections
    annual_gross_salary: float = Field(0.0, description="Annual gross salary")
    annual_tax_liability: float = Field(0.0, description="Annual tax liability")
    
    # Tax details
    tax_regime: str = Field("new", description="Tax regime")
    tax_exemptions: float = Field(0.0, description="Tax exemptions")
    standard_deduction: float = Field(0.0, description="Standard deduction")
    
    # Working days
    total_days_in_month: int = Field(30, description="Total days in month")
    working_days_in_period: int = Field(22, description="Working days")
    lwp_days: int = Field(0, description="LWP days")
    effective_working_days: int = Field(22, description="Effective working days")
    
    # Processing details
    status: str = Field("not_computed", description="Processing status")
    computation_date: Optional[datetime] = Field(None, description="Computation date")
    notes: Optional[str] = Field(None, description="Notes")
    remarks: Optional[str] = Field(None, description="Remarks")
    
    # Payment tracking
    salary_payment_date: Optional[datetime] = Field(None, description="Salary payment date")
    tds_payment_date: Optional[datetime] = Field(None, description="TDS payment date")
    salary_payment_reference: Optional[str] = Field(None, description="Salary payment reference")
    tds_payment_reference: Optional[str] = Field(None, description="TDS payment reference")
    salary_paid_by: Optional[str] = Field(None, description="Salary paid by")
    tds_paid_by: Optional[str] = Field(None, description="TDS paid by")
    
    # Payment status helpers
    is_salary_paid: bool = Field(False, description="Whether salary is paid")
    is_tds_paid: bool = Field(False, description="Whether TDS is paid")
    is_fully_paid: bool = Field(False, description="Whether both salary and TDS are paid")
    
    # Audit fields
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")
    created_by: Optional[str] = Field(None, description="Created by")
    updated_by: Optional[str] = Field(None, description="Updated by")


class MonthlySalaryListResponseDTO(BaseModel):
    """Response DTO for list of monthly salaries."""
    
    items: List[MonthlySalaryResponseDTO] = Field(default_factory=list, description="Monthly salary records")
    total: int = Field(0, description="Total count")
    skip: int = Field(0, description="Skip count")
    limit: int = Field(50, description="Limit count")
    has_more: bool = Field(False, description="Has more records")


class MonthlySalaryComputeRequestDTO(BaseModel):
    """Request DTO for computing monthly salary."""
    
    employee_id: str = Field(..., description="Employee ID")
    month: int = Field(..., ge=1, le=12, description="Month")
    year: int = Field(..., ge=2020, le=2030, description="Year")
    tax_year: str = Field(..., description="Tax year")
    force_recompute: bool = Field(False, description="Force recomputation")
    computed_by: Optional[str] = Field(None, description="Computed by")


class MonthlySalaryBulkComputeRequestDTO(BaseModel):
    """Request DTO for bulk computing monthly salaries."""
    
    month: int = Field(..., ge=1, le=12, description="Month")
    year: int = Field(..., ge=2020, le=2030, description="Year")
    tax_year: str = Field(..., description="Tax year")
    employee_ids: Optional[List[str]] = Field(None, description="Specific employee IDs (if None, process all)")
    force_recompute: bool = Field(False, description="Force recomputation")
    computed_by: Optional[str] = Field(None, description="Computed by")


class MonthlySalaryBulkComputeResponseDTO(BaseModel):
    """Response DTO for bulk compute operation."""
    
    total_requested: int = Field(0, description="Total employees requested")
    successful: int = Field(0, description="Successfully computed")
    failed: int = Field(0, description="Failed computations")
    skipped: int = Field(0, description="Skipped (already computed)")
    errors: List[dict] = Field(default_factory=list, description="Error details")
    computation_summary: dict = Field(default_factory=dict, description="Summary statistics")


class MonthlySalaryStatusUpdateRequestDTO(BaseModel):
    """Request DTO for updating monthly salary status."""
    
    employee_id: str = Field(..., description="Employee ID")
    month: int = Field(..., ge=1, le=12, description="Month")
    year: int = Field(..., ge=2020, le=2030, description="Year")
    status: str = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Status change notes")
    updated_by: Optional[str] = Field(None, description="Updated by")


class MonthlySalaryPaymentRequestDTO(BaseModel):
    """Request DTO for marking salary payment."""
    
    employee_id: str = Field(..., description="Employee ID")
    month: int = Field(..., ge=1, le=12, description="Month")
    year: int = Field(..., ge=2020, le=2030, description="Year")
    payment_type: str = Field(..., description="Payment type: 'salary', 'tds', or 'both'")
    payment_reference: Optional[str] = Field(None, description="Payment reference number")
    payment_notes: Optional[str] = Field(None, description="Payment notes")
    paid_by: Optional[str] = Field(None, description="Paid by")


class MonthlySalarySummaryDTO(BaseModel):
    """Summary DTO for monthly salary overview."""
    
    month: int = Field(..., description="Month")
    year: int = Field(..., description="Year")
    tax_year: str = Field(..., description="Tax year")
    
    # Summary statistics
    total_employees: int = Field(0, description="Total employees")
    computed_count: int = Field(0, description="Computed salaries")
    pending_count: int = Field(0, description="Pending computations")
    approved_count: int = Field(0, description="Approved salaries")
    salary_paid_count: int = Field(0, description="Salary paid (but TDS pending)")
    tds_paid_count: int = Field(0, description="TDS paid (but salary pending)")
    paid_count: int = Field(0, description="Fully paid salaries")
    
    # Financial summary
    total_gross_payroll: float = Field(0.0, description="Total gross payroll")
    total_net_payroll: float = Field(0.0, description="Total net payroll")
    total_deductions: float = Field(0.0, description="Total deductions")
    total_tds: float = Field(0.0, description="Total TDS")
    
    # Processing summary
    computation_completion_rate: float = Field(0.0, description="Completion rate percentage")
    last_computed_at: Optional[datetime] = Field(None, description="Last computation time")
    next_processing_date: Optional[datetime] = Field(None, description="Next processing date") 