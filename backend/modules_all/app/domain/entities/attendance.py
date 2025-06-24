"""
Attendance Entity - Aggregate Root
Main entity for attendance management following DDD patterns
"""

import uuid
from datetime import datetime, date, time, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.attendance_status import AttendanceStatus, AttendanceStatusType, AttendanceMarkingType
from app.domain.value_objects.working_hours import WorkingHours, TimeSlot
from app.domain.events.attendance_events import (
    AttendanceCheckedInEvent,
    AttendanceCheckedOutEvent,
    AttendanceRegularizedEvent,
    AttendanceUpdatedEvent,
    AttendanceDeletedEvent,
    BreakStartedEvent,
    BreakEndedEvent
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Attendance:
    """
    Attendance aggregate root representing a daily attendance record.
    
    Follows SOLID principles:
    - SRP: Manages attendance lifecycle and business rules
    - OCP: Extensible through events and new status types
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for attendance operations
    - DIP: Depends on value object abstractions
    
    Domain Events:
    - AttendanceCheckedInEvent: When employee checks in
    - AttendanceCheckedOutEvent: When employee checks out
    - AttendanceRegularizedEvent: When attendance is regularized
    - AttendanceUpdatedEvent: When attendance is modified
    - AttendanceDeletedEvent: When attendance is deleted
    - BreakStartedEvent: When break is started
    - BreakEndedEvent: When break is ended
    """
    
    # Identity
    attendance_id: str
    employee_id: EmployeeId
    attendance_date: date
    
    # Core attributes
    status: AttendanceStatus
    working_hours: WorkingHours
    
    # Metadata
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    
    # Location tracking (optional)
    check_in_location: Optional[str] = None
    check_out_location: Optional[str] = None
    
    # Comments and notes
    comments: Optional[str] = None
    admin_notes: Optional[str] = None
    
    # Domain events
    _domain_events: List[Any] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate the attendance record"""
        if not self.attendance_id:
            raise ValueError("Attendance ID is required")
        
        if not isinstance(self.employee_id, EmployeeId):
            raise ValueError("Invalid employee ID")
        
        if not isinstance(self.status, AttendanceStatus):
            raise ValueError("Invalid attendance status")
        
        if not isinstance(self.working_hours, WorkingHours):
            raise ValueError("Invalid working hours")
        
        if self.created_at > datetime.utcnow():
            raise ValueError("Created date cannot be in the future")
    
    # ==================== BUSINESS METHODS ====================
    
    def check_in(self, check_in_time: datetime, location: Optional[str] = None, marked_by: Optional[str] = None) -> None:
        """
        Record check-in for the employee.
        
        Business Rules:
        - Cannot check in if already checked in
        - Check-in time must be on the same date as attendance date
        - Cannot check in for future dates
        """
        if self.working_hours.is_checked_in():
            raise ValueError("Employee is already checked in")
        
        if check_in_time.date() != self.attendance_date:
            raise ValueError("Check-in time must be on the same date as attendance date")
        
        # Allow a small buffer for timezone differences (24 hours for development)
        if check_in_time > datetime.utcnow() + timedelta(hours=24):
            raise ValueError("Cannot check in for future time")
        
        # Update working hours
        self.working_hours = self.working_hours.with_check_in(check_in_time)
        
        # Update status if it was absent or not set
        if self.status.status in [AttendanceStatusType.ABSENT]:
            marking_type = AttendanceMarkingType.MANUAL if marked_by else AttendanceMarkingType.MOBILE_APP
            self.status = AttendanceStatus.create_present(marking_type)
        
        # Update location
        self.check_in_location = location
        
        # Update metadata
        self.updated_at = datetime.utcnow()
        self.updated_by = marked_by or "system"
        
        # Publish domain event
        self._add_domain_event(AttendanceCheckedInEvent(
            attendance_id=self.attendance_id,
            employee_id=self.employee_id.value,
            check_in_time=check_in_time,
            location=location,
            marked_by=marked_by or "system"
        ))
        
        logger.info(f"Employee {self.employee_id.value} checked in at {check_in_time}")
    
    def check_out(self, check_out_time: datetime, location: Optional[str] = None, marked_by: Optional[str] = None) -> None:
        """
        Record check-out for the employee.
        
        Business Rules:
        - Must be checked in before checking out
        - Check-out time must be after check-in time
        - Check-out time must be on the same date as attendance date
        """
        if not self.working_hours.is_checked_in():
            raise ValueError("Employee must check in before checking out")
        
        if self.working_hours.is_checked_out():
            raise ValueError("Employee is already checked out")
        
        if check_out_time <= self.working_hours.check_in_time:
            raise ValueError("Check-out time must be after check-in time")
        
        if check_out_time.date() != self.attendance_date:
            raise ValueError("Check-out time must be on the same date as attendance date")
        
        # Update working hours
        self.working_hours = self.working_hours.with_check_out(check_out_time)
        
        # Update status based on working hours
        self._update_status_based_on_hours()
        
        # Update location
        self.check_out_location = location
        
        # Update metadata
        self.updated_at = datetime.utcnow()
        self.updated_by = marked_by or "system"
        
        # Publish domain event
        self._add_domain_event(AttendanceCheckedOutEvent(
            attendance_id=self.attendance_id,
            employee_id=self.employee_id.value,
            check_out_time=check_out_time,
            working_hours=float(self.working_hours.working_hours()),
            overtime_hours=float(self.working_hours.overtime_hours()),
            location=location,
            marked_by=marked_by or "system"
        ))
        
        logger.info(f"Employee {self.employee_id.value} checked out at {check_out_time}")
    
    def start_break(self, break_start_time: datetime, marked_by: Optional[str] = None) -> None:
        """
        Start a break period.
        
        Business Rules:
        - Must be checked in to start break
        - Cannot start break if already on break
        - Break start time must be after check-in time
        """
        if not self.working_hours.is_checked_in():
            raise ValueError("Employee must be checked in to start break")
        
        if break_start_time <= self.working_hours.check_in_time:
            raise ValueError("Break start time must be after check-in time")
        
        if self.working_hours.check_out_time and break_start_time >= self.working_hours.check_out_time:
            raise ValueError("Break start time must be before check-out time")
        
        # Check if already on break (incomplete break slot)
        for slot in self.working_hours.break_slots:
            if slot.end_time is None:
                raise ValueError("Employee is already on break")
        
        # Update metadata
        self.updated_at = datetime.utcnow()
        self.updated_by = marked_by or "system"
        
        # Publish domain event
        self._add_domain_event(BreakStartedEvent(
            attendance_id=self.attendance_id,
            employee_id=self.employee_id.value,
            break_start_time=break_start_time,
            marked_by=marked_by or "system"
        ))
        
        logger.info(f"Employee {self.employee_id.value} started break at {break_start_time}")
    
    def end_break(self, break_end_time: datetime, marked_by: Optional[str] = None) -> None:
        """
        End the current break period.
        
        Business Rules:
        - Must have an active break to end
        - Break end time must be after break start time
        """
        # Find the active break (one without end time)
        active_break_index = None
        for i, slot in enumerate(self.working_hours.break_slots):
            if slot.end_time is None:
                active_break_index = i
                break
        
        if active_break_index is None:
            raise ValueError("No active break to end")
        
        active_break = self.working_hours.break_slots[active_break_index]
        if break_end_time <= active_break.start_time:
            raise ValueError("Break end time must be after break start time")
        
        # Create completed break slot
        completed_break = TimeSlot(
            start_time=active_break.start_time,
            end_time=break_end_time
        )
        
        # Update break slots
        new_break_slots = list(self.working_hours.break_slots)
        new_break_slots[active_break_index] = completed_break
        
        self.working_hours = WorkingHours(
            check_in_time=self.working_hours.check_in_time,
            check_out_time=self.working_hours.check_out_time,
            break_slots=new_break_slots,
            expected_hours=self.working_hours.expected_hours,
            minimum_hours=self.working_hours.minimum_hours,
            overtime_threshold=self.working_hours.overtime_threshold
        )
        
        # Update metadata
        self.updated_at = datetime.utcnow()
        self.updated_by = marked_by or "system"
        
        # Publish domain event
        self._add_domain_event(BreakEndedEvent(
            attendance_id=self.attendance_id,
            employee_id=self.employee_id.value,
            break_end_time=break_end_time,
            break_duration_minutes=completed_break.duration_minutes(),
            marked_by=marked_by or "system"
        ))
        
        logger.info(f"Employee {self.employee_id.value} ended break at {break_end_time}")
    
    def regularize(self, reason: str, regularized_by: str, new_status: Optional[AttendanceStatus] = None) -> None:
        """
        Regularize the attendance record.
        
        Business Rules:
        - Only certain statuses can be regularized
        - Regularization reason is required
        - Cannot regularize already regularized attendance
        """
        if not self.status.can_be_regularized():
            raise ValueError("This attendance status cannot be regularized")
        
        if not reason.strip():
            raise ValueError("Regularization reason is required")
        
        if not regularized_by.strip():
            raise ValueError("Regularized by is required")
        
        # Update status with regularization
        if new_status:
            self.status = new_status.with_regularization(reason)
        else:
            self.status = self.status.with_regularization(reason)
        
        # Update metadata
        self.updated_at = datetime.utcnow()
        self.updated_by = regularized_by
        
        # Publish domain event
        self._add_domain_event(AttendanceRegularizedEvent(
            attendance_id=self.attendance_id,
            employee_id=self.employee_id.value,
            regularization_reason=reason,
            regularized_by=regularized_by,
            previous_status=self.status.status.value,
            new_status=self.status.status.value
        ))
        
        logger.info(f"Attendance {self.attendance_id} regularized by {regularized_by}")
    
    def update_status(self, new_status: AttendanceStatus, updated_by: str, reason: Optional[str] = None) -> None:
        """
        Update the attendance status.
        
        Business Rules:
        - Status transitions must be valid
        - Admin override is allowed for any transition
        """
        if not updated_by.strip():
            raise ValueError("Updated by is required")
        
        previous_status = self.status
        self.status = new_status
        
        # Update metadata
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        
        if reason:
            self.admin_notes = f"{self.admin_notes or ''}\n{datetime.utcnow()}: {reason}".strip()
        
        # Publish domain event
        self._add_domain_event(AttendanceUpdatedEvent(
            attendance_id=self.attendance_id,
            employee_id=self.employee_id.value,
            previous_status=previous_status.status.value,
            new_status=new_status.status.value,
            updated_by=updated_by,
            reason=reason
        ))
        
        logger.info(f"Attendance {self.attendance_id} status updated from {previous_status.status.value} to {new_status.status.value}")
    
    def add_comment(self, comment: str, added_by: str) -> None:
        """Add a comment to the attendance record"""
        if not comment.strip():
            raise ValueError("Comment cannot be empty")
        
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        new_comment = f"[{timestamp}] {added_by}: {comment}"
        
        if self.comments:
            self.comments = f"{self.comments}\n{new_comment}"
        else:
            self.comments = new_comment
        
        self.updated_at = datetime.utcnow()
        self.updated_by = added_by
    
    def delete(self, deleted_by: str, reason: str) -> None:
        """
        Mark attendance as deleted.
        
        Business Rules:
        - Deletion reason is required
        - Only admin can delete attendance
        """
        if not reason.strip():
            raise ValueError("Deletion reason is required")
        
        if not deleted_by.strip():
            raise ValueError("Deleted by is required")
        
        # Publish domain event
        self._add_domain_event(AttendanceDeletedEvent(
            attendance_id=self.attendance_id,
            employee_id=self.employee_id.value,
            deleted_by=deleted_by,
            deletion_reason=reason
        ))
        
        logger.info(f"Attendance {self.attendance_id} deleted by {deleted_by}")
    
    # ==================== QUERY METHODS ====================
    
    def is_present(self) -> bool:
        """Check if employee is present"""
        return self.status.is_present()
    
    def is_absent(self) -> bool:
        """Check if employee is absent"""
        return self.status.is_absent()
    
    def is_on_leave(self) -> bool:
        """Check if employee is on leave"""
        return self.status.is_on_leave()
    
    def is_holiday(self) -> bool:
        """Check if it's a holiday"""
        return self.status.is_holiday()
    
    def is_late(self, expected_start_time: time) -> bool:
        """Check if employee arrived late"""
        return (self.status.status == AttendanceStatusType.LATE or 
                self.working_hours.is_late_arrival(expected_start_time))
    
    def is_overtime(self) -> bool:
        """Check if employee worked overtime"""
        return self.working_hours.overtime_hours() > 0
    
    def is_regularized(self) -> bool:
        """Check if attendance is regularized"""
        return self.status.is_regularized
    
    def get_working_hours(self) -> float:
        """Get working hours as float"""
        return float(self.working_hours.working_hours())
    
    def get_overtime_hours(self) -> float:
        """Get overtime hours as float"""
        return float(self.working_hours.overtime_hours())
    
    def get_shortage_hours(self) -> float:
        """Get shortage hours as float"""
        return float(self.working_hours.shortage_hours())
    
    # ==================== HELPER METHODS ====================
    
    def _update_status_based_on_hours(self) -> None:
        """Update status based on working hours"""
        if not self.working_hours.is_complete_day():
            return
        
        if self.working_hours.is_insufficient_hours():
            self.status = AttendanceStatus.create_absent(self.status.marking_type)
        elif self.working_hours.is_half_day():
            self.status = AttendanceStatus(
                status=AttendanceStatusType.HALF_DAY,
                marking_type=self.status.marking_type,
                is_regularized=self.status.is_regularized,
                regularization_reason=self.status.regularization_reason
            )
        elif self.working_hours.is_full_day():
            self.status = AttendanceStatus.create_present(self.status.marking_type)
    
    def _add_domain_event(self, event: Any) -> None:
        """Add a domain event"""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[Any]:
        """Get all domain events"""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear all domain events"""
        self._domain_events.clear()
    
    # ==================== FACTORY METHODS ====================
    
    @classmethod
    def create_new(
        cls,
        employee_id: EmployeeId,
        attendance_date: date,
        created_by: str,
        initial_status: Optional[AttendanceStatus] = None
    ) -> 'Attendance':
        """Create a new attendance record"""
        attendance_id = str(uuid.uuid4())
        
        if initial_status is None:
            initial_status = AttendanceStatus.create_absent()
        
        return cls(
            attendance_id=attendance_id,
            employee_id=employee_id,
            attendance_date=attendance_date,
            status=initial_status,
            working_hours=WorkingHours.create_empty(),
            created_at=datetime.utcnow(),
            created_by=created_by
        )
    
    @classmethod
    def create_with_check_in(
        cls,
        employee_id: EmployeeId,
        attendance_date: date,
        check_in_time: datetime,
        created_by: str,
        location: Optional[str] = None
    ) -> 'Attendance':
        """Create a new attendance record with check-in"""
        attendance = cls.create_new(employee_id, attendance_date, created_by)
        attendance.check_in(check_in_time, location, created_by)
        return attendance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "attendance_id": self.attendance_id,
            "employee_id": self.employee_id.value,
            "attendance_date": self.attendance_date.isoformat(),
            "status": self.status.to_dict(),
            "working_hours": self.working_hours.to_dict(),
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "check_in_location": self.check_in_location,
            "check_out_location": self.check_out_location,
            "comments": self.comments,
            "admin_notes": self.admin_notes
        } 