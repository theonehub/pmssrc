"""
Attendance Status Value Object
Defines the various states an attendance record can have
"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass


class AttendanceStatusType(Enum):
    """Enumeration of attendance status types"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    WORK_FROM_HOME = "work_from_home"
    ON_LEAVE = "on_leave"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"


class AttendanceMarkingType(Enum):
    """Enumeration of how attendance was marked"""
    MANUAL = "manual"
    BIOMETRIC = "biometric"
    MOBILE_APP = "mobile_app"
    WEB_APP = "web_app"
    SYSTEM_AUTO = "system_auto"
    ADMIN_OVERRIDE = "admin_override"


@dataclass(frozen=True)
class AttendanceStatus:
    """
    Value object representing attendance status.
    
    Follows SOLID principles:
    - SRP: Encapsulates attendance status logic
    - OCP: Extensible through new status types
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for status operations
    - DIP: Depends on abstractions (enums)
    """
    
    status: AttendanceStatusType
    marking_type: AttendanceMarkingType
    is_regularized: bool = False
    regularization_reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate the attendance status"""
        if not isinstance(self.status, AttendanceStatusType):
            raise ValueError("Invalid attendance status type")
        
        if not isinstance(self.marking_type, AttendanceMarkingType):
            raise ValueError("Invalid marking type")
        
        if self.is_regularized and not self.regularization_reason:
            raise ValueError("Regularization reason is required when attendance is regularized")
        
        if not self.is_regularized and self.regularization_reason:
            raise ValueError("Regularization reason should not be provided when attendance is not regularized")
    
    def is_present(self) -> bool:
        """Check if the attendance status indicates presence"""
        return self.status in [
            AttendanceStatusType.PRESENT,
            AttendanceStatusType.LATE,
            AttendanceStatusType.HALF_DAY,
            AttendanceStatusType.WORK_FROM_HOME
        ]
    
    def is_absent(self) -> bool:
        """Check if the attendance status indicates absence"""
        return self.status == AttendanceStatusType.ABSENT
    
    def is_on_leave(self) -> bool:
        """Check if the attendance status indicates leave"""
        return self.status == AttendanceStatusType.ON_LEAVE
    
    def is_holiday(self) -> bool:
        """Check if the attendance status indicates holiday"""
        return self.status in [AttendanceStatusType.HOLIDAY, AttendanceStatusType.WEEKEND]
    
    def requires_working_hours(self) -> bool:
        """Check if this status requires working hours tracking"""
        return self.status in [
            AttendanceStatusType.PRESENT,
            AttendanceStatusType.LATE,
            AttendanceStatusType.HALF_DAY,
            AttendanceStatusType.WORK_FROM_HOME
        ]
    
    def is_manually_marked(self) -> bool:
        """Check if attendance was manually marked"""
        return self.marking_type in [
            AttendanceMarkingType.MANUAL,
            AttendanceMarkingType.ADMIN_OVERRIDE
        ]
    
    def is_system_generated(self) -> bool:
        """Check if attendance was system generated"""
        return self.marking_type == AttendanceMarkingType.SYSTEM_AUTO
    
    def can_be_regularized(self) -> bool:
        """Check if this attendance status can be regularized"""
        return self.status in [
            AttendanceStatusType.ABSENT,
            AttendanceStatusType.LATE,
            AttendanceStatusType.HALF_DAY
        ] and not self.is_regularized
    
    def with_regularization(self, reason: str) -> 'AttendanceStatus':
        """Create a new attendance status with regularization"""
        if not self.can_be_regularized():
            raise ValueError("This attendance status cannot be regularized")
        
        return AttendanceStatus(
            status=self.status,
            marking_type=self.marking_type,
            is_regularized=True,
            regularization_reason=reason
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "status": self.status.value,
            "marking_type": self.marking_type.value,
            "is_regularized": self.is_regularized,
            "regularization_reason": self.regularization_reason
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AttendanceStatus':
        """Create from dictionary representation"""
        return cls(
            status=AttendanceStatusType(data["status"]),
            marking_type=AttendanceMarkingType(data["marking_type"]),
            is_regularized=data.get("is_regularized", False),
            regularization_reason=data.get("regularization_reason")
        )
    
    @classmethod
    def create_present(cls, marking_type: AttendanceMarkingType = AttendanceMarkingType.MANUAL) -> 'AttendanceStatus':
        """Create a present attendance status"""
        return cls(
            status=AttendanceStatusType.PRESENT,
            marking_type=marking_type
        )
    
    @classmethod
    def create_absent(cls, marking_type: AttendanceMarkingType = AttendanceMarkingType.SYSTEM_AUTO) -> 'AttendanceStatus':
        """Create an absent attendance status"""
        return cls(
            status=AttendanceStatusType.ABSENT,
            marking_type=marking_type
        )
    
    @classmethod
    def create_late(cls, marking_type: AttendanceMarkingType = AttendanceMarkingType.MANUAL) -> 'AttendanceStatus':
        """Create a late attendance status"""
        return cls(
            status=AttendanceStatusType.LATE,
            marking_type=marking_type
        )
    
    @classmethod
    def create_work_from_home(cls, marking_type: AttendanceMarkingType = AttendanceMarkingType.MANUAL) -> 'AttendanceStatus':
        """Create a work from home attendance status"""
        return cls(
            status=AttendanceStatusType.WORK_FROM_HOME,
            marking_type=marking_type
        )
    
    @classmethod
    def create_on_leave(cls, marking_type: AttendanceMarkingType = AttendanceMarkingType.SYSTEM_AUTO) -> 'AttendanceStatus':
        """Create an on leave attendance status"""
        return cls(
            status=AttendanceStatusType.ON_LEAVE,
            marking_type=marking_type
        )
    
    @classmethod
    def create_holiday(cls, marking_type: AttendanceMarkingType = AttendanceMarkingType.SYSTEM_AUTO) -> 'AttendanceStatus':
        """Create a holiday attendance status"""
        return cls(
            status=AttendanceStatusType.HOLIDAY,
            marking_type=marking_type
        ) 