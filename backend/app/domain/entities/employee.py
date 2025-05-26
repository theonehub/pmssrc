"""
Employee Domain Entity
Aggregate root for employee-related operations
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum

from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.money import Money
from domain.events.employee_events import (
    EmployeeCreated, SalaryChanged, EmployeeActivated, 
    EmployeeDeactivated, EmployeePromoted
)


class EmployeeStatus(Enum):
    """Employee status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"


class EmployeeType(Enum):
    """Employee type enumeration"""
    PERMANENT = "permanent"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"
    CONSULTANT = "consultant"


@dataclass
class Employee:
    """
    Employee aggregate root following DDD principles.
    
    Follows SOLID principles:
    - SRP: Only handles employee-related business logic
    - OCP: Can be extended with new employee types without modification
    - LSP: Can be substituted anywhere Employee is expected
    - ISP: Provides focused employee operations
    - DIP: Depends on abstractions (value objects, events)
    """
    
    # Identity
    id: EmployeeId
    
    # Basic Information
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    
    # Employment Details
    date_of_joining: date
    date_of_birth: date
    employee_type: EmployeeType = EmployeeType.PERMANENT
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    
    # Salary Information
    current_salary: Money = field(default_factory=lambda: Money.zero())
    
    # Organizational Information
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_id: Optional[EmployeeId] = None
    
    # Personal Information
    address: Optional[Dict[str, str]] = None
    emergency_contact: Optional[Dict[str, str]] = None
    
    # System Fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Domain Events
    _domain_events: List = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Post initialization validation and setup"""
        self._validate_employee_data()
        
        # Raise domain event for new employee creation
        if not hasattr(self, '_is_existing_employee'):
            self._domain_events.append(
                EmployeeCreated(
                    employee_id=self.id,
                    name=self.get_full_name(),
                    email=self.email,
                    date_of_joining=self.date_of_joining,
                    occurred_at=datetime.utcnow()
                )
            )
    
    @classmethod
    def create_new_employee(
        cls,
        employee_id: EmployeeId,
        first_name: str,
        last_name: str,
        email: str,
        date_of_joining: date,
        date_of_birth: date,
        initial_salary: Money,
        employee_type: EmployeeType = EmployeeType.PERMANENT,
        department: Optional[str] = None,
        designation: Optional[str] = None
    ) -> 'Employee':
        """Factory method to create a new employee"""
        
        employee = cls(
            id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_joining=date_of_joining,
            date_of_birth=date_of_birth,
            current_salary=initial_salary,
            employee_type=employee_type,
            department=department,
            designation=designation
        )
        
        return employee
    
    @classmethod
    def from_existing_data(cls, **kwargs) -> 'Employee':
        """Create employee from existing data (for repository loading)"""
        employee = cls(**kwargs)
        employee._is_existing_employee = True
        return employee
    
    def get_full_name(self) -> str:
        """Get employee's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_age(self) -> int:
        """Calculate employee's current age"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def get_years_of_service(self) -> int:
        """Calculate years of service"""
        today = date.today()
        return today.year - self.date_of_joining.year - (
            (today.month, today.day) < (self.date_of_joining.month, self.date_of_joining.day)
        )
    
    def is_senior_citizen(self) -> bool:
        """Check if employee is a senior citizen (60+ years)"""
        return self.get_age() >= 60
    
    def is_super_senior_citizen(self) -> bool:
        """Check if employee is a super senior citizen (80+ years)"""
        return self.get_age() >= 80
    
    def is_active(self) -> bool:
        """Check if employee is active"""
        return self.status == EmployeeStatus.ACTIVE
    
    def is_permanent(self) -> bool:
        """Check if employee is permanent"""
        return self.employee_type == EmployeeType.PERMANENT
    
    def change_salary(
        self, 
        new_salary: Money, 
        effective_date: date, 
        reason: str,
        changed_by: Optional[EmployeeId] = None
    ):
        """
        Change employee salary - follows business rules.
        
        Business Rules:
        1. New salary must be positive
        2. Effective date cannot be in the past
        3. Salary change must have a reason
        """
        
        # Validate business rules
        if not new_salary.is_positive():
            raise ValueError("New salary must be positive")
        
        if effective_date < date.today():
            raise ValueError("Effective date cannot be in the past")
        
        if not reason or not reason.strip():
            raise ValueError("Salary change reason is required")
        
        # Store old salary for event
        old_salary = self.current_salary
        
        # Update salary
        self.current_salary = new_salary
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._domain_events.append(
            SalaryChanged(
                employee_id=self.id,
                old_salary=old_salary,
                new_salary=new_salary,
                effective_date=effective_date,
                reason=reason,
                changed_by=changed_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def promote(
        self, 
        new_designation: str, 
        new_salary: Money, 
        effective_date: date,
        promoted_by: Optional[EmployeeId] = None
    ):
        """
        Promote employee with new designation and salary.
        
        Business Rules:
        1. New designation must be different from current
        2. New salary should typically be higher than current
        3. Effective date cannot be in the past
        """
        
        if new_designation == self.designation:
            raise ValueError("New designation must be different from current designation")
        
        if effective_date < date.today():
            raise ValueError("Effective date cannot be in the past")
        
        # Store old values for event
        old_designation = self.designation
        old_salary = self.current_salary
        
        # Update employee details
        self.designation = new_designation
        self.current_salary = new_salary
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._domain_events.append(
            EmployeePromoted(
                employee_id=self.id,
                old_designation=old_designation,
                new_designation=new_designation,
                old_salary=old_salary,
                new_salary=new_salary,
                effective_date=effective_date,
                promoted_by=promoted_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def activate(self, activated_by: Optional[EmployeeId] = None):
        """
        Activate employee.
        
        Business Rules:
        1. Can only activate inactive employees
        2. Cannot activate terminated employees
        """
        
        if self.status == EmployeeStatus.TERMINATED:
            raise ValueError("Cannot activate terminated employee")
        
        if self.status == EmployeeStatus.ACTIVE:
            raise ValueError("Employee is already active")
        
        old_status = self.status
        self.status = EmployeeStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._domain_events.append(
            EmployeeActivated(
                employee_id=self.id,
                previous_status=old_status.value,
                activated_by=activated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def deactivate(self, reason: str, deactivated_by: Optional[EmployeeId] = None):
        """
        Deactivate employee.
        
        Business Rules:
        1. Can only deactivate active employees
        2. Must provide reason for deactivation
        """
        
        if self.status != EmployeeStatus.ACTIVE:
            raise ValueError("Can only deactivate active employees")
        
        if not reason or not reason.strip():
            raise ValueError("Deactivation reason is required")
        
        old_status = self.status
        self.status = EmployeeStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._domain_events.append(
            EmployeeDeactivated(
                employee_id=self.id,
                previous_status=old_status.value,
                reason=reason,
                deactivated_by=deactivated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def terminate(self, termination_date: date, reason: str, terminated_by: Optional[EmployeeId] = None):
        """
        Terminate employee.
        
        Business Rules:
        1. Termination date cannot be in the past
        2. Must provide reason for termination
        3. Cannot terminate already terminated employee
        """
        
        if self.status == EmployeeStatus.TERMINATED:
            raise ValueError("Employee is already terminated")
        
        if termination_date < date.today():
            raise ValueError("Termination date cannot be in the past")
        
        if not reason or not reason.strip():
            raise ValueError("Termination reason is required")
        
        old_status = self.status
        self.status = EmployeeStatus.TERMINATED
        self.updated_at = datetime.utcnow()
        
        # Note: We could create a EmployeeTerminated event here
        # For now, using deactivated event with termination context
        self._domain_events.append(
            EmployeeDeactivated(
                employee_id=self.id,
                previous_status=old_status.value,
                reason=f"TERMINATED: {reason}",
                deactivated_by=terminated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def update_personal_info(
        self, 
        phone: Optional[str] = None,
        address: Optional[Dict[str, str]] = None,
        emergency_contact: Optional[Dict[str, str]] = None
    ):
        """Update employee personal information"""
        
        if phone is not None:
            self.phone = phone
        
        if address is not None:
            self.address = address
        
        if emergency_contact is not None:
            self.emergency_contact = emergency_contact
        
        self.updated_at = datetime.utcnow()
    
    def assign_manager(self, manager_id: EmployeeId):
        """Assign manager to employee"""
        if manager_id == self.id:
            raise ValueError("Employee cannot be their own manager")
        
        self.manager_id = manager_id
        self.updated_at = datetime.utcnow()
    
    def transfer_department(self, new_department: str, effective_date: date):
        """Transfer employee to new department"""
        if effective_date < date.today():
            raise ValueError("Transfer date cannot be in the past")
        
        if new_department == self.department:
            raise ValueError("Employee is already in this department")
        
        old_department = self.department
        self.department = new_department
        self.updated_at = datetime.utcnow()
        
        # Could raise a EmployeeTransferred event here
    
    def get_domain_events(self) -> List:
        """Get list of domain events"""
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """Clear domain events after processing"""
        self._domain_events.clear()
    
    def _validate_employee_data(self):
        """Validate employee data consistency"""
        
        # Validate names
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name is required")
        
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name is required")
        
        # Validate email
        if not self.email or '@' not in self.email:
            raise ValueError("Valid email is required")
        
        # Validate dates
        if self.date_of_birth >= date.today():
            raise ValueError("Date of birth must be in the past")
        
        if self.date_of_joining > date.today():
            raise ValueError("Date of joining cannot be in the future")
        
        if self.date_of_birth >= self.date_of_joining:
            raise ValueError("Date of joining must be after date of birth")
        
        # Validate age (minimum 18 years at joining)
        joining_age = self.date_of_joining.year - self.date_of_birth.year - (
            (self.date_of_joining.month, self.date_of_joining.day) < 
            (self.date_of_birth.month, self.date_of_birth.day)
        )
        
        if joining_age < 18:
            raise ValueError("Employee must be at least 18 years old at joining")
        
        # Validate salary
        if not self.current_salary.is_zero() and not self.current_salary.is_positive():
            raise ValueError("Salary must be positive or zero")
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.get_full_name()} ({self.id})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Employee(id={self.id}, name='{self.get_full_name()}', status={self.status.value})" 