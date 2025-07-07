"""
Employee Leave Entity
Domain entity representing employee leave requests
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from app.domain.entities.base_entity import BaseEntity

@dataclass
class EmployeeLeave(BaseEntity):
    """
    Employee Leave domain entity.
    
    Represents a leave request made by an employee. Follows DDD principles
    with rich domain behavior and encapsulated business rules.
    """
    
    # Identity
    leave_id: str
    employee_id: str
    employee_name: str
    employee_email: str
    organisation_id: str
    
    # Leave details using leave_name instead of LeaveType
    leave_name: str  # e.g., "Casual Leave", "Sick Leave"
    start_date: date
    end_date: date
    
    # Optional fields with defaults
    reason: Optional[str] = None
    status: str = "pending"  # pending, approved, rejected, cancelled
    applied_days: Optional[int] = None
    approved_days: Optional[int] = None
    
    # Metadata
    applied_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    # Business fields
    is_half_day: bool = False
    is_compensatory: bool = False
    compensatory_work_date: Optional[date] = None
    
    # Audit fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        """Initialize the entity after dataclass creation"""
        if not self.leave_id:
            self.leave_id = str(uuid.uuid4())
        
        # Initialize applied_days if not provided
        if self.applied_days is None:
            self.applied_days = self.calculate_leave_days()
    
    @classmethod
    def create(
        cls,
        employee_id: str,
        employee_name: str,
        employee_email: str,
        organisation_id: str,
        leave_name: str,
        start_date: date,
        end_date: date,
        reason: Optional[str] = None,
        is_half_day: bool = False,
        is_compensatory: bool = False,
        compensatory_work_date: Optional[date] = None,
        created_by: Optional[str] = None
    ) -> 'EmployeeLeave':
        """
        Factory method to create a new employee leave.
        
        Args:
            employee_id: ID of the employee
            employee_name: Name of the employee
            employee_email: Email of the employee
            organisation_id: ID of the organisation
            leave_name: Name of the leave type
            start_date: Leave start date
            end_date: Leave end date
            reason: Reason for leave
            is_half_day: Whether it's a half day leave
            is_compensatory: Whether it's compensatory leave
            compensatory_work_date: Date of compensatory work
            created_by: Who created the leave
            
        Returns:
            New EmployeeLeave instance
        """
        return cls(
            leave_id=str(uuid.uuid4()),
            employee_id=employee_id,
            employee_name=employee_name,
            employee_email=employee_email,
            organisation_id=organisation_id,
            leave_name=leave_name,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            is_half_day=is_half_day,
            is_compensatory=is_compensatory,
            compensatory_work_date=compensatory_work_date,
            created_by=created_by
        )
    
    @classmethod
    def from_legacy_data(
        cls,
        legacy_leave_name: str,
        employee_id: str,
        employee_name: str,
        employee_email: str,
        organisation_id: str,
        start_date: date,
        end_date: date,
        reason: Optional[str] = None,
        status: str = "approved"
    ) -> 'EmployeeLeave':
        """
        Create EmployeeLeave from legacy data.
        
        This method helps in migrating from legacy systems where
        leave data might be stored differently.
        """
        
        return cls(
            leave_id=str(uuid.uuid4()),
            employee_id=employee_id,
            employee_name=employee_name,
            employee_email=employee_email,
            organisation_id=organisation_id,
            leave_name=legacy_leave_name,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status=status,
            applied_days=None,  # Will be calculated in __post_init__
            created_by="migration_service"
        )
    
    def calculate_leave_days(self) -> int:
        """Calculate the number of leave days"""
        if self.is_half_day:
            return 0.5
        
        # Simple calculation - in real implementation, you'd exclude weekends and holidays
        delta = self.end_date - self.start_date
        return delta.days + 1
    
    def approve(self, approved_by: str, approved_days: Optional[int] = None) -> None:
        """
        Approve the leave request.
        
        Args:
            approved_by: Who approved the leave
            approved_days: Number of days approved (defaults to applied_days)
        """
        if self.status != "pending":
            raise ValueError(f"Cannot approve leave in status: {self.status}")
        
        self.status = "approved"
        self.approved_at = datetime.utcnow()
        self.approved_by = approved_by
        self.approved_days = approved_days or self.applied_days
        self.updated_at = datetime.utcnow()
        self.updated_by = approved_by
        
        # Publish domain event
        from app.domain.events.leave_events import EmployeeLeaveApprovedEvent
        self.add_domain_event(EmployeeLeaveApprovedEvent(
            employee_id=self.employee_id,
            leave_id=self.leave_id,
            leave_name=self.leave_name,
            approved_by=approved_by,
            approved_days=self.approved_days
        ))
    
    def reject(self, rejected_by: str, rejection_reason: str) -> None:
        """
        Reject the leave request.
        
        Args:
            rejected_by: Who rejected the leave
            rejection_reason: Reason for rejection
        """
        if self.status != "pending":
            raise ValueError(f"Cannot reject leave in status: {self.status}")
        
        self.status = "rejected"
        self.rejected_at = datetime.utcnow()
        self.rejected_by = rejected_by
        self.rejection_reason = rejection_reason
        self.updated_at = datetime.utcnow()
        self.updated_by = rejected_by
        
        # Publish domain event
        from app.domain.events.leave_events import EmployeeLeaveRejectedEvent
        self.add_domain_event(EmployeeLeaveRejectedEvent(
            employee_id=self.employee_id,
            leave_id=self.leave_id,
            leave_name=self.leave_name,
            rejected_by=rejected_by,
            rejection_reason=rejection_reason
        ))
    
    def cancel(self, cancelled_by: str, cancellation_reason: Optional[str] = None) -> None:
        """
        Cancel the leave request.
        
        Args:
            cancelled_by: Who cancelled the leave
            cancellation_reason: Reason for cancellation
        """
        if self.status in ["rejected", "cancelled"]:
            raise ValueError(f"Cannot cancel leave in status: {self.status}")
        
        self.status = "cancelled"
        self.updated_at = datetime.utcnow()
        self.updated_by = cancelled_by
        
        # Store cancellation reason in the general reason field if provided
        if cancellation_reason:
            if self.reason:
                self.reason += f" [Cancelled: {cancellation_reason}]"
            else:
                self.reason = f"Cancelled: {cancellation_reason}"
        
        # Publish domain event
        from app.domain.events.leave_events import EmployeeLeaveCancelledEvent
        self.add_domain_event(EmployeeLeaveCancelledEvent(
            employee_id=self.employee_id,
            leave_id=self.leave_id,
            leave_name=self.leave_name,
            cancelled_by=cancelled_by,
            cancellation_reason=cancellation_reason
        ))
    
    def is_pending(self) -> bool:
        """Check if leave is pending approval"""
        return self.status == "pending"
    
    def is_approved(self) -> bool:
        """Check if leave is approved"""
        return self.status == "approved"
    
    def is_rejected(self) -> bool:
        """Check if leave is rejected"""
        return self.status == "rejected"
    
    def is_cancelled(self) -> bool:
        """Check if leave is cancelled"""
        return self.status == "cancelled"
    
    def is_active(self) -> bool:
        """Check if leave is currently active (approved and not past)"""
        return self.is_approved() and self.end_date >= date.today()
    
    def is_past(self) -> bool:
        """Check if leave is in the past"""
        return self.end_date < date.today()
    
    def is_future(self) -> bool:
        """Check if leave is in the future"""
        return self.start_date > date.today()
    
    def is_current(self) -> bool:
        """Check if leave is currently ongoing"""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    def get_duration_display(self) -> str:
        """Get human-readable duration"""
        if self.is_half_day:
            return "Half Day"
        
        days = self.applied_days or self.calculate_leave_days()
        if days == 1:
            return "1 Day"
        return f"{days} Days"
    
    def get_status_display(self) -> str:
        """Get human-readable status"""
        status_map = {
            "pending": "Pending Approval",
            "approved": "Approved",
            "rejected": "Rejected",
            "cancelled": "Cancelled"
        }
        return status_map.get(self.status, self.status.title())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "leave_id": self.leave_id,
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "employee_email": self.employee_email,
            "organisation_id": self.organisation_id,
            "leave_name": self.leave_name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "reason": self.reason,
            "status": self.status,
            "applied_days": self.applied_days,
            "approved_days": self.approved_days,
            "applied_at": self.applied_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "rejected_at": self.rejected_at.isoformat() if self.rejected_at else None,
            "rejected_by": self.rejected_by,
            "rejection_reason": self.rejection_reason,
            "is_half_day": self.is_half_day,
            "is_compensatory": self.is_compensatory,
            "compensatory_work_date": self.compensatory_work_date.isoformat() if self.compensatory_work_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }
    
    def validate(self) -> List[str]:
        """
        Validate the leave entity and return list of validation errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Basic field validation
        if not self.employee_id:
            errors.append("Employee ID is required")
        
        if not self.organisation_id:
            errors.append("Organisation ID is required")
        
        if not self.leave_name:
            errors.append("Leave name is required")
        
        # Date validation
        if not self.start_date:
            errors.append("Start date is required")
        
        if not self.end_date:
            errors.append("End date is required")
        
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors.append("Start date cannot be after end date")
        
        # Business rule validation
        if self.is_compensatory and not self.compensatory_work_date:
            errors.append("Compensatory work date is required for compensatory leave")
        
        if self.is_half_day and self.start_date != self.end_date:
            errors.append("Half day leave must be for a single date")
        
        return errors
    
    def __str__(self) -> str:
        """String representation"""
        return (
            f"EmployeeLeave(leave_id={self.leave_id}, "
            f"employee_id={self.employee_id}, "
            f"leave_name={self.leave_name}, "
            f"start_date={self.start_date}, "
            f"end_date={self.end_date}, "
            f"status={self.status})"
        ) 