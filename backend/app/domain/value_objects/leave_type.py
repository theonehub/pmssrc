"""
Leave Type Value Object
Immutable value object representing different types of company leaves
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class LeaveCategory(Enum):
    """Categories of leave types"""
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    CASUAL = "casual"
    EMERGENCY = "emergency"
    COMPENSATORY = "compensatory"
    SABBATICAL = "sabbatical"
    UNPAID = "unpaid"
    BEREAVEMENT = "bereavement"
    STUDY = "study"
    RELIGIOUS = "religious"


class AccrualType(Enum):
    """How leave is accrued"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    IMMEDIATE = "immediate"  # All allocated at once
    NONE = "none"  # No accrual, fixed allocation


@dataclass(frozen=True)
class LeaveType:
    """
    Leave type value object ensuring immutability and validation.
    
    Follows SOLID principles:
    - SRP: Only handles leave type representation and rules
    - OCP: Can be extended without modification
    - LSP: Can be substituted anywhere LeaveType is expected
    - ISP: Provides only leave type operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    code: str  # Unique identifier like "CL", "SL", "ML"
    name: str  # Display name like "Casual Leave", "Sick Leave"
    category: LeaveCategory
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate leave type on creation"""
        if not self.code or not self.code.strip():
            raise ValueError("Leave type code is required")
        
        if not self.name or not self.name.strip():
            raise ValueError("Leave type name is required")
        
        if len(self.code) > 10:
            raise ValueError("Leave type code cannot exceed 10 characters")
        
        if len(self.name) > 100:
            raise ValueError("Leave type name cannot exceed 100 characters")
        
        # Validate code format (alphanumeric, no spaces)
        if not self.code.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Leave type code can only contain alphanumeric characters, hyphens, and underscores")
    
    @classmethod
    def create(cls, code: str, name: str, category: LeaveCategory, description: Optional[str] = None) -> 'LeaveType':
        """Create leave type with validation"""
        return cls(
            code=code.strip().upper(),
            name=name.strip(),
            category=category,
            description=description.strip() if description else None
        )
    
    @classmethod
    def casual_leave(cls) -> 'LeaveType':
        """Create casual leave type"""
        return cls(
            code="CL",
            name="Casual Leave",
            category=LeaveCategory.CASUAL,
            description="Leave for personal reasons and emergencies"
        )
    
    @classmethod
    def sick_leave(cls) -> 'LeaveType':
        """Create sick leave type"""
        return cls(
            code="SL",
            name="Sick Leave",
            category=LeaveCategory.SICK,
            description="Leave for medical reasons and health issues"
        )
    
    @classmethod
    def annual_leave(cls) -> 'LeaveType':
        """Create annual leave type"""
        return cls(
            code="AL",
            name="Annual Leave",
            category=LeaveCategory.ANNUAL,
            description="Yearly vacation leave for rest and recreation"
        )
    
    @classmethod
    def maternity_leave(cls) -> 'LeaveType':
        """Create maternity leave type"""
        return cls(
            code="ML",
            name="Maternity Leave",
            category=LeaveCategory.MATERNITY,
            description="Leave for childbirth and post-natal care"
        )
    
    @classmethod
    def paternity_leave(cls) -> 'LeaveType':
        """Create paternity leave type"""
        return cls(
            code="PL",
            name="Paternity Leave",
            category=LeaveCategory.PATERNITY,
            description="Leave for fathers during childbirth"
        )
    
    def is_medical_leave(self) -> bool:
        """Check if this is a medical-related leave"""
        return self.category in [LeaveCategory.SICK, LeaveCategory.MATERNITY, LeaveCategory.PATERNITY]
    
    def is_planned_leave(self) -> bool:
        """Check if this is typically a planned leave"""
        return self.category in [LeaveCategory.ANNUAL, LeaveCategory.MATERNITY, LeaveCategory.PATERNITY, LeaveCategory.SABBATICAL, LeaveCategory.STUDY]
    
    def is_emergency_leave(self) -> bool:
        """Check if this is an emergency leave"""
        return self.category in [LeaveCategory.EMERGENCY, LeaveCategory.BEREAVEMENT, LeaveCategory.SICK]
    
    def requires_medical_certificate(self) -> bool:
        """Check if medical certificate is typically required"""
        return self.category in [LeaveCategory.SICK, LeaveCategory.MATERNITY, LeaveCategory.PATERNITY]
    
    def is_paid_leave(self) -> bool:
        """Check if this is typically a paid leave (default assumption)"""
        return self.category != LeaveCategory.UNPAID
    
    def get_typical_advance_notice_days(self) -> int:
        """Get typical advance notice required in days"""
        if self.category == LeaveCategory.ANNUAL:
            return 7  # 1 week notice
        elif self.category in [LeaveCategory.MATERNITY, LeaveCategory.PATERNITY]:
            return 30  # 1 month notice
        elif self.category == LeaveCategory.SABBATICAL:
            return 90  # 3 months notice
        elif self.category in [LeaveCategory.EMERGENCY, LeaveCategory.BEREAVEMENT, LeaveCategory.SICK]:
            return 0  # No advance notice required
        else:
            return 3  # 3 days default notice
    
    def get_maximum_continuous_days(self) -> Optional[int]:
        """Get maximum continuous days that can be taken (if applicable)"""
        if self.category == LeaveCategory.CASUAL:
            return 3  # Typically max 3 continuous casual leave days
        elif self.category == LeaveCategory.SICK:
            return 7  # Max 7 continuous sick days without medical certificate
        elif self.category == LeaveCategory.ANNUAL:
            return 15  # Max 15 continuous annual leave days
        else:
            return None  # No specific limit
    
    def format(self) -> str:
        """Format leave type for display"""
        return f"{self.code} - {self.name}"
    
    def __str__(self) -> str:
        """String representation"""
        return self.format()
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"LeaveType(code='{self.code}', name='{self.name}', category={self.category})"


# Predefined common leave types
COMMON_LEAVE_TYPES = {
    'CL': LeaveType.casual_leave(),
    'SL': LeaveType.sick_leave(),
    'AL': LeaveType.annual_leave(),
    'ML': LeaveType.maternity_leave(),
    'PL': LeaveType.paternity_leave(),
}


def get_leave_type_by_code(code: str) -> Optional[LeaveType]:
    """Get predefined leave type by code"""
    return COMMON_LEAVE_TYPES.get(code.upper())


def get_all_common_leave_types() -> List[LeaveType]:
    """Get all predefined common leave types"""
    return list(COMMON_LEAVE_TYPES.values()) 