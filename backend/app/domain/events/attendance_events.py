"""
Attendance Domain Events
Events published by the attendance aggregate for system integration
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class AttendanceDomainEvent:
    """Base class for all attendance domain events"""
    event_id: str
    occurred_at: datetime
    attendance_id: str
    employee_id: str
    
    def __post_init__(self):
        """Validate base event properties"""
        if not self.event_id:
            raise ValueError("Event ID is required")
        if not self.attendance_id:
            raise ValueError("Attendance ID is required")
        if not self.employee_id:
            raise ValueError("Employee ID is required")


@dataclass(frozen=True)
class AttendanceCreatedEvent(AttendanceDomainEvent):
    """Event published when a new attendance record is created"""
    attendance_date: str  # ISO format date
    initial_status: str
    created_by: str


@dataclass(frozen=True)
class AttendanceCheckedInEvent(AttendanceDomainEvent):
    """Event published when an employee checks in"""
    check_in_time: datetime
    location: Optional[str] = None
    marked_by: str = "system"
    
    def __post_init__(self):
        """Validate check-in event"""
        super().__post_init__()
        if not self.check_in_time:
            raise ValueError("Check-in time is required")


@dataclass(frozen=True)
class AttendanceCheckedOutEvent(AttendanceDomainEvent):
    """Event published when an employee checks out"""
    check_out_time: datetime
    working_hours: float
    overtime_hours: float
    location: Optional[str] = None
    marked_by: str = "system"
    
    def __post_init__(self):
        """Validate check-out event"""
        super().__post_init__()
        if not self.check_out_time:
            raise ValueError("Check-out time is required")
        if self.working_hours < 0:
            raise ValueError("Working hours cannot be negative")
        if self.overtime_hours < 0:
            raise ValueError("Overtime hours cannot be negative")


@dataclass(frozen=True)
class BreakStartedEvent(AttendanceDomainEvent):
    """Event published when an employee starts a break"""
    break_start_time: datetime
    marked_by: str = "system"
    
    def __post_init__(self):
        """Validate break started event"""
        super().__post_init__()
        if not self.break_start_time:
            raise ValueError("Break start time is required")


@dataclass(frozen=True)
class BreakEndedEvent(AttendanceDomainEvent):
    """Event published when an employee ends a break"""
    break_end_time: datetime
    break_duration_minutes: int
    marked_by: str = "system"
    
    def __post_init__(self):
        """Validate break ended event"""
        super().__post_init__()
        if not self.break_end_time:
            raise ValueError("Break end time is required")
        if self.break_duration_minutes < 0:
            raise ValueError("Break duration cannot be negative")


@dataclass(frozen=True)
class AttendanceRegularizedEvent(AttendanceDomainEvent):
    """Event published when attendance is regularized"""
    regularization_reason: str
    regularized_by: str
    previous_status: str
    new_status: str
    
    def __post_init__(self):
        """Validate regularization event"""
        super().__post_init__()
        if not self.regularization_reason.strip():
            raise ValueError("Regularization reason is required")
        if not self.regularized_by.strip():
            raise ValueError("Regularized by is required")
        if not self.previous_status:
            raise ValueError("Previous status is required")
        if not self.new_status:
            raise ValueError("New status is required")


@dataclass(frozen=True)
class AttendanceUpdatedEvent(AttendanceDomainEvent):
    """Event published when attendance status is updated"""
    previous_status: str
    new_status: str
    updated_by: str
    reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate update event"""
        super().__post_init__()
        if not self.previous_status:
            raise ValueError("Previous status is required")
        if not self.new_status:
            raise ValueError("New status is required")
        if not self.updated_by.strip():
            raise ValueError("Updated by is required")


@dataclass(frozen=True)
class AttendanceDeletedEvent(AttendanceDomainEvent):
    """Event published when attendance is deleted"""
    deleted_by: str
    deletion_reason: str
    
    def __post_init__(self):
        """Validate deletion event"""
        super().__post_init__()
        if not self.deleted_by.strip():
            raise ValueError("Deleted by is required")
        if not self.deletion_reason.strip():
            raise ValueError("Deletion reason is required")


@dataclass(frozen=True)
class AttendanceLateArrivalEvent(AttendanceDomainEvent):
    """Event published when an employee arrives late"""
    expected_start_time: datetime
    actual_start_time: datetime
    late_minutes: int
    
    def __post_init__(self):
        """Validate late arrival event"""
        super().__post_init__()
        if not self.expected_start_time:
            raise ValueError("Expected start time is required")
        if not self.actual_start_time:
            raise ValueError("Actual start time is required")
        if self.late_minutes <= 0:
            raise ValueError("Late minutes must be positive")


@dataclass(frozen=True)
class AttendanceEarlyDepartureEvent(AttendanceDomainEvent):
    """Event published when an employee leaves early"""
    expected_end_time: datetime
    actual_end_time: datetime
    early_minutes: int
    
    def __post_init__(self):
        """Validate early departure event"""
        super().__post_init__()
        if not self.expected_end_time:
            raise ValueError("Expected end time is required")
        if not self.actual_end_time:
            raise ValueError("Actual end time is required")
        if self.early_minutes <= 0:
            raise ValueError("Early minutes must be positive")


