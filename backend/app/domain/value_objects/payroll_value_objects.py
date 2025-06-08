"""
Payroll Domain Value Objects
Immutable value objects that represent payroll domain concepts
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Optional, List
from decimal import Decimal
from enum import Enum

from app.domain.value_objects.bank_details import BankDetails


class PaymentMethod(str, Enum):
    """Payment method enumeration"""
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHEQUE = "cheque"
    UPI = "upi"
    WALLET = "wallet"


class DeductionType(str, Enum):
    """Deduction type enumeration"""
    STATUTORY = "statutory"  # EPF, ESI, PT, TDS
    VOLUNTARY = "voluntary"  # Advance, Loan
    RECOVERY = "recovery"    # Notice period, other recoveries


class EarningsType(str, Enum):
    """Earnings type enumeration"""
    BASIC = "basic"
    ALLOWANCE = "allowance"
    BONUS = "bonus"
    INCENTIVE = "incentive"
    REIMBURSEMENT = "reimbursement"
    OVERTIME = "overtime"


@dataclass(frozen=True)
class Money:
    """Value object for monetary amounts"""
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency is required")
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money values"""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two money values"""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Result cannot be negative")
        return Money(result, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        """Multiply money by a factor"""
        return Money(self.amount * Decimal(str(factor)), self.currency)
    
    def to_float(self) -> float:
        """Convert to float for compatibility"""
        return float(self.amount)


@dataclass(frozen=True)
class SalaryComponents:
    """Value object for salary components"""
    basic: Money
    dearness_allowance: Money
    hra: Money
    special_allowance: Money
    bonus: Money
    commission: Money = Money(Decimal('0'))
    transport_allowance: Money = Money(Decimal('0'))
    medical_allowance: Money = Money(Decimal('0'))
    other_allowances: Money = Money(Decimal('0'))
    
    def total_earnings(self) -> Money:
        """Calculate total earnings"""
        return (self.basic
                .add(self.dearness_allowance)
                .add(self.hra)
                .add(self.special_allowance)
                .add(self.bonus)
                .add(self.commission)
                .add(self.transport_allowance)
                .add(self.medical_allowance)
                .add(self.other_allowances))
    
    def basic_plus_da(self) -> Money:
        """Calculate basic plus dearness allowance (for PF calculation)"""
        return self.basic.add(self.dearness_allowance)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for compatibility"""
        return {
            "basic": self.basic.to_float(),
            "dearness_allowance": self.dearness_allowance.to_float(),
            "hra": self.hra.to_float(),
            "special_allowance": self.special_allowance.to_float(),
            "bonus": self.bonus.to_float(),
            "commission": self.commission.to_float(),
            "transport_allowance": self.transport_allowance.to_float(),
            "medical_allowance": self.medical_allowance.to_float(),
            "other_allowances": self.other_allowances.to_float(),
        }


@dataclass(frozen=True)
class DeductionComponents:
    """Value object for deduction components"""
    epf_employee: Money
    esi_employee: Money
    professional_tax: Money
    tds: Money
    advance_deduction: Money = Money(Decimal('0'))
    loan_deduction: Money = Money(Decimal('0'))
    notice_period_recovery: Money = Money(Decimal('0'))
    other_deductions: Money = Money(Decimal('0'))
    
    def total_deductions(self) -> Money:
        """Calculate total deductions"""
        return (self.epf_employee
                .add(self.esi_employee)
                .add(self.professional_tax)
                .add(self.tds)
                .add(self.advance_deduction)
                .add(self.loan_deduction)
                .add(self.notice_period_recovery)
                .add(self.other_deductions))
    
    def statutory_deductions(self) -> Money:
        """Calculate statutory deductions only"""
        return (self.epf_employee
                .add(self.esi_employee)
                .add(self.professional_tax)
                .add(self.tds))
    
    def voluntary_deductions(self) -> Money:
        """Calculate voluntary deductions only"""
        return (self.advance_deduction
                .add(self.loan_deduction)
                .add(self.other_deductions))
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for compatibility"""
        return {
            "epf_employee": self.epf_employee.to_float(),
            "esi_employee": self.esi_employee.to_float(),
            "professional_tax": self.professional_tax.to_float(),
            "tds": self.tds.to_float(),
            "advance_deduction": self.advance_deduction.to_float(),
            "loan_deduction": self.loan_deduction.to_float(),
            "notice_period_recovery": self.notice_period_recovery.to_float(),
            "other_deductions": self.other_deductions.to_float(),
        }


@dataclass(frozen=True)
class EmployerContributions:
    """Value object for employer contributions"""
    epf_employer: Money
    esi_employer: Money
    gratuity: Money = Money(Decimal('0'))
    bonus_provision: Money = Money(Decimal('0'))
    leave_encashment_provision: Money = Money(Decimal('0'))
    
    def total_contributions(self) -> Money:
        """Calculate total employer contributions"""
        return (self.epf_employer
                .add(self.esi_employer)
                .add(self.gratuity)
                .add(self.bonus_provision)
                .add(self.leave_encashment_provision))
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for compatibility"""
        return {
            "epf_employer": self.epf_employer.to_float(),
            "esi_employer": self.esi_employer.to_float(),
            "gratuity": self.gratuity.to_float(),
            "bonus_provision": self.bonus_provision.to_float(),
            "leave_encashment_provision": self.leave_encashment_provision.to_float(),
        }


