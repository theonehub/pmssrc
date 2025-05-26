"""
Company Leave Domain Entity
Aggregate root for company leave policies and configurations
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from datetime import datetime
from uuid import uuid4

from domain.value_objects.leave_type import LeaveType
from domain.value_objects.leave_policy import LeavePolicy
from domain.events.leave_events import (
    CompanyLeaveCreated, CompanyLeaveUpdated, CompanyLeaveDeactivated,
    CompanyLeavePolicyChanged
)


@dataclass
class CompanyLeave:
    """
    Company Leave aggregate root following DDD principles.
    
    Follows SOLID principles:
    - SRP: Only handles company leave policy management
    - OCP: Can be extended with new leave types without modification
    - LSP: Can be substituted anywhere CompanyLeave is expected
    - ISP: Provides focused leave policy operations
    - DIP: Depends on abstractions (value objects, events)
    """
    
    # Identity
    company_leave_id: str
    leave_type: LeaveType
    
    # Policy Configuration
    policy: LeavePolicy
    
    # Status
    is_active: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Additional Configuration
    description: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None
    
    # Domain Events
    _domain_events: List = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Post initialization validation"""
        self._validate_company_leave_data()
    
    @classmethod
    def create_new_company_leave(
        cls,
        leave_type: LeaveType,
        policy: LeavePolicy,
        created_by: str,
        description: Optional[str] = None,
        effective_from: Optional[datetime] = None
    ) -> 'CompanyLeave':
        """Factory method to create new company leave"""
        
        company_leave_id = str(uuid4())
        
        company_leave = cls(
            company_leave_id=company_leave_id,
            leave_type=leave_type,
            policy=policy,
            created_by=created_by,
            description=description,
            effective_from=effective_from or datetime.utcnow()
        )
        
        # Raise domain event
        company_leave._domain_events.append(
            CompanyLeaveCreated(
                company_leave_id=company_leave_id,
                leave_type=leave_type,
                policy=policy,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return company_leave
    
    @classmethod
    def create_with_standard_policy(
        cls,
        leave_type: LeaveType,
        annual_allocation: int,
        created_by: str,
        description: Optional[str] = None
    ) -> 'CompanyLeave':
        """Create company leave with standard policy for the leave type"""
        
        policy = LeavePolicy.create_standard_policy(
            leave_type=leave_type,
            annual_allocation=annual_allocation
        )
        
        return cls.create_new_company_leave(
            leave_type=leave_type,
            policy=policy,
            created_by=created_by,
            description=description
        )
    
    def update_policy(self, new_policy: LeavePolicy, updated_by: str, reason: str):
        """
        Update leave policy.
        
        Business Rules:
        1. Policy must be for the same leave type
        2. Must provide reason for change
        3. Change should be effective from future date for existing employees
        """
        
        if new_policy.leave_type != self.leave_type:
            raise ValueError("New policy must be for the same leave type")
        
        if not reason or not reason.strip():
            raise ValueError("Reason for policy change is required")
        
        old_policy = self.policy
        self.policy = new_policy
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        
        # Raise domain event
        self._domain_events.append(
            CompanyLeavePolicyChanged(
                company_leave_id=self.company_leave_id,
                leave_type=self.leave_type,
                old_policy=old_policy,
                new_policy=new_policy,
                reason=reason,
                updated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def update_allocation(self, new_allocation: int, updated_by: str, reason: str):
        """Update annual allocation while keeping other policy settings"""
        
        if new_allocation < 0:
            raise ValueError("Annual allocation cannot be negative")
        
        # Create new policy with updated allocation
        import dataclasses
        new_policy = dataclasses.replace(self.policy, annual_allocation=new_allocation)
        
        self.update_policy(new_policy, updated_by, reason)
    
    def update_details(
        self, 
        description: Optional[str] = None,
        effective_from: Optional[datetime] = None,
        effective_until: Optional[datetime] = None,
        updated_by: Optional[str] = None
    ):
        """Update company leave details"""
        
        old_description = self.description
        
        if description is not None:
            self.description = description.strip() if description else None
        
        if effective_from is not None:
            self.effective_from = effective_from
        
        if effective_until is not None:
            self.effective_until = effective_until
        
        self.updated_at = datetime.utcnow()
        if updated_by:
            self.updated_by = updated_by
        
        # Raise domain event if significant changes
        if description != old_description:
            self._domain_events.append(
                CompanyLeaveUpdated(
                    company_leave_id=self.company_leave_id,
                    leave_type=self.leave_type,
                    changes={
                        'description': {'old': old_description, 'new': self.description},
                        'effective_from': {'old': None, 'new': self.effective_from},
                        'effective_until': {'old': None, 'new': self.effective_until}
                    },
                    updated_by=updated_by,
                    occurred_at=datetime.utcnow()
                )
            )
    
    def deactivate(self, deactivated_by: str, reason: str):
        """
        Deactivate company leave.
        
        Business Rules:
        1. Must provide reason for deactivation
        2. Should handle existing employee leave balances
        3. Cannot deactivate if employees have pending applications
        """
        
        if not self.is_active:
            raise ValueError("Company leave is already deactivated")
        
        if not reason or not reason.strip():
            raise ValueError("Reason for deactivation is required")
        
        self.is_active = False
        self.updated_at = datetime.utcnow()
        self.updated_by = deactivated_by
        
        # Raise domain event
        self._domain_events.append(
            CompanyLeaveDeactivated(
                company_leave_id=self.company_leave_id,
                leave_type=self.leave_type,
                reason=reason,
                deactivated_by=deactivated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def reactivate(self, reactivated_by: str):
        """Reactivate company leave"""
        
        if self.is_active:
            raise ValueError("Company leave is already active")
        
        self.is_active = True
        self.updated_at = datetime.utcnow()
        self.updated_by = reactivated_by
    
    def is_effective_on(self, check_date: datetime) -> bool:
        """Check if leave policy is effective on given date"""
        
        if not self.is_active:
            return False
        
        if self.effective_from and check_date < self.effective_from:
            return False
        
        if self.effective_until and check_date > self.effective_until:
            return False
        
        return True
    
    def is_applicable_for_employee(
        self,
        employee_gender: Optional[str] = None,
        employee_category: Optional[str] = None,
        is_on_probation: bool = False
    ) -> bool:
        """Check if leave is applicable for employee"""
        
        if not self.is_active:
            return False
        
        return self.policy.is_applicable_for_employee(
            employee_gender=employee_gender,
            employee_category=employee_category,
            is_on_probation=is_on_probation
        )
    
    def get_annual_allocation_for_employee(self, is_on_probation: bool = False) -> int:
        """Get annual allocation for employee based on their status"""
        return self.policy.get_effective_allocation(is_on_probation)
    
    def calculate_accrued_days(self, months_completed: int) -> float:
        """Calculate accrued leave days for employee"""
        accrued = self.policy.calculate_accrued_days(months_completed)
        return float(accrued)
    
    def validate_leave_application(
        self,
        requested_days: int,
        advance_notice_days: int = 0
    ) -> List[str]:
        """Validate leave application against policy"""
        
        errors = []
        
        if not self.is_active:
            errors.append("This leave type is not currently active")
        
        # Validate application days
        policy_errors = self.policy.validate_application_days(requested_days)
        errors.extend(policy_errors)
        
        # Validate advance notice
        if advance_notice_days < self.policy.min_advance_notice_days:
            errors.append(
                f"Minimum {self.policy.min_advance_notice_days} days advance notice required"
            )
        
        return errors
    
    def can_auto_approve_application(self, requested_days: int) -> bool:
        """Check if application can be auto-approved"""
        return self.policy.can_auto_approve(requested_days)
    
    def requires_medical_certificate(self, requested_days: int) -> bool:
        """Check if medical certificate is required"""
        return self.policy.requires_medical_cert_for_days(requested_days)
    
    def calculate_encashment_amount(self, days_to_encash: int, daily_salary: float) -> float:
        """Calculate leave encashment amount"""
        from decimal import Decimal
        daily_salary_decimal = Decimal(str(daily_salary))
        amount = self.policy.calculate_encashment_amount(days_to_encash, daily_salary_decimal)
        return float(amount)
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of leave policy"""
        return {
            'leave_type': {
                'code': self.leave_type.code,
                'name': self.leave_type.name,
                'category': self.leave_type.category.value
            },
            'annual_allocation': self.policy.annual_allocation,
            'accrual_type': self.policy.accrual_type.value,
            'max_carryover_days': self.policy.max_carryover_days,
            'min_advance_notice_days': self.policy.min_advance_notice_days,
            'requires_approval': self.policy.requires_approval,
            'requires_medical_certificate': self.policy.requires_medical_certificate,
            'is_encashable': self.policy.is_encashable,
            'available_during_probation': self.policy.available_during_probation,
            'gender_specific': self.policy.gender_specific
        }
    
    def _validate_company_leave_data(self):
        """Validate company leave data consistency"""
        
        if not self.company_leave_id:
            raise ValueError("Company leave ID is required")
        
        if self.effective_from and self.effective_until:
            if self.effective_from >= self.effective_until:
                raise ValueError("Effective from date must be before effective until date")
    
    def get_domain_events(self) -> List:
        """Get list of domain events"""
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """Clear domain events after processing"""
        self._domain_events.clear()
    
    def __str__(self) -> str:
        """String representation"""
        status = "Active" if self.is_active else "Inactive"
        return f"{self.leave_type.name} ({self.policy.annual_allocation} days/year) - {status}"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"CompanyLeave(id='{self.company_leave_id}', leave_type={self.leave_type}, active={self.is_active})" 