@dataclass(frozen=True)
class AttendanceOvertimeEvent(AttendanceDomainEvent):
    """Event published when an employee works overtime"""
    overtime_hours: float
    total_working_hours: float
    overtime_threshold: float
    
    def __post_init__(self):
        """Validate overtime event"""
        super().__post_init__()
        if self.overtime_hours <= 0:
            raise ValueError("Overtime hours must be positive")
        if self.total_working_hours <= 0:
            raise ValueError("Total working hours must be positive")
        if self.overtime_threshold <= 0:
            raise ValueError("Overtime threshold must be positive")


@dataclass(frozen=True)
class AttendanceAbsentEvent(AttendanceDomainEvent):
    """Event published when an employee is marked absent"""
    absence_date: str  # ISO format date
    absence_reason: Optional[str] = None
    marked_by: str = "system"
    
    def __post_init__(self):
        """Validate absence event"""
        super().__post_init__()
        if not self.absence_date:
            raise ValueError("Absence date is required")


@dataclass(frozen=True)
class AttendanceHalfDayEvent(AttendanceDomainEvent):
    """Event published when an employee works half day"""
    working_hours: float
    minimum_hours_threshold: float
    full_day_threshold: float
    
    def __post_init__(self):
        """Validate half day event"""
        super().__post_init__()
        if self.working_hours <= 0:
            raise ValueError("Working hours must be positive")
        if self.minimum_hours_threshold <= 0:
            raise ValueError("Minimum hours threshold must be positive")
        if self.full_day_threshold <= 0:
            raise ValueError("Full day threshold must be positive")


@dataclass(frozen=True)
class AttendanceWorkFromHomeEvent(AttendanceDomainEvent):
    """Event published when an employee works from home"""
    wfh_date: str  # ISO format date
    marked_by: str
    reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate work from home event"""
        super().__post_init__()
        if not self.wfh_date:
            raise ValueError("WFH date is required")
        if not self.marked_by.strip():
            raise ValueError("Marked by is required")


@dataclass(frozen=True)
class AttendanceCommentAddedEvent(AttendanceDomainEvent):
    """Event published when a comment is added to attendance"""
    comment: str
    added_by: str
    
    def __post_init__(self):
        """Validate comment added event"""
        super().__post_init__()
        if not self.comment.strip():
            raise ValueError("Comment is required")
        if not self.added_by.strip():
            raise ValueError("Added by is required")


@dataclass(frozen=True)
class AttendanceBulkUpdateEvent(AttendanceDomainEvent):
    """Event published when multiple attendance records are updated"""
    updated_count: int
    update_type: str  # e.g., "status_change", "regularization", "bulk_import"
    updated_by: str
    
    def __post_init__(self):
        """Validate bulk update event"""
        super().__post_init__()
        if self.updated_count <= 0:
            raise ValueError("Updated count must be positive")
        if not self.update_type.strip():
            raise ValueError("Update type is required")
        if not self.updated_by.strip():
            raise ValueError("Updated by is required")


@dataclass(frozen=True)
class AttendanceReportGeneratedEvent(AttendanceDomainEvent):
    """Event published when an attendance report is generated"""
    report_type: str  # e.g., "monthly", "weekly", "custom"
    report_period_start: str  # ISO format date
    report_period_end: str  # ISO format date
    generated_by: str
    report_format: str  # e.g., "pdf", "excel", "csv"
    
    def __post_init__(self):
        """Validate report generated event"""
        super().__post_init__()
        if not self.report_type.strip():
            raise ValueError("Report type is required")
        if not self.report_period_start:
            raise ValueError("Report period start is required")
        if not self.report_period_end:
            raise ValueError("Report period end is required")
        if not self.generated_by.strip():
            raise ValueError("Generated by is required")
        if not self.report_format.strip():
            raise ValueError("Report format is required")


# Event factory functions for easier event creation
import uuid


def create_attendance_checked_in_event(
    attendance_id: str,
    employee_id: str,
    check_in_time: datetime,
    location: Optional[str] = None,
    marked_by: str = "system"
) -> AttendanceCheckedInEvent:
    """Factory function to create check-in event"""
    return AttendanceCheckedInEvent(
        event_id=str(uuid.uuid4()),
        occurred_at=datetime.utcnow(),
        attendance_id=attendance_id,
        employee_id=employee_id,
        check_in_time=check_in_time,
        location=location,
        marked_by=marked_by
    )


def create_attendance_checked_out_event(
    attendance_id: str,
    employee_id: str,
    check_out_time: datetime,
    working_hours: float,
    overtime_hours: float,
    location: Optional[str] = None,
    marked_by: str = "system"
) -> AttendanceCheckedOutEvent:
    """Factory function to create check-out event"""
    return AttendanceCheckedOutEvent(
        event_id=str(uuid.uuid4()),
        occurred_at=datetime.utcnow(),
        attendance_id=attendance_id,
        employee_id=employee_id,
        check_out_time=check_out_time,
        working_hours=working_hours,
        overtime_hours=overtime_hours,
        location=location,
        marked_by=marked_by
    )


def create_attendance_regularized_event(
    attendance_id: str,
    employee_id: str,
    regularization_reason: str,
    regularized_by: str,
    previous_status: str,
    new_status: str
) -> AttendanceRegularizedEvent:
    """Factory function to create regularization event"""
    return AttendanceRegularizedEvent(
        event_id=str(uuid.uuid4()),
        occurred_at=datetime.utcnow(),
        attendance_id=attendance_id,
        employee_id=employee_id,
        regularization_reason=regularization_reason,
        regularized_by=regularized_by,
        previous_status=previous_status,
        new_status=new_status
    ) 