@dataclass(frozen=True)
class PayPeriod:
    """Value object for pay period"""
    start_date: date
    end_date: date
    month: int
    year: int
    
    def __post_init__(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
        if not (1 <= self.month <= 12):
            raise ValueError("Month must be between 1 and 12")
        if self.year < 1900:
            raise ValueError("Year must be >= 1900")
    
    def total_days(self) -> int:
        """Calculate total days in pay period"""
        return (self.end_date - self.start_date).days + 1
    
    def is_partial_month(self) -> bool:
        """Check if this is a partial month"""
        import calendar
        last_day_of_month = calendar.monthrange(self.year, self.month)[1]
        expected_start = date(self.year, self.month, 1)
        expected_end = date(self.year, self.month, last_day_of_month)
        
        return self.start_date != expected_start or self.end_date != expected_end
    
    def to_string(self) -> str:
        """Convert to string representation"""
        return f"{self.month:02d}/{self.year}"


@dataclass(frozen=True)
class AttendanceInfo:
    """Value object for attendance information"""
    total_days_in_month: int
    working_days_in_period: int
    lwp_days: int
    overtime_hours: float = 0.0
    
    def __post_init__(self):
        if self.total_days_in_month <= 0:
            raise ValueError("Total days must be positive")
        if self.working_days_in_period < 0:
            raise ValueError("Working days cannot be negative")
        if self.lwp_days < 0:
            raise ValueError("LWP days cannot be negative")
        if self.working_days_in_period > self.total_days_in_month:
            raise ValueError("Working days cannot exceed total days")
        if self.overtime_hours < 0:
            raise ValueError("Overtime hours cannot be negative")
    
    def effective_working_days(self) -> int:
        """Calculate effective working days (excluding LWP)"""
        return max(0, self.working_days_in_period - self.lwp_days)
    
    def working_ratio(self) -> float:
        """Calculate working days ratio for salary calculation"""
        return self.working_days_in_period / self.total_days_in_month
    
    def effective_working_ratio(self) -> float:
        """Calculate effective working days ratio (excluding LWP)"""
        return self.effective_working_days() / self.total_days_in_month
    
    def lwp_ratio(self) -> float:
        """Calculate LWP ratio"""
        return self.lwp_days / self.total_days_in_month if self.total_days_in_month > 0 else 0


@dataclass(frozen=True)
class TaxInfo:
    """Value object for tax information"""
    regime: str
    annual_tax_liability: Money
    monthly_tds: Money
    exemptions_claimed: Money = Money(Decimal('0'))
    standard_deduction: Money = Money(Decimal('0'))
    section_80c_claimed: Money = Money(Decimal('0'))
    
    def __post_init__(self):
        if self.regime not in ["old", "new"]:
            raise ValueError("Tax regime must be 'old' or 'new'")
    
    def total_deductions_claimed(self) -> Money:
        """Calculate total tax deductions claimed"""
        return (self.exemptions_claimed
                .add(self.standard_deduction)
                .add(self.section_80c_claimed))
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for compatibility"""
        return {
            "regime": self.regime,
            "annual_tax_liability": self.annual_tax_liability.to_float(),
            "monthly_tds": self.monthly_tds.to_float(),
            "exemptions_claimed": self.exemptions_claimed.to_float(),
            "standard_deduction": self.standard_deduction.to_float(),
            "section_80c_claimed": self.section_80c_claimed.to_float(),
        }


# BankDetails is now imported from app.domain.value_objects.bank_details


@dataclass(frozen=True)
class PayoutSummary:
    """Value object for payout summary"""
    gross_earnings: Money
    total_deductions: Money
    net_pay: Money
    employer_contributions: Money
    
    def cost_to_company(self) -> Money:
        """Calculate total cost to company"""
        return self.gross_earnings.add(self.employer_contributions)
    
    def take_home_percentage(self) -> float:
        """Calculate take home percentage"""
        if self.gross_earnings.amount == 0:
            return 0.0
        return float(self.net_pay.amount / self.gross_earnings.amount * 100)
    
    def deduction_percentage(self) -> float:
        """Calculate deduction percentage"""
        if self.gross_earnings.amount == 0:
            return 0.0
        return float(self.total_deductions.amount / self.gross_earnings.amount * 100)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for compatibility"""
        return {
            "gross_earnings": self.gross_earnings.to_float(),
            "total_deductions": self.total_deductions.to_float(),
            "net_pay": self.net_pay.to_float(),
            "employer_contributions": self.employer_contributions.to_float(),
            "cost_to_company": self.cost_to_company().to_float(),
            "take_home_percentage": self.take_home_percentage(),
            "deduction_percentage": self.deduction_percentage(),
        }


@dataclass(frozen=True)
class PayslipMetadata:
    """Value object for payslip metadata"""
    payslip_id: str
    payout_id: str
    employee_id: str
    format: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: Optional[datetime] = None
    email_sent: bool = False
    email_sent_at: Optional[datetime] = None
    download_count: int = 0
    
    def __post_init__(self):
        if not self.payslip_id or not self.payslip_id.strip():
            raise ValueError("Payslip ID is required")
        if not self.payout_id or not self.payout_id.strip():
            raise ValueError("Payout ID is required")
        if not self.employee_id or not self.employee_id.strip():
            raise ValueError("Employee ID is required")
        if self.format not in ["PDF", "HTML", "JSON"]:
            raise ValueError("Format must be PDF, HTML, or JSON")
        if self.download_count < 0:
            raise ValueError("Download count cannot be negative") 