"""
Taxation Domain Events
Events that represent important business occurrences in the taxation domain
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any
from decimal import Decimal

from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.money import Money
from domain.events.employee_events import DomainEvent


@dataclass
class TaxationCalculated(DomainEvent):
    """
    Event raised when tax calculation is completed for an employee.
    
    This event can trigger:
    - Tax report generation
    - Payroll system updates
    - Notification to HR/Finance
    - Audit trail updates
    """
    
    employee_id: EmployeeId
    tax_year: str
    regime: str
    total_tax: Money
    taxable_income: Money
    calculated_by: Optional[EmployeeId] = None
    occurred_at: datetime = field(default_factory=lambda: datetime.utcnow())
    event_id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    
    def __post_init__(self):
        """Initialize parent class"""
        super().__init__(self.occurred_at, self.event_id)
    
    def get_event_type(self) -> str:
        return "taxation.calculated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class TaxRegimeChanged(DomainEvent):
    """
    Event raised when an employee's tax regime is changed.
    
    This event can trigger:
    - Tax recalculation
    - Notification to employee
    - Payroll adjustments
    - Compliance record updates
    """
    
    employee_id: EmployeeId
    old_regime: str
    new_regime: str
    tax_year: str
    effective_date: date
    changed_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "taxation.regime_changed"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class TaxComponentUpdated(DomainEvent):
    """
    Event raised when tax component (salary, deductions, etc.) is updated.
    
    This event can trigger:
    - Tax recalculation
    - Impact analysis
    - Audit logging
    - Approval workflows
    """
    
    employee_id: EmployeeId
    component_type: str  # 'salary', 'deductions', 'capital_gains', etc.
    component_name: str
    old_value: Optional[Money] = None
    new_value: Optional[Money] = None
    tax_year: str = ""
    updated_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "taxation.component_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class TaxDeductionApplied(DomainEvent):
    """
    Event raised when tax deduction is applied.
    
    This event can trigger:
    - Deduction verification
    - Compliance tracking
    - Document requirement notifications
    - Audit trail updates
    """
    
    employee_id: EmployeeId
    deduction_section: str  # '80C', '80D', etc.
    deduction_amount: Money
    tax_year: str
    applied_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "taxation.deduction_applied"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class TaxProjectionGenerated(DomainEvent):
    """
    Event raised when tax projection is generated for an employee.
    
    This event can trigger:
    - Investment planning notifications
    - Tax savings suggestions
    - Financial planning updates
    """
    
    employee_id: EmployeeId
    projected_tax: Money
    projected_savings: Money
    tax_year: str
    projection_type: str  # 'annual', 'quarterly', 'monthly'
    generated_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "taxation.projection_generated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class LWPTaxAdjustmentApplied(DomainEvent):
    """
    Event raised when LWP (Leave Without Pay) tax adjustment is applied.
    
    This event can trigger:
    - Salary adjustment notifications
    - Tax recalculation
    - Payroll updates
    """
    
    employee_id: EmployeeId
    lwp_days: int
    salary_reduction: Money
    tax_savings: Money
    adjustment_period: str
    applied_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "taxation.lwp_adjustment_applied"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class TaxFilingStatusUpdated(DomainEvent):
    """
    Event raised when tax filing status is updated.
    
    This event can trigger:
    - Filing deadline reminders
    - Document preparation
    - Compliance tracking
    """
    
    employee_id: EmployeeId
    old_status: str
    new_status: str
    tax_year: str
    updated_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "taxation.filing_status_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class TaxationUpdated(DomainEvent):
    """
    Event raised when taxation record is updated.
    
    This event can trigger:
    - Change notifications
    - Audit logging
    - Dependent calculations
    """
    
    employee_id: EmployeeId
    tax_year: str
    update_type: str
    updated_fields: Dict[str, Any]
    updated_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "taxation.updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class TaxFilingStatusChanged(DomainEvent):
    """
    Event raised when tax filing status is changed.
    
    This is an alias for TaxFilingStatusUpdated for backward compatibility.
    """
    
    employee_id: EmployeeId
    old_status: str
    new_status: str
    tax_year: str
    updated_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "taxation.filing_status_changed"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


# Event type registry for easy lookup
TAXATION_EVENT_TYPE_REGISTRY = {
    "taxation.calculated": TaxationCalculated,
    "taxation.regime_changed": TaxRegimeChanged,
    "taxation.component_updated": TaxComponentUpdated,
    "taxation.deduction_applied": TaxDeductionApplied,
    "taxation.projection_generated": TaxProjectionGenerated,
    "taxation.lwp_adjustment_applied": LWPTaxAdjustmentApplied,
    "taxation.filing_status_updated": TaxFilingStatusUpdated,
}


def get_taxation_event_class(event_type: str) -> type:
    """Get taxation event class by event type string"""
    return TAXATION_EVENT_TYPE_REGISTRY.get(event_type)


def is_valid_taxation_event_type(event_type: str) -> bool:
    """Check if taxation event type is valid"""
    return event_type in TAXATION_EVENT_TYPE_REGISTRY 