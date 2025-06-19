"""
Monthly Salary Domain Entity
Represents computed monthly salary for an employee in a specific month and year
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money


@dataclass
class ProcessingStatus:
    """Value object for monthly salary processing status."""
    
    NOT_COMPUTED = "not_computed"
    PENDING = "pending"
    COMPUTED = "computed"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"
    
    def __init__(self, status: str):
        """Initialize processing status."""
        valid_statuses = [
            self.NOT_COMPUTED, self.PENDING, self.COMPUTED, 
            self.APPROVED, self.PAID, self.REJECTED
        ]
        if status not in valid_statuses:
            raise ValueError(f"Invalid processing status: {status}")
        self.value = status
    
    def __str__(self) -> str:
        return self.value
    
    def is_computed(self) -> bool:
        """Check if salary has been computed."""
        return self.value != self.NOT_COMPUTED
    
    def is_final(self) -> bool:
        """Check if salary processing is final (approved or paid)."""
        return self.value in [self.APPROVED, self.PAID]


@dataclass
class MonthlySalary:
    """
    Monthly Salary domain entity.
    
    Represents the computed monthly salary for an employee in a specific month and year.
    Follows domain-driven design principles with rich behavior and business rules.
    """
    
    # Core identification
    employee_id: EmployeeId
    month: int
    year: int
    tax_year: str
    
    # Salary components (using Money value objects)
    basic_salary: Money
    da: Money  # Dearness Allowance
    hra: Money  # House Rent Allowance
    special_allowance: Money
    transport_allowance: Money
    medical_allowance: Money
    bonus: Money
    commission: Money
    other_allowances: Money
    
    # Deductions
    epf_employee: Money  # Employee Provident Fund
    esi_employee: Money  # Employee State Insurance
    professional_tax: Money
    tds: Money  # Tax Deducted at Source
    advance_deduction: Money
    loan_deduction: Money
    other_deductions: Money
    
    # Calculated totals
    gross_salary: Money
    total_deductions: Money
    net_salary: Money
    
    # Annual projections
    annual_gross_salary: Money
    annual_tax_liability: Money
    
    # Tax details
    tax_regime: str
    tax_exemptions: Money
    standard_deduction: Money
    
    # Working days and attendance
    total_days_in_month: int
    working_days_in_period: int
    lwp_days: int
    effective_working_days: int
    
    # Processing metadata
    status: ProcessingStatus
    computation_date: Optional[datetime]
    notes: Optional[str]
    remarks: Optional[str]
    
    # Audit fields
    organization_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    @classmethod
    def create_new(
        cls,
        employee_id: EmployeeId,
        month: int,
        year: int,
        tax_year: str,
        organization_id: str,
        created_by: Optional[str] = None
    ) -> 'MonthlySalary':
        """
        Create a new monthly salary record with default values.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            tax_year: Tax year (e.g., "2024-25")
            organization_id: Organization ID
            created_by: User who created the record
            
        Returns:
            MonthlySalary: New monthly salary instance
        """
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise ValueError("Year must be between 2020 and 2030")
        
        now = datetime.utcnow()
        
        return cls(
            employee_id=employee_id,
            month=month,
            year=year,
            tax_year=tax_year,
            
            # Initialize all salary components to zero
            basic_salary=Money.zero(),
            da=Money.zero(),
            hra=Money.zero(),
            special_allowance=Money.zero(),
            transport_allowance=Money.zero(),
            medical_allowance=Money.zero(),
            bonus=Money.zero(),
            commission=Money.zero(),
            other_allowances=Money.zero(),
            
            # Initialize all deductions to zero
            epf_employee=Money.zero(),
            esi_employee=Money.zero(),
            professional_tax=Money.zero(),
            tds=Money.zero(),
            advance_deduction=Money.zero(),
            loan_deduction=Money.zero(),
            other_deductions=Money.zero(),
            
            # Initialize calculated totals to zero
            gross_salary=Money.zero(),
            total_deductions=Money.zero(),
            net_salary=Money.zero(),
            
            # Initialize annual projections to zero
            annual_gross_salary=Money.zero(),
            annual_tax_liability=Money.zero(),
            
            # Default tax details
            tax_regime="new",
            tax_exemptions=Money.zero(),
            standard_deduction=Money.zero(),
            
            # Default working days
            total_days_in_month=30,
            working_days_in_period=22,
            lwp_days=0,
            effective_working_days=22,
            
            # Processing metadata
            status=ProcessingStatus(ProcessingStatus.NOT_COMPUTED),
            computation_date=None,
            notes=None,
            remarks=None,
            
            # Audit fields
            organization_id=organization_id,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=created_by
        )
    
    @classmethod
    def from_taxation_projection(
        cls,
        employee_id: EmployeeId,
        month: int,
        year: int,
        tax_year: str,
        organization_id: str,
        monthly_projection: 'PayoutBase',
        created_by: Optional[str] = None
    ) -> 'MonthlySalary':
        """
        Create monthly salary from taxation record projection.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            tax_year: Tax year
            organization_id: Organization ID
            monthly_projection: Monthly payout projection from taxation
            created_by: User who created the record
            
        Returns:
            MonthlySalary: Monthly salary instance with projected data
        """
        now = datetime.utcnow()
        
        return cls(
            employee_id=employee_id,
            month=month,
            year=year,
            tax_year=tax_year,
            
            # Salary components from projection
            basic_salary=Money(Decimal(str(monthly_projection.basic_salary))),
            da=Money(Decimal(str(monthly_projection.da))),
            hra=Money(Decimal(str(monthly_projection.hra))),
            special_allowance=Money(Decimal(str(monthly_projection.special_allowance))),
            transport_allowance=Money(Decimal(str(monthly_projection.transport_allowance))),
            medical_allowance=Money(Decimal(str(monthly_projection.medical_allowance))),
            bonus=Money(Decimal(str(monthly_projection.bonus))),
            commission=Money(Decimal(str(monthly_projection.commission))),
            other_allowances=Money(Decimal(str(monthly_projection.other_allowances))),
            
            # Deductions from projection
            epf_employee=Money(Decimal(str(monthly_projection.epf_employee))),
            esi_employee=Money(Decimal(str(monthly_projection.esi_employee))),
            professional_tax=Money(Decimal(str(monthly_projection.professional_tax))),
            tds=Money(Decimal(str(monthly_projection.tds))),
            advance_deduction=Money(Decimal(str(monthly_projection.advance_deduction))),
            loan_deduction=Money(Decimal(str(monthly_projection.loan_deduction))),
            other_deductions=Money(Decimal(str(monthly_projection.other_deductions))),
            
            # Calculated totals from projection
            gross_salary=Money(Decimal(str(monthly_projection.gross_salary))),
            total_deductions=Money(Decimal(str(monthly_projection.total_deductions))),
            net_salary=Money(Decimal(str(monthly_projection.net_salary))),
            
            # Annual projections from projection
            annual_gross_salary=Money(Decimal(str(monthly_projection.annual_gross_salary))),
            annual_tax_liability=Money(Decimal(str(monthly_projection.annual_tax_liability))),
            
            # Tax details from projection
            tax_regime=monthly_projection.tax_regime or "new",
            tax_exemptions=Money(Decimal(str(monthly_projection.tax_exemptions))),
            standard_deduction=Money(Decimal(str(monthly_projection.standard_deduction))),
            
            # Working days from projection
            total_days_in_month=monthly_projection.total_days_in_month,
            working_days_in_period=monthly_projection.working_days_in_period,
            lwp_days=monthly_projection.lwp_days,
            effective_working_days=monthly_projection.effective_working_days,
            
            # Mark as not yet computed (projection only)
            status=ProcessingStatus(ProcessingStatus.NOT_COMPUTED),
            computation_date=None,
            notes=getattr(monthly_projection, 'notes', None),
            remarks=getattr(monthly_projection, 'remarks', None),
            
            # Audit fields
            organization_id=organization_id,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=created_by
        )
    
    def update_salary_components(
        self,
        basic_salary: Optional[Money] = None,
        da: Optional[Money] = None,
        hra: Optional[Money] = None,
        special_allowance: Optional[Money] = None,
        transport_allowance: Optional[Money] = None,
        medical_allowance: Optional[Money] = None,
        bonus: Optional[Money] = None,
        commission: Optional[Money] = None,
        other_allowances: Optional[Money] = None,
        updated_by: Optional[str] = None
    ) -> None:
        """Update salary components and recalculate totals."""
        
        if basic_salary is not None:
            self.basic_salary = basic_salary
        if da is not None:
            self.da = da
        if hra is not None:
            self.hra = hra
        if special_allowance is not None:
            self.special_allowance = special_allowance
        if transport_allowance is not None:
            self.transport_allowance = transport_allowance
        if medical_allowance is not None:
            self.medical_allowance = medical_allowance
        if bonus is not None:
            self.bonus = bonus
        if commission is not None:
            self.commission = commission
        if other_allowances is not None:
            self.other_allowances = other_allowances
        
        # Recalculate gross salary
        self._recalculate_totals()
        
        # Update audit fields
        self.updated_at = datetime.utcnow()
        if updated_by:
            self.updated_by = updated_by
    
    def update_deductions(
        self,
        epf_employee: Optional[Money] = None,
        esi_employee: Optional[Money] = None,
        professional_tax: Optional[Money] = None,
        tds: Optional[Money] = None,
        advance_deduction: Optional[Money] = None,
        loan_deduction: Optional[Money] = None,
        other_deductions: Optional[Money] = None,
        updated_by: Optional[str] = None
    ) -> None:
        """Update deduction components and recalculate totals."""
        
        if epf_employee is not None:
            self.epf_employee = epf_employee
        if esi_employee is not None:
            self.esi_employee = esi_employee
        if professional_tax is not None:
            self.professional_tax = professional_tax
        if tds is not None:
            self.tds = tds
        if advance_deduction is not None:
            self.advance_deduction = advance_deduction
        if loan_deduction is not None:
            self.loan_deduction = loan_deduction
        if other_deductions is not None:
            self.other_deductions = other_deductions
        
        # Recalculate totals
        self._recalculate_totals()
        
        # Update audit fields
        self.updated_at = datetime.utcnow()
        if updated_by:
            self.updated_by = updated_by
    
    def mark_as_computed(
        self,
        computed_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> None:
        """Mark salary as computed."""
        self.status = ProcessingStatus(ProcessingStatus.COMPUTED)
        self.computation_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if computed_by:
            self.updated_by = computed_by
        if notes:
            self.notes = notes
    
    def approve_salary(
        self,
        approved_by: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> None:
        """Approve computed salary."""
        if not self.status.is_computed():
            raise ValueError("Cannot approve salary that has not been computed")
        
        self.status = ProcessingStatus(ProcessingStatus.APPROVED)
        self.updated_at = datetime.utcnow()
        
        if approved_by:
            self.updated_by = approved_by
        if remarks:
            self.remarks = remarks
    
    def reject_salary(
        self,
        rejected_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """Reject computed salary."""
        self.status = ProcessingStatus(ProcessingStatus.REJECTED)
        self.updated_at = datetime.utcnow()
        
        if rejected_by:
            self.updated_by = rejected_by
        if reason:
            self.remarks = reason
    
    def mark_as_paid(
        self,
        paid_by: Optional[str] = None,
        payment_notes: Optional[str] = None
    ) -> None:
        """Mark salary as paid."""
        if self.status.value != ProcessingStatus.APPROVED:
            raise ValueError("Can only mark approved salaries as paid")
        
        self.status = ProcessingStatus(ProcessingStatus.PAID)
        self.updated_at = datetime.utcnow()
        
        if paid_by:
            self.updated_by = paid_by
        if payment_notes:
            self.notes = payment_notes
    
    def _recalculate_totals(self) -> None:
        """Recalculate gross salary, total deductions, and net salary."""
        # Calculate gross salary
        self.gross_salary = (
            self.basic_salary
            .add(self.da)
            .add(self.hra)
            .add(self.special_allowance)
            .add(self.transport_allowance)
            .add(self.medical_allowance)
            .add(self.bonus)
            .add(self.commission)
            .add(self.other_allowances)
        )
        
        # Calculate total deductions
        self.total_deductions = (
            self.epf_employee
            .add(self.esi_employee)
            .add(self.professional_tax)
            .add(self.tds)
            .add(self.advance_deduction)
            .add(self.loan_deduction)
            .add(self.other_deductions)
        )
        
        # Calculate net salary
        self.net_salary = self.gross_salary.subtract(self.total_deductions)
        
        # Ensure net salary is not negative
        if self.net_salary.amount < 0:
            self.net_salary = Money.zero()
    
    def get_month_year_key(self) -> str:
        """Get a unique key for month-year combination."""
        return f"{self.year}-{self.month:02d}"
    
    def is_current_month(self) -> bool:
        """Check if this record is for the current month."""
        now = datetime.now()
        return self.month == now.month and self.year == now.year
    
    def get_salary_breakdown(self) -> Dict[str, Any]:
        """Get detailed salary breakdown."""
        return {
            "employee_id": str(self.employee_id),
            "month": self.month,
            "year": self.year,
            "tax_year": self.tax_year,
            "status": self.status.value,
            "is_computed": self.status.is_computed(),
            
            "earnings": {
                "basic_salary": self.basic_salary.to_float(),
                "da": self.da.to_float(),
                "hra": self.hra.to_float(),
                "special_allowance": self.special_allowance.to_float(),
                "transport_allowance": self.transport_allowance.to_float(),
                "medical_allowance": self.medical_allowance.to_float(),
                "bonus": self.bonus.to_float(),
                "commission": self.commission.to_float(),
                "other_allowances": self.other_allowances.to_float(),
                "gross_salary": self.gross_salary.to_float()
            },
            
            "deductions": {
                "epf_employee": self.epf_employee.to_float(),
                "esi_employee": self.esi_employee.to_float(),
                "professional_tax": self.professional_tax.to_float(),
                "tds": self.tds.to_float(),
                "advance_deduction": self.advance_deduction.to_float(),
                "loan_deduction": self.loan_deduction.to_float(),
                "other_deductions": self.other_deductions.to_float(),
                "total_deductions": self.total_deductions.to_float()
            },
            
            "summary": {
                "gross_salary": self.gross_salary.to_float(),
                "total_deductions": self.total_deductions.to_float(),
                "net_salary": self.net_salary.to_float(),
                "effective_working_days": self.effective_working_days,
                "lwp_days": self.lwp_days
            }
        }
    
    def __str__(self) -> str:
        return f"MonthlySalary({self.employee_id}, {self.month:02d}/{self.year}, {self.status.value})" 