"""
Employee Leave Domain Entity
Aggregate root for employee leave applications and management
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict
from datetime import datetime, date
from uuid import uuid4
from enum import Enum

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.leave_type import LeaveType
from app.domain.value_objects.date_range import DateRange
from app.domain.events.leave_events import (
    EmployeeLeaveApplied, EmployeeLeaveApproved, EmployeeLeaveRejected,
    EmployeeLeaveCancelled, EmployeeLeaveUpdated
)

# Define LeaveStatus as proper enum
class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass
class EmployeeLeave:
    """
    Employee Leave aggregate root following DDD principles.
    
    Follows SOLID principles:
    - SRP: Only handles employee leave application management
    - OCP: Can be extended with new leave types without modification
    - LSP: Can be substituted anywhere EmployeeLeave is expected
    - ISP: Provides focused leave application operations
    - DIP: Depends on abstractions (value objects, events)
    """
    
    # Identity
    leave_id: str
    employee_id: EmployeeId
    
    # Leave Details
    leave_type: LeaveType
    date_range: DateRange
    working_days_count: int
    reason: Optional[str] = None
    
    # Status and Approval
    status: LeaveStatus = LeaveStatus.PENDING
    applied_date: date = field(default_factory=date.today)
    approved_by: Optional[str] = None
    approved_date: Optional[date] = None
    approval_comments: Optional[str] = None
    
    # Employee Information (for convenience)
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Domain Events
    _domain_events: List = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Post initialization validation"""
        self._validate_employee_leave_data()
    
    @classmethod
    def create_new_leave_application(
        cls,
        employee_id: EmployeeId,
        leave_type: LeaveType,
        date_range: DateRange,
        working_days_count: int,
        reason: Optional[str] = None,
        employee_name: Optional[str] = None,
        employee_email: Optional[str] = None
    ) -> 'EmployeeLeave':
        """Factory method to create new employee leave application"""
        
        leave_id = str(uuid4())
        
        employee_leave = cls(
            leave_id=leave_id,
            employee_id=employee_id,
            leave_type=leave_type,
            date_range=date_range,
            working_days_count=working_days_count,
            reason=reason,
            employee_name=employee_name,
            employee_email=employee_email,
            created_by=str(employee_id)
        )
        
        # Raise domain event
        employee_leave._domain_events.append(
            EmployeeLeaveApplied(
                leave_application_id=leave_id,
                employee_id=employee_id,
                leave_type=leave_type,
                date_range=date_range,
                requested_days=working_days_count,
                reason=reason,
                occurred_at=datetime.utcnow()
            )
        )
        
        return employee_leave
    
    @classmethod
    def create_from_legacy_data(
        cls,
        leave_id: str,
        employee_id: str,
        leave_type_code: str,
        start_date: str,
        end_date: str,
        working_days_count: int,
        status: LeaveStatus,
        applied_date: str,
        reason: Optional[str] = None,
        approved_by: Optional[str] = None,
        approved_date: Optional[str] = None,
        employee_name: Optional[str] = None,
        employee_email: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ) -> 'EmployeeLeave':
        """Create employee leave from legacy data format"""
        
        from app.domain.value_objects.leave_type import LeaveCategory
        
        # Convert legacy data to domain objects
        employee_id = EmployeeId(employee_id)
        leave_type = LeaveType(
            code=leave_type_code,
            name=leave_type_code,  # In legacy, code and name might be same
            category=LeaveCategory.GENERAL,  # Default category
            description=f"{leave_type_code} leave"
        )
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        date_range = DateRange(start_date=start_dt, end_date=end_dt)
        
        applied_dt = datetime.strptime(applied_date, "%Y-%m-%d").date()
        approved_dt = None
        if approved_date:
            approved_dt = datetime.strptime(approved_date, "%Y-%m-%d").date()
        
        return cls(
            leave_id=leave_id,
            employee_id=employee_id,
            leave_type=leave_type,
            date_range=date_range,
            working_days_count=working_days_count,
            reason=reason,
            status=status,
            applied_date=applied_dt,
            approved_by=approved_by,
            approved_date=approved_dt,
            employee_name=employee_name,
            employee_email=employee_email,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow()
        )
    
    def approve(self, approved_by: str, comments: Optional[str] = None):
        """
        Approve the leave application.
        
        Business Rules:
        1. Leave must be in pending status
        2. Approver must be provided
        3. Approval date is set to current date
        """
        
        if self.status != LeaveStatus.PENDING:
            raise ValueError(f"Cannot approve leave in {self.status} status")
        
        if not approved_by or not approved_by.strip():
            raise ValueError("Approver is required")
        
        self.status = LeaveStatus.APPROVED
        self.approved_by = approved_by
        self.approved_date = date.today()
        self.approval_comments = comments
        self.updated_at = datetime.utcnow()
        self.updated_by = approved_by
        
        # Raise domain event
        self._domain_events.append(
            EmployeeLeaveApproved(
                leave_application_id=self.leave_id,
                employee_id=self.employee_id,
                leave_type=self.leave_type,
                date_range=self.date_range,
                approved_days=self.working_days_count,
                approved_by=approved_by,
                approval_comments=comments,
                occurred_at=datetime.utcnow()
            )
        )
    
    def reject(self, rejected_by: str, reason: str):
        """
        Reject the leave application.
        
        Business Rules:
        1. Leave must be in pending status
        2. Rejector and reason must be provided
        3. Rejection date is set to current date
        """
        
        if self.status != LeaveStatus.PENDING:
            raise ValueError(f"Cannot reject leave in {self.status} status")
        
        if not rejected_by or not rejected_by.strip():
            raise ValueError("Rejector is required")
        
        if not reason or not reason.strip():
            raise ValueError("Rejection reason is required")
        
        self.status = LeaveStatus.REJECTED
        self.approved_by = rejected_by
        self.approved_date = date.today()
        self.approval_comments = reason
        self.updated_at = datetime.utcnow()
        self.updated_by = rejected_by
        
        # Raise domain event
        self._domain_events.append(
            EmployeeLeaveRejected(
                leave_application_id=self.leave_id,
                employee_id=self.employee_id,
                leave_type=self.leave_type,
                date_range=self.date_range,
                rejected_by=rejected_by,
                rejection_reason=reason,
                occurred_at=datetime.utcnow()
            )
        )
    
    def cancel(self, cancelled_by: str, reason: Optional[str] = None):
        """
        Cancel the leave application.
        
        Business Rules:
        1. Leave must be in pending or approved status
        2. Cannot cancel if leave has already started
        3. Canceller must be provided
        """
        
        if self.status not in [LeaveStatus.PENDING, LeaveStatus.APPROVED]:
            raise ValueError(f"Cannot cancel leave in {self.status} status")
        
        if self.date_range.start_date <= date.today():
            raise ValueError("Cannot cancel leave that has already started")
        
        if not cancelled_by or not cancelled_by.strip():
            raise ValueError("Canceller is required")
        
        self.status = LeaveStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        self.updated_by = cancelled_by
        
        # Raise domain event
        self._domain_events.append(
            EmployeeLeaveCancelled(
                leave_application_id=self.leave_id,
                employee_id=self.employee_id,
                leave_type=self.leave_type,
                date_range=self.date_range,
                cancelled_by=cancelled_by,
                cancellation_reason=reason,
                occurred_at=datetime.utcnow()
            )
        )
    
    def update_details(
        self,
        new_date_range: Optional[DateRange] = None,
        new_working_days_count: Optional[int] = None,
        new_reason: Optional[str] = None,
        updated_by: str = None
    ):
        """
        Update leave application details.
        
        Business Rules:
        1. Leave must be in pending status
        2. Cannot update if leave has already started
        3. Must recalculate working days if dates change
        """
        
        if self.status != LeaveStatus.PENDING:
            raise ValueError(f"Cannot update leave in {self.status} status")
        
        if self.date_range.start_date <= date.today():
            raise ValueError("Cannot update leave that has already started")
        
        old_date_range = self.date_range
        old_working_days = self.working_days_count
        old_reason = self.reason
        
        if new_date_range:
            self.date_range = new_date_range
        
        if new_working_days_count is not None:
            self.working_days_count = new_working_days_count
        
        if new_reason is not None:
            self.reason = new_reason
        
        self.updated_at = datetime.utcnow()
        if updated_by:
            self.updated_by = updated_by
        
        # Raise domain event if there were changes
        if (new_date_range and new_date_range != old_date_range) or \
           (new_working_days_count is not None and new_working_days_count != old_working_days) or \
           (new_reason is not None and new_reason != old_reason):
            
            self._domain_events.append(
                EmployeeLeaveUpdated(
                    leave_application_id=self.leave_id,
                    employee_id=self.employee_id,
                    old_date_range=old_date_range,
                    new_date_range=self.date_range,
                    old_working_days=old_working_days,
                    new_working_days=self.working_days_count,
                    updated_by=updated_by or str(self.employee_id),
                    occurred_at=datetime.utcnow()
                )
            )
    
    def is_active(self) -> bool:
        """Check if leave is currently active (approved and within date range)"""
        if self.status != LeaveStatus.APPROVED:
            return False
        
        today = date.today()
        return self.date_range.start_date <= today <= self.date_range.end_date
    
    def is_future(self) -> bool:
        """Check if leave is in the future"""
        return self.date_range.start_date > date.today()
    
    def is_past(self) -> bool:
        """Check if leave is in the past"""
        return self.date_range.end_date < date.today()
    
    def can_be_modified(self) -> bool:
        """Check if leave can be modified"""
        return (
            self.status == LeaveStatus.PENDING and
            self.date_range.start_date > date.today()
        )
    
    def can_be_cancelled(self) -> bool:
        """Check if leave can be cancelled"""
        return (
            self.status in [LeaveStatus.PENDING, LeaveStatus.APPROVED] and
            self.date_range.start_date > date.today()
        )
    
    def overlaps_with(self, other_date_range: DateRange) -> bool:
        """Check if this leave overlaps with another date range"""
        return self.date_range.overlaps_with(other_date_range)
    
    def get_duration_in_days(self) -> int:
        """Get total duration in calendar days"""
        return self.date_range.get_duration_in_days()
    
    def get_working_days_in_month(self, month: int, year: int) -> int:
        """Get working days that fall within a specific month"""
        from datetime import datetime
        
        # Get month boundaries
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        # Find overlap with leave period
        overlap_start = max(self.date_range.start_date, month_start)
        overlap_end = min(self.date_range.end_date, month_end)
        
        if overlap_start > overlap_end:
            return 0
        
        # Calculate working days in overlap period
        # This is a simplified calculation - in real implementation,
        # you'd use the same working days calculation as in the service
        overlap_range = DateRange(start_date=overlap_start, end_date=overlap_end)
        return overlap_range.get_duration_in_days()  # Simplified
    
    def to_legacy_dict(self) -> Dict[str, Any]:
        """Convert to legacy dictionary format for backward compatibility"""
        return {
            "leave_id": self.leave_id,
            "employee_id": str(self.employee_id),
            "emp_name": self.employee_name,
            "emp_email": self.employee_email,
            "leave_name": self.leave_type.code,
            "start_date": self.date_range.start_date.strftime("%Y-%m-%d"),
            "end_date": self.date_range.end_date.strftime("%Y-%m-%d"),
            "leave_count": self.working_days_count,
            "status": self.status,
            "applied_date": self.applied_date.strftime("%Y-%m-%d"),
            "approved_by": self.approved_by,
            "approved_date": self.approved_date.strftime("%Y-%m-%d") if self.approved_date else None,
            "reason": self.reason,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def get_domain_events(self) -> List:
        """Get domain events for this aggregate"""
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """Clear domain events after processing"""
        self._domain_events.clear()
    
    def _validate_employee_leave_data(self):
        """Validate employee leave data"""
        
        if not self.leave_id:
            raise ValueError("Leave ID is required")
        
        if not self.employee_id:
            raise ValueError("Employee ID is required")
        
        if not self.leave_type:
            raise ValueError("Leave type is required")
        
        if not self.date_range:
            raise ValueError("Date range is required")
        
        if self.working_days_count < 0:
            raise ValueError("Working days count cannot be negative")
        
        if self.date_range.start_date > self.date_range.end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Validate status transitions
        if self.status not in [LeaveStatus.PENDING, LeaveStatus.APPROVED, 
                              LeaveStatus.REJECTED, LeaveStatus.CANCELLED]:
            raise ValueError(f"Invalid leave status: {self.status}")
    
    def __str__(self) -> str:
        """String representation"""
        return (
            f"EmployeeLeave(id={self.leave_id}, "
            f"employee={self.employee_id}, "
            f"type={self.leave_type.code}, "
            f"dates={self.date_range}, "
            f"status={self.status})"
        )
    
    def __eq__(self, other) -> bool:
        """Equality comparison based on leave ID"""
        if not isinstance(other, EmployeeLeave):
            return False
        return self.leave_id == other.leave_id
    
    def __hash__(self) -> int:
        """Hash based on leave ID"""
        return hash(self.leave_id) 