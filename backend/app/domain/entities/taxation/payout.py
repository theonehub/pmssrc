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
    bonus: float = Field(0.0, ge=0)
    commission: float = Field(0.0, ge=0)
    transport_allowance: float = Field(0.0, ge=0)
    medical_allowance: float = Field(0.0, ge=0)
    other_allowances: float = Field(0.0, ge=0)
    
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
            "basic_salary", "da", "hra", "special_allowance", "bonus", 
            "commission", "transport_allowance", "medical_allowance", 
            "other_allowances", "reimbursements"
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
    """Enhanced monthly payout projection with LWP integration."""
    
    # LWP-specific fields
    lwp_factor: float = Field(1.0, ge=0.0, le=1.0, description="LWP adjustment factor (0.0 to 1.0)")
    lwp_deduction_amount: float = Field(0.0, ge=0, description="Amount deducted due to LWP")
    base_gross_without_lwp: float = Field(0.0, ge=0, description="Base gross salary without LWP adjustment")
    
    # Enhanced metadata
    organization_id: Optional[str] = None
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, le=2050, description="Year")
    calculation_date: Optional[datetime] = None
    
    # Taxation integration
    tax_calculation_id: Optional[str] = None
    is_tax_calculated: bool = False
    
    @classmethod
    def create_from_monthly_payroll(
        cls,
        employee_id: str,
        monthly_payroll: "MonthlyPayroll",
        organization_id: str,
        tax_regime: str = "new",
        annual_tax_liability: float = 0.0,
        calculation_date: Optional[datetime] = None
    ) -> "PayoutMonthlyProjection":
        """
        Create PayoutMonthlyProjection from MonthlyPayroll entity.
        
        Args:
            employee_id: Employee ID
            monthly_payroll: MonthlyPayroll entity with LWP calculations
            organization_id: Organization ID
            tax_regime: Tax regime ("old" or "new")
            annual_tax_liability: Annual tax liability for TDS calculation
            calculation_date: When the calculation was performed
            
        Returns:
            PayoutMonthlyProjection instance
        """
        from app.domain.value_objects.tax_regime import TaxRegime
        
        # Get regime for calculations
        regime = TaxRegime.old_regime() if tax_regime == "old" else TaxRegime.new_regime()
        
        # Calculate base amounts
        base_monthly_gross = monthly_payroll.calculate_monthly_gross_without_lwp()
        adjusted_monthly_gross = monthly_payroll.calculate_monthly_gross_with_lwp()
        lwp_deduction = monthly_payroll.calculate_lwp_deduction()
        
        # Get salary components (proportionally adjusted for LWP)
        lwp_factor = float(monthly_payroll.lwp_details.get_lwp_factor())
        base_salary_income = monthly_payroll.base_salary_income
        
        # Calculate monthly components with LWP adjustment
        monthly_basic = float(base_salary_income.basic_salary.divide(12).multiply(lwp_factor).amount)
        monthly_da = float(base_salary_income.dearness_allowance.divide(12).multiply(lwp_factor).amount)
        monthly_hra = float(base_salary_income.hra_received.divide(12).multiply(lwp_factor).amount)
        monthly_special = float(base_salary_income.special_allowance.divide(12).multiply(lwp_factor).amount)
        monthly_transport = float(base_salary_income.conveyance_allowance.divide(12).multiply(lwp_factor).amount)
        monthly_medical = float(base_salary_income.medical_allowance.divide(12).multiply(lwp_factor).amount)
        monthly_bonus = float(base_salary_income.bonus.divide(12).multiply(lwp_factor).amount)
        monthly_commission = float(base_salary_income.commission.divide(12).multiply(lwp_factor).amount)
        monthly_other = float(base_salary_income.other_allowances.divide(12).multiply(lwp_factor).amount)
        
        # Calculate monthly TDS
        monthly_tds = annual_tax_liability / 12 if annual_tax_liability > 0 else 0.0
        
        # Calculate statutory deductions (EPF, ESI, Professional Tax)
        monthly_epf_employee = cls._calculate_monthly_epf_employee(adjusted_monthly_gross.to_float())
        monthly_esi_employee = cls._calculate_monthly_esi_employee(adjusted_monthly_gross.to_float())
        monthly_professional_tax = cls._calculate_monthly_professional_tax(adjusted_monthly_gross.to_float())
        
        # Calculate period dates
        lwp_details = monthly_payroll.lwp_details
        pay_period_start = date(lwp_details.year, lwp_details.month, 1)
        
        # Calculate last day of month
        import calendar
        last_day = calendar.monthrange(lwp_details.year, lwp_details.month)[1]
        pay_period_end = date(lwp_details.year, lwp_details.month, last_day)
        payout_date = date(lwp_details.year, lwp_details.month, min(30, last_day))
        
        return cls(
            employee_id=employee_id,
            organization_id=organization_id,
            month=lwp_details.month,
            year=lwp_details.year,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            payout_date=payout_date,
            calculation_date=calculation_date or datetime.utcnow(),
            
            # Salary components (LWP adjusted)
            basic_salary=monthly_basic,
            da=monthly_da,
            hra=monthly_hra,
            special_allowance=monthly_special,
            transport_allowance=monthly_transport,
            medical_allowance=monthly_medical,
            bonus=monthly_bonus,
            commission=monthly_commission,
            other_allowances=monthly_other,
            
            # Deductions
            epf_employee=monthly_epf_employee,
            esi_employee=monthly_esi_employee,
            professional_tax=monthly_professional_tax,
            tds=monthly_tds,
            advance_deduction=0.0,  # Can be set separately
            loan_deduction=0.0,     # Can be set separately
            other_deductions=0.0,   # Can be set separately
            
            # LWP-specific fields
            lwp_factor=lwp_factor,
            lwp_deduction_amount=float(lwp_deduction.amount),
            base_gross_without_lwp=float(base_monthly_gross.amount),
            
            # Working days
            total_days_in_month=lwp_details.total_working_days,
            working_days_in_period=lwp_details.total_working_days,
            lwp_days=lwp_details.lwp_days,
            effective_working_days=lwp_details.get_paid_days(),
            
            # Annual projections
            annual_gross_salary=float(base_salary_income.calculate_gross_salary().amount),
            annual_tax_liability=annual_tax_liability,
            monthly_tds=monthly_tds,
            
            # Tax details
            tax_regime=tax_regime,
            tax_exemptions=float(base_salary_income.calculate_total_exemptions(regime).amount),
            standard_deduction=float(regime.get_standard_deduction().amount),
            
            # Status
            status=PayoutStatus.PENDING,
            notes=f"Monthly payout with LWP adjustment (factor: {lwp_factor:.3f})",
            remarks=f"LWP days: {lwp_details.lwp_days}, Effective working days: {lwp_details.get_paid_days()}"
        )
    
    @staticmethod
    def _calculate_monthly_epf_employee(monthly_gross: float) -> float:
        """Calculate monthly EPF employee contribution (12% of basic + DA, capped at ₹1,800)."""
        # Approximate basic + DA as 50% of gross
        epf_eligible_salary = monthly_gross * 0.5
        epf_contribution = epf_eligible_salary * 0.12
        return min(epf_contribution, 1800.0)  # EPF cap is ₹1,800 per month
    
    @staticmethod
    def _calculate_monthly_esi_employee(monthly_gross: float) -> float:
        """Calculate monthly ESI employee contribution (0.75% of gross, applicable if gross ≤ ₹21,000)."""
        if monthly_gross > 21000:
            return 0.0
        return monthly_gross * 0.0075
    
    @staticmethod
    def _calculate_monthly_professional_tax(monthly_gross: float) -> float:
        """Calculate monthly professional tax (varies by state, using standard rates)."""
        if monthly_gross <= 15000:
            return 0.0
        elif monthly_gross <= 20000:
            return 150.0
        else:
            return 200.0
    
    def get_lwp_impact_summary(self) -> Dict[str, Any]:
        """
        Get LWP impact summary for this monthly payout.
        
        Returns:
            Dict containing LWP impact details
        """
        return {
            "lwp_days": self.lwp_days,
            "effective_working_days": self.effective_working_days,
            "lwp_factor": self.lwp_factor,
            "base_gross_without_lwp": self.base_gross_without_lwp,
            "lwp_deduction_amount": self.lwp_deduction_amount,
            "adjusted_gross_salary": self.gross_salary,
            "salary_reduction_percentage": (self.lwp_deduction_amount / self.base_gross_without_lwp * 100) if self.base_gross_without_lwp > 0 else 0,
            "net_salary_after_lwp": self.net_salary
        }
    
    def get_payslip_data(self, employee_name: str, company_name: str, 
                        employee_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get formatted payslip data for PDF generation or display.
        
        Args:
            employee_name: Employee name
            company_name: Company name
            employee_details: Optional employee details (department, designation, etc.)
            
        Returns:
            Dict containing formatted payslip data
        """
        earnings = {
            "Basic Salary": self.basic_salary,
            "Dearness Allowance": self.da,
            "HRA": self.hra,
            "Special Allowance": self.special_allowance,
            "Transport Allowance": self.transport_allowance,
            "Medical Allowance": self.medical_allowance,
            "Bonus": self.bonus,
            "Commission": self.commission,
            "Other Allowances": self.other_allowances,
            "Reimbursements": self.reimbursements
        }
        
        deductions = {
            "EPF (Employee)": self.epf_employee,
            "ESI (Employee)": self.esi_employee,
            "Professional Tax": self.professional_tax,
            "TDS": self.tds,
            "Advance Deduction": self.advance_deduction,
            "Loan Deduction": self.loan_deduction,
            "Other Deductions": self.other_deductions
        }
        
        # Filter out zero amounts
        earnings = {k: v for k, v in earnings.items() if v > 0}
        deductions = {k: v for k, v in deductions.items() if v > 0}
        
        return {
            "employee_id": self.employee_id,
            "employee_name": employee_name,
            "company_name": company_name,
            "pay_period": f"{self.month:02d}/{self.year}",
            "pay_period_start": self.pay_period_start.strftime("%d-%m-%Y"),
            "pay_period_end": self.pay_period_end.strftime("%d-%m-%Y"),
            "payout_date": self.payout_date.strftime("%d-%m-%Y"),
            "employee_details": employee_details or {},
            
            # Attendance
            "total_days_in_month": self.total_days_in_month,
            "working_days": self.working_days_in_period,
            "lwp_days": self.lwp_days,
            "effective_working_days": self.effective_working_days,
            
            # Earnings and deductions
            "earnings": earnings,
            "total_earnings": self.gross_salary,
            "deductions": deductions,
            "total_deductions": self.total_deductions,
            "net_pay": self.net_salary,
            
            # Tax information
            "tax_regime": self.tax_regime,
            "annual_gross_salary": self.annual_gross_salary,
            "annual_tax_liability": self.annual_tax_liability,
            "ytd_tax_deducted": self.tds * self.month,  # Approximate YTD
            
            # LWP impact
            "lwp_impact": self.get_lwp_impact_summary(),
            
            # Status
            "status": self.status.value,
            "notes": self.notes,
            "remarks": self.remarks
        }

class PayoutCreate(PayoutBase):
    pass

class PayoutUpdate(BaseModel):
    basic_salary: Optional[float] = Field(None, ge=0)
    da: Optional[float] = Field(None, ge=0)
    hra: Optional[float] = Field(None, ge=0)
    special_allowance: Optional[float] = Field(None, ge=0)
    bonus: Optional[float] = Field(None, ge=0)
    commission: Optional[float] = Field(None, ge=0)
    transport_allowance: Optional[float] = Field(None, ge=0)
    medical_allowance: Optional[float] = Field(None, ge=0)
    other_allowances: Optional[float] = Field(None, ge=0)
    
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