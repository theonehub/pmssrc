from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.lwp_details import LWPDetails

@dataclass
class MonthlySalary:
    employee_id: EmployeeId
    month: int
    year: int
    salary: SalaryIncome
    perquisites: Perquisites
    deductions: TaxDeductions
    retirement: RetirementBenefits
    lwp: LWPDetails
    tax_year: TaxYear
    tax_regime: TaxRegime
    tax_amount: Money
    net_salary: Money
    
    # Additional salary components for frontend compatibility
    transport_allowance: Money = field(default_factory=lambda: Money.zero())
    medical_allowance: Money = field(default_factory=lambda: Money.zero())
    other_allowances: Money = field(default_factory=lambda: Money.zero())
    
    # Deduction components
    epf_employee: Money = field(default_factory=lambda: Money.zero())
    esi_employee: Money = field(default_factory=lambda: Money.zero())
    professional_tax: Money = field(default_factory=lambda: Money.zero())
    advance_deduction: Money = field(default_factory=lambda: Money.zero())
    loan_deduction: Money = field(default_factory=lambda: Money.zero())
    other_deductions: Money = field(default_factory=lambda: Money.zero())
    
    # Loan details for transparency
    loan_principal_amount: Money = field(default_factory=lambda: Money.zero())
    loan_interest_amount: Money = field(default_factory=lambda: Money.zero())
    loan_outstanding_amount: Money = field(default_factory=lambda: Money.zero())
    loan_type: Optional[str] = None
    
    # Calculated totals
    gross_salary: Money = field(default_factory=lambda: Money.zero())
    total_deductions: Money = field(default_factory=lambda: Money.zero())
    
    # Annual projections
    annual_gross_salary: Money = field(default_factory=lambda: Money.zero())
    annual_tax_liability: Money = field(default_factory=lambda: Money.zero())
    
    # Tax details
    tax_exemptions: Money = field(default_factory=lambda: Money.zero())
    standard_deduction: Money = field(default_factory=lambda: Money.zero())
    
    # Working days and LWP
    total_days_in_month: int = 30
    working_days_in_period: int = 30
    lwp_days: int = 0
    effective_working_days: int = 30
    
    # Status management
    status: str = "not_computed"  # not_computed, computed, approved, salary_paid, tds_paid, paid, rejected
    
    # Payment tracking
    salary_paid: bool = False
    tds_paid: bool = False
    payment_reference: Optional[str] = None
    payment_notes: Optional[str] = None
    
    # Metadata
    computation_date: Optional[datetime] = None
    notes: Optional[str] = None
    remarks: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    def __post_init__(self):
        if self.salary is None:
            raise ValueError("Salary cannot be None")
        
        # Calculate effective working days
        self.effective_working_days = self.working_days_in_period - self.lwp_days
        
        # Update payment status based on individual flags
        if self.salary_paid and self.tds_paid:
            self.status = "paid"
        elif self.salary_paid:
            self.status = "salary_paid"
        elif self.tds_paid:
            self.status = "tds_paid"
        
    def compute_net_pay(self) -> Money:
        """
        Compute the net pay for the month.
        """
        # Calculate gross salary from salary components
        self.gross_salary = self.salary.calculate_gross_salary()
        
        # Add additional allowances
        self.gross_salary = self.gross_salary.add(self.transport_allowance)
        self.gross_salary = self.gross_salary.add(self.medical_allowance)
        self.gross_salary = self.gross_salary.add(self.other_allowances)
        
        # Calculate total deductions
        self.total_deductions = (
            self.epf_employee
            .add(self.esi_employee)
            .add(self.professional_tax)
            .add(self.advance_deduction)
            .add(self.loan_deduction)
            .add(self.other_deductions)
            .add(self.tax_amount)
        )
        
        # Calculate net salary
        self.net_salary = self.gross_salary.subtract(self.total_deductions)
        
        # Update computation timestamp
        self.computation_date = datetime.utcnow()
        self.status = "computed"
        
        return self.net_salary
    
    def approve(self, approved_by: str, notes: Optional[str] = None) -> None:
        """Approve the monthly salary."""
        self.status = "approved"
        self.updated_by = approved_by
        self.updated_at = datetime.utcnow()
        if notes:
            self.notes = notes
    
    def reject(self, rejected_by: str, notes: Optional[str] = None) -> None:
        """Reject the monthly salary."""
        self.status = "rejected"
        self.updated_by = rejected_by
        self.updated_at = datetime.utcnow()
        if notes:
            self.notes = notes
    
    def mark_salary_paid(self, paid_by: str, payment_reference: Optional[str] = None, payment_notes: Optional[str] = None) -> None:
        """Mark salary as paid."""
        self.salary_paid = True
        self.payment_reference = payment_reference
        self.payment_notes = payment_notes
        self.updated_by = paid_by
        self.updated_at = datetime.utcnow()
        
        # Update status based on payment state
        if self.tds_paid:
            self.status = "paid"
        else:
            self.status = "salary_paid"
    
    def mark_tds_paid(self, paid_by: str, payment_reference: Optional[str] = None, payment_notes: Optional[str] = None) -> None:
        """Mark TDS as paid."""
        self.tds_paid = True
        self.payment_reference = payment_reference
        self.payment_notes = payment_notes
        self.updated_by = paid_by
        self.updated_at = datetime.utcnow()
        
        # Update status based on payment state
        if self.salary_paid:
            self.status = "paid"
        else:
            self.status = "tds_paid"
    
    def mark_both_paid(self, paid_by: str, payment_reference: Optional[str] = None, payment_notes: Optional[str] = None) -> None:
        """Mark both salary and TDS as paid."""
        self.salary_paid = True
        self.tds_paid = True
        self.payment_reference = payment_reference
        self.payment_notes = payment_notes
        self.status = "paid"
        self.updated_by = paid_by
        self.updated_at = datetime.utcnow()
    
    def recompute(self, recomputed_by: str) -> None:
        """Recompute the monthly salary."""
        self.compute_net_pay()
        self.updated_by = recomputed_by
        self.updated_at = datetime.utcnow()
        