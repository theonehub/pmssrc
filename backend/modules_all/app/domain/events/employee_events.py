"""
Employee Domain Events
Events that represent important business occurrences in the employee domain
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from abc import ABC

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money


class DomainEvent(ABC):
    """
    Base class for all domain events.
    
    Follows SOLID principles:
    - SRP: Only represents event data
    - OCP: Can be extended with new event types
    - LSP: All events can be treated uniformly
    - ISP: Minimal interface for events
    - DIP: Doesn't depend on concrete implementations
    """
    
    def __init__(self, occurred_at: datetime = None, event_id: str = ""):
        self.occurred_at = occurred_at or datetime.utcnow()
        self.event_id = event_id or str(__import__('uuid').uuid4())
    



@dataclass
class EmployeeCreated(DomainEvent):
    """
    Event raised when a new employee is created.
    
    This event can trigger:
    - Welcome email sending
    - Account setup processes
    - Onboarding workflow initiation
    - Audit logging
    """
    
    employee_id: EmployeeId
    name: str
    email: str
    date_of_joining: date
    occurred_at: datetime = field(default_factory=lambda: datetime.utcnow())
    event_id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    
    def __post_init__(self):
        """Initialize parent class"""
        super().__init__(self.occurred_at, self.event_id)
    
    def get_event_type(self) -> str:
        return "employee.created"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class SalaryChanged(DomainEvent):
    """
    Event raised when an employee's salary is changed.
    
    This event can trigger:
    - Payroll system updates
    - Tax calculation recalculation
    - Notification to HR/Finance
    - Audit logging
    - Contract amendment generation
    """
    
    employee_id: EmployeeId
    old_salary: Money
    new_salary: Money
    effective_date: date
    reason: str
    changed_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "employee.salary_changed"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def get_salary_increase_amount(self) -> Money:
        """Calculate salary increase amount"""
        if self.new_salary.currency != self.old_salary.currency:
            raise ValueError("Cannot calculate increase for different currencies")
        
        if self.new_salary.amount >= self.old_salary.amount:
            return self.new_salary.subtract(self.old_salary)
        else:
            return Money.zero(self.new_salary.currency)
    
    def get_salary_decrease_amount(self) -> Money:
        """Calculate salary decrease amount"""
        if self.new_salary.currency != self.old_salary.currency:
            raise ValueError("Cannot calculate decrease for different currencies")
        
        if self.old_salary.amount > self.new_salary.amount:
            return self.old_salary.subtract(self.new_salary)
        else:
            return Money.zero(self.new_salary.currency)
    
    def is_salary_increase(self) -> bool:
        """Check if this is a salary increase"""
        return self.new_salary.amount > self.old_salary.amount
    
    def is_salary_decrease(self) -> bool:
        """Check if this is a salary decrease"""
        return self.new_salary.amount < self.old_salary.amount
    
    def get_percentage_change(self) -> float:
        """Calculate percentage change in salary"""
        if self.old_salary.is_zero():
            return 100.0 if self.new_salary.is_positive() else 0.0
        
        change = self.new_salary.amount - self.old_salary.amount
        return float((change / self.old_salary.amount) * 100)


@dataclass
class EmployeePromoted(DomainEvent):
    """
    Event raised when an employee is promoted.
    
    This event can trigger:
    - Congratulatory notifications
    - Role and permission updates
    - Organisational chart updates
    - Performance review scheduling
    - Career progression tracking
    """
    
    employee_id: EmployeeId
    old_designation: Optional[str]
    new_designation: str
    old_salary: Money
    new_salary: Money
    effective_date: date
    promoted_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "employee.promoted"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def get_promotion_details(self) -> dict:
        """Get promotion details summary"""
        return {
            "employee_id": str(self.employee_id),
            "designation_change": {
                "from": self.old_designation,
                "to": self.new_designation
            },
            "salary_change": {
                "from": self.old_salary.format(),
                "to": self.new_salary.format(),
                "increase": self.new_salary.subtract(self.old_salary).format()
            },
            "effective_date": self.effective_date.isoformat(),
            "promoted_by": str(self.promoted_by) if self.promoted_by else None
        }


@dataclass
class EmployeeActivated(DomainEvent):
    """
    Event raised when an employee is activated.
    
    This event can trigger:
    - System access restoration
    - Email account reactivation
    - Notification to team members
    - Payroll system updates
    """
    
    employee_id: EmployeeId
    previous_status: str
    activated_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "employee.activated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class EmployeeDeactivated(DomainEvent):
    """
    Event raised when an employee is deactivated.
    
    This event can trigger:
    - System access revocation
    - Email account suspension
    - Asset return reminders
    - Exit interview scheduling
    - Final settlement calculations
    """
    
    employee_id: EmployeeId
    previous_status: str
    reason: str
    deactivated_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "employee.deactivated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)
    
    def is_termination(self) -> bool:
        """Check if this deactivation is due to termination"""
        return self.reason.startswith("TERMINATED:")
    
    def get_termination_reason(self) -> Optional[str]:
        """Get termination reason if this is a termination"""
        if self.is_termination():
            return self.reason.replace("TERMINATED:", "").strip()
        return None


@dataclass
class EmployeeDepartmentChanged(DomainEvent):
    """
    Event raised when an employee's department is changed.
    
    This event can trigger:
    - Reporting structure updates
    - Budget allocation changes
    - Team notification
    - Access permission updates
    """
    
    employee_id: EmployeeId
    old_department: Optional[str]
    new_department: str
    effective_date: date
    changed_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "employee.department_changed"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class EmployeeManagerAssigned(DomainEvent):
    """
    Event raised when an employee is assigned a new manager.
    
    This event can trigger:
    - Reporting relationship updates
    - Notification to new manager
    - Performance review reassignment
    - Goal setting sessions
    """
    
    employee_id: EmployeeId
    old_manager_id: Optional[EmployeeId]
    new_manager_id: EmployeeId
    assigned_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "employee.manager_assigned"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


@dataclass
class EmployeePersonalInfoUpdated(DomainEvent):
    """
    Event raised when an employee's personal information is updated.
    
    This event can trigger:
    - Contact directory updates
    - Emergency contact notifications
    - Compliance record updates
    """
    
    employee_id: EmployeeId
    updated_fields: list
    updated_by: Optional[EmployeeId] = None
    
    def get_event_type(self) -> str:
        return "employee.personal_info_updated"
    
    def get_aggregate_id(self) -> str:
        return str(self.employee_id)


# Event type registry for easy lookup
EVENT_TYPE_REGISTRY = {
    "employee.created": EmployeeCreated,
    "employee.salary_changed": SalaryChanged,
    "employee.promoted": EmployeePromoted,
    "employee.activated": EmployeeActivated,
    "employee.deactivated": EmployeeDeactivated,
    "employee.department_changed": EmployeeDepartmentChanged,
    "employee.manager_assigned": EmployeeManagerAssigned,
    "employee.personal_info_updated": EmployeePersonalInfoUpdated,
}


def get_event_class(event_type: str) -> type:
    """Get event class by event type string"""
    return EVENT_TYPE_REGISTRY.get(event_type)


def is_valid_event_type(event_type: str) -> bool:
    """Check if event type is valid"""
    return event_type in EVENT_TYPE_REGISTRY 