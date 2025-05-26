"""
Leave Policy Value Object
Immutable value object representing leave policies and business rules
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from decimal import Decimal

from domain.value_objects.leave_type import LeaveType, AccrualType


@dataclass(frozen=True)
class LeavePolicy:
    """
    Leave policy value object ensuring immutability and validation.
    
    Follows SOLID principles:
    - SRP: Only handles leave policy representation and rules
    - OCP: Can be extended without modification
    - LSP: Can be substituted anywhere LeavePolicy is expected
    - ISP: Provides only leave policy operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    leave_type: LeaveType
    annual_allocation: int  # Total days allocated per year
    accrual_type: AccrualType
    accrual_rate: Optional[Decimal] = None  # Days per month/quarter (if applicable)
    
    # Carryover rules
    max_carryover_days: int = 0
    carryover_expiry_months: int = 12  # Months after which carried over leave expires
    
    # Application rules
    min_advance_notice_days: int = 0
    max_advance_application_days: int = 365
    min_application_days: int = 1  # Minimum days that can be applied
    max_continuous_days: Optional[int] = None
    
    # Approval rules
    requires_approval: bool = True
    auto_approve_threshold: Optional[int] = None  # Auto-approve if <= this many days
    
    # Documentation requirements
    requires_medical_certificate: bool = False
    medical_certificate_threshold: Optional[int] = None  # Days after which medical cert required
    
    # Encashment rules
    is_encashable: bool = False
    max_encashment_days: int = 0
    encashment_percentage: Decimal = Decimal('100')  # Percentage of salary for encashment
    
    # Probation rules
    available_during_probation: bool = True
    probation_allocation: Optional[int] = None  # Different allocation during probation
    
    # Gender/category specific
    gender_specific: Optional[str] = None  # 'male', 'female', None for all
    employee_category_specific: Optional[List[str]] = None  # Specific employee categories
    
    def __post_init__(self):
        """Validate leave policy on creation"""
        if self.annual_allocation < 0:
            raise ValueError("Annual allocation cannot be negative")
        
        if self.max_carryover_days < 0:
            raise ValueError("Max carryover days cannot be negative")
        
        if self.max_carryover_days > self.annual_allocation:
            raise ValueError("Max carryover days cannot exceed annual allocation")
        
        if self.carryover_expiry_months <= 0:
            raise ValueError("Carryover expiry months must be positive")
        
        if self.min_advance_notice_days < 0:
            raise ValueError("Min advance notice days cannot be negative")
        
        if self.max_advance_application_days <= 0:
            raise ValueError("Max advance application days must be positive")
        
        if self.min_application_days <= 0:
            raise ValueError("Min application days must be positive")
        
        if self.max_continuous_days is not None and self.max_continuous_days <= 0:
            raise ValueError("Max continuous days must be positive if specified")
        
        if self.auto_approve_threshold is not None and self.auto_approve_threshold <= 0:
            raise ValueError("Auto approve threshold must be positive if specified")
        
        if self.medical_certificate_threshold is not None and self.medical_certificate_threshold <= 0:
            raise ValueError("Medical certificate threshold must be positive if specified")
        
        if self.max_encashment_days < 0:
            raise ValueError("Max encashment days cannot be negative")
        
        if not (0 <= self.encashment_percentage <= 100):
            raise ValueError("Encashment percentage must be between 0 and 100")
        
        if self.probation_allocation is not None and self.probation_allocation < 0:
            raise ValueError("Probation allocation cannot be negative")
        
        # Validate accrual rate based on accrual type
        if self.accrual_type in [AccrualType.MONTHLY, AccrualType.QUARTERLY]:
            if self.accrual_rate is None or self.accrual_rate <= 0:
                raise ValueError(f"Accrual rate is required and must be positive for {self.accrual_type.value} accrual")
        
        if self.gender_specific and self.gender_specific not in ['male', 'female']:
            raise ValueError("Gender specific must be 'male', 'female', or None")
    
    @classmethod
    def create_standard_policy(
        cls,
        leave_type: LeaveType,
        annual_allocation: int,
        accrual_type: AccrualType = AccrualType.ANNUALLY
    ) -> 'LeavePolicy':
        """Create a standard leave policy with common defaults"""
        
        # Calculate accrual rate based on type
        accrual_rate = None
        if accrual_type == AccrualType.MONTHLY:
            accrual_rate = Decimal(str(annual_allocation / 12))
        elif accrual_type == AccrualType.QUARTERLY:
            accrual_rate = Decimal(str(annual_allocation / 4))
        
        return cls(
            leave_type=leave_type,
            annual_allocation=annual_allocation,
            accrual_type=accrual_type,
            accrual_rate=accrual_rate,
            max_carryover_days=min(5, annual_allocation // 2),  # Max 5 days or half allocation
            min_advance_notice_days=leave_type.get_typical_advance_notice_days(),
            max_continuous_days=leave_type.get_maximum_continuous_days(),
            requires_medical_certificate=leave_type.requires_medical_certificate()
        )
    
    @classmethod
    def create_casual_leave_policy(cls, annual_allocation: int = 12) -> 'LeavePolicy':
        """Create standard casual leave policy"""
        return cls.create_standard_policy(
            leave_type=LeaveType.casual_leave(),
            annual_allocation=annual_allocation,
            accrual_type=AccrualType.MONTHLY
        )
    
    @classmethod
    def create_sick_leave_policy(cls, annual_allocation: int = 12) -> 'LeavePolicy':
        """Create standard sick leave policy"""
        policy = cls.create_standard_policy(
            leave_type=LeaveType.sick_leave(),
            annual_allocation=annual_allocation,
            accrual_type=AccrualType.MONTHLY
        )
        
        # Override with sick leave specific rules
        return dataclass.replace(
            policy,
            min_advance_notice_days=0,  # No advance notice for sick leave
            auto_approve_threshold=3,  # Auto-approve up to 3 days
            medical_certificate_threshold=3,  # Medical cert required after 3 days
            max_carryover_days=annual_allocation  # Can carry over all sick leave
        )
    
    @classmethod
    def create_annual_leave_policy(cls, annual_allocation: int = 21) -> 'LeavePolicy':
        """Create standard annual leave policy"""
        policy = cls.create_standard_policy(
            leave_type=LeaveType.annual_leave(),
            annual_allocation=annual_allocation,
            accrual_type=AccrualType.MONTHLY
        )
        
        return dataclass.replace(
            policy,
            min_advance_notice_days=7,  # 1 week advance notice
            is_encashable=True,
            max_encashment_days=annual_allocation // 2  # Can encash half
        )
    
    @classmethod
    def create_maternity_leave_policy(cls, annual_allocation: int = 180) -> 'LeavePolicy':
        """Create standard maternity leave policy"""
        policy = cls.create_standard_policy(
            leave_type=LeaveType.maternity_leave(),
            annual_allocation=annual_allocation,
            accrual_type=AccrualType.IMMEDIATE
        )
        
        return dataclass.replace(
            policy,
            gender_specific='female',
            min_advance_notice_days=30,  # 1 month advance notice
            requires_medical_certificate=True,
            max_carryover_days=0,  # Cannot carry over
            is_encashable=False,
            available_during_probation=False
        )
    
    @classmethod
    def create_paternity_leave_policy(cls, annual_allocation: int = 15) -> 'LeavePolicy':
        """Create standard paternity leave policy"""
        policy = cls.create_standard_policy(
            leave_type=LeaveType.paternity_leave(),
            annual_allocation=annual_allocation,
            accrual_type=AccrualType.IMMEDIATE
        )
        
        return dataclass.replace(
            policy,
            gender_specific='male',
            min_advance_notice_days=30,  # 1 month advance notice
            requires_medical_certificate=True,
            max_carryover_days=0,  # Cannot carry over
            is_encashable=False
        )
    
    def calculate_accrued_days(self, months_completed: int) -> Decimal:
        """Calculate accrued leave days based on months completed"""
        
        if self.accrual_type == AccrualType.IMMEDIATE:
            return Decimal(str(self.annual_allocation))
        
        elif self.accrual_type == AccrualType.ANNUALLY:
            # All allocated at year end or pro-rated
            return Decimal(str(self.annual_allocation * months_completed / 12))
        
        elif self.accrual_type == AccrualType.MONTHLY:
            return self.accrual_rate * months_completed
        
        elif self.accrual_type == AccrualType.QUARTERLY:
            quarters_completed = months_completed // 3
            return self.accrual_rate * quarters_completed
        
        else:  # AccrualType.NONE
            return Decimal('0')
    
    def is_applicable_for_employee(
        self, 
        employee_gender: Optional[str] = None,
        employee_category: Optional[str] = None,
        is_on_probation: bool = False
    ) -> bool:
        """Check if policy is applicable for employee"""
        
        # Check probation eligibility
        if is_on_probation and not self.available_during_probation:
            return False
        
        # Check gender eligibility
        if self.gender_specific and employee_gender != self.gender_specific:
            return False
        
        # Check category eligibility
        if (self.employee_category_specific and 
            employee_category not in self.employee_category_specific):
            return False
        
        return True
    
    def get_effective_allocation(self, is_on_probation: bool = False) -> int:
        """Get effective allocation based on employee status"""
        if is_on_probation and self.probation_allocation is not None:
            return self.probation_allocation
        return self.annual_allocation
    
    def can_auto_approve(self, requested_days: int) -> bool:
        """Check if leave can be auto-approved"""
        if not self.requires_approval:
            return True
        
        if self.auto_approve_threshold is None:
            return False
        
        return requested_days <= self.auto_approve_threshold
    
    def requires_medical_cert_for_days(self, requested_days: int) -> bool:
        """Check if medical certificate is required for requested days"""
        if not self.requires_medical_certificate:
            return False
        
        if self.medical_certificate_threshold is None:
            return True  # Always required if policy says so
        
        return requested_days > self.medical_certificate_threshold
    
    def validate_application_days(self, requested_days: int) -> List[str]:
        """Validate requested days against policy rules"""
        errors = []
        
        if requested_days < self.min_application_days:
            errors.append(f"Minimum {self.min_application_days} day(s) must be applied")
        
        if self.max_continuous_days and requested_days > self.max_continuous_days:
            errors.append(f"Maximum {self.max_continuous_days} continuous days allowed")
        
        return errors
    
    def calculate_encashment_amount(
        self, 
        days_to_encash: int, 
        daily_salary: Decimal
    ) -> Decimal:
        """Calculate encashment amount"""
        if not self.is_encashable or days_to_encash > self.max_encashment_days:
            return Decimal('0')
        
        base_amount = daily_salary * days_to_encash
        return base_amount * (self.encashment_percentage / 100)
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.leave_type.name} Policy ({self.annual_allocation} days/year)"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"LeavePolicy(leave_type={self.leave_type}, annual_allocation={self.annual_allocation})"


# Import dataclass.replace for policy modifications
import dataclasses
dataclass = dataclasses 