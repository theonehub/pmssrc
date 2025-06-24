"""
Attendance Domain Events
Events published by the attendance aggregate for system integration
"""

from datetime import datetime
from typing import Optional, Dict, Any
# Removed dataclass import as we're using regular classes

from app.domain.events.base_event import DomainEvent


class AttendanceDomainEvent(DomainEvent):
    """Base class for all attendance domain events"""
    
    def __init__(self, attendance_id: str, employee_id: str, occurred_at: datetime = None):
        super().__init__(aggregate_id=attendance_id, occurred_at=occurred_at)
        self.attendance_id = attendance_id
        self.employee_id = employee_id
    
    def get_aggregate_id(self) -> str:
        """Get the attendance ID as aggregate ID"""
        return self.attendance_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation"""
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.attendance_id,
            "employee_id": self.employee_id,
            "occurred_at": self.occurred_at.isoformat(),
            **self._get_event_data()
        }
    
    def _get_event_data(self) -> Dict[str, Any]:
        """Get event-specific data - to be overridden by subclasses"""
        return {}


class AttendanceCreatedEvent(AttendanceDomainEvent):
    """Event published when a new attendance record is created"""
    
    def __init__(self, attendance_id: str, employee_id: str, attendance_date: str, 
                 initial_status: str, created_by: str, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.attendance_date = attendance_date
        self.initial_status = initial_status
        self.created_by = created_by
    
    def get_event_type(self) -> str:
        return "AttendanceCreated"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "attendance_date": self.attendance_date,
            "initial_status": self.initial_status,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceCreatedEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            attendance_date=data["attendance_date"],
            initial_status=data["initial_status"],
            created_by=data["created_by"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )


class AttendanceCheckedInEvent(AttendanceDomainEvent):
    """Event published when an employee checks in"""
    
    def __init__(self, attendance_id: str, employee_id: str, check_in_time: datetime,
                 location: Optional[str] = None, marked_by: str = "system", occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.check_in_time = check_in_time
        self.location = location
        self.marked_by = marked_by
    
    def get_event_type(self) -> str:
        return "AttendanceCheckedIn"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "check_in_time": self.check_in_time.isoformat(),
            "location": self.location,
            "marked_by": self.marked_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceCheckedInEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            check_in_time=datetime.fromisoformat(data["check_in_time"]),
            location=data.get("location"),
            marked_by=data.get("marked_by", "system"),
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceCheckedOutEvent(AttendanceDomainEvent):
    """Event published when an employee checks out"""
    location: Optional[str] = None
    marked_by: str = "system"
    
    def __init__(self, attendance_id: str, employee_id: str, check_out_time: datetime,
                 working_hours: float, overtime_hours: float, location: Optional[str] = None,
                 marked_by: str = "system", occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.check_out_time = check_out_time
        self.working_hours = working_hours
        self.overtime_hours = overtime_hours
        self.location = location
        self.marked_by = marked_by
    
    def get_event_type(self) -> str:
        return "AttendanceCheckedOut"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "check_out_time": self.check_out_time.isoformat(),
            "working_hours": self.working_hours,
            "overtime_hours": self.overtime_hours,
            "location": self.location,
            "marked_by": self.marked_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceCheckedOutEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            check_out_time=datetime.fromisoformat(data["check_out_time"]),
            working_hours=data["working_hours"],
            overtime_hours=data["overtime_hours"],
            location=data.get("location"),
            marked_by=data.get("marked_by", "system"),
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class BreakStartedEvent(AttendanceDomainEvent):
    """Event published when an employee starts a break"""
    marked_by: str = "system"
    
    def __init__(self, attendance_id: str, employee_id: str, break_start_time: datetime,
                 marked_by: str = "system", occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.break_start_time = break_start_time
        self.marked_by = marked_by
    
    def get_event_type(self) -> str:
        return "BreakStarted"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "break_start_time": self.break_start_time.isoformat(),
            "marked_by": self.marked_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BreakStartedEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            break_start_time=datetime.fromisoformat(data["break_start_time"]),
            marked_by=data.get("marked_by", "system"),
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class BreakEndedEvent(AttendanceDomainEvent):
    """Event published when an employee ends a break"""
    marked_by: str = "system"
    
    def __init__(self, attendance_id: str, employee_id: str, break_end_time: datetime,
                 break_duration_minutes: int, marked_by: str = "system", occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.break_end_time = break_end_time
        self.break_duration_minutes = break_duration_minutes
        self.marked_by = marked_by
    
    def get_event_type(self) -> str:
        return "BreakEnded"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "break_end_time": self.break_end_time.isoformat(),
            "break_duration_minutes": self.break_duration_minutes,
            "marked_by": self.marked_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BreakEndedEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            break_end_time=datetime.fromisoformat(data["break_end_time"]),
            break_duration_minutes=data["break_duration_minutes"],
            marked_by=data.get("marked_by", "system"),
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceRegularizedEvent(AttendanceDomainEvent):
    """Event published when attendance is regularized"""
    
    def __init__(self, attendance_id: str, employee_id: str, regularization_reason: str,
                 regularized_by: str, previous_status: str, new_status: str, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.regularization_reason = regularization_reason
        self.regularized_by = regularized_by
        self.previous_status = previous_status
        self.new_status = new_status
    
    def get_event_type(self) -> str:
        return "AttendanceRegularized"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "regularization_reason": self.regularization_reason,
            "regularized_by": self.regularized_by,
            "previous_status": self.previous_status,
            "new_status": self.new_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceRegularizedEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            regularization_reason=data["regularization_reason"],
            regularized_by=data["regularized_by"],
            previous_status=data["previous_status"],
            new_status=data["new_status"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceUpdatedEvent(AttendanceDomainEvent):
    """Event published when attendance status is updated"""
    reason: Optional[str] = None
    
    def __init__(self, attendance_id: str, employee_id: str, previous_status: str,
                 new_status: str, updated_by: str, reason: Optional[str] = None, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.previous_status = previous_status
        self.new_status = new_status
        self.updated_by = updated_by
        self.reason = reason
    
    def get_event_type(self) -> str:
        return "AttendanceUpdated"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "updated_by": self.updated_by,
            "reason": self.reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceUpdatedEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            previous_status=data["previous_status"],
            new_status=data["new_status"],
            updated_by=data["updated_by"],
            reason=data.get("reason"),
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceDeletedEvent(AttendanceDomainEvent):
    """Event published when attendance is deleted"""
    
    def __init__(self, attendance_id: str, employee_id: str, deleted_by: str,
                 deletion_reason: str, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.deleted_by = deleted_by
        self.deletion_reason = deletion_reason
    
    def get_event_type(self) -> str:
        return "AttendanceDeleted"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "deleted_by": self.deleted_by,
            "deletion_reason": self.deletion_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceDeletedEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            deleted_by=data["deleted_by"],
            deletion_reason=data["deletion_reason"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceLateArrivalEvent(AttendanceDomainEvent):
    """Event published when an employee arrives late"""
    
    def __init__(self, attendance_id: str, employee_id: str, expected_start_time: datetime,
                 actual_start_time: datetime, late_minutes: int, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.expected_start_time = expected_start_time
        self.actual_start_time = actual_start_time
        self.late_minutes = late_minutes
    
    def get_event_type(self) -> str:
        return "AttendanceLateArrival"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "expected_start_time": self.expected_start_time.isoformat(),
            "actual_start_time": self.actual_start_time.isoformat(),
            "late_minutes": self.late_minutes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceLateArrivalEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            expected_start_time=datetime.fromisoformat(data["expected_start_time"]),
            actual_start_time=datetime.fromisoformat(data["actual_start_time"]),
            late_minutes=data["late_minutes"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceEarlyDepartureEvent(AttendanceDomainEvent):
    """Event published when an employee leaves early"""
    
    def __init__(self, attendance_id: str, employee_id: str, expected_end_time: datetime,
                 actual_end_time: datetime, early_minutes: int, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.expected_end_time = expected_end_time
        self.actual_end_time = actual_end_time
        self.early_minutes = early_minutes
    
    def get_event_type(self) -> str:
        return "AttendanceEarlyDeparture"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "expected_end_time": self.expected_end_time.isoformat(),
            "actual_end_time": self.actual_end_time.isoformat(),
            "early_minutes": self.early_minutes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceEarlyDepartureEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            expected_end_time=datetime.fromisoformat(data["expected_end_time"]),
            actual_end_time=datetime.fromisoformat(data["actual_end_time"]),
            early_minutes=data["early_minutes"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceOvertimeEvent(AttendanceDomainEvent):
    """Event published when an employee works overtime"""
    overtime_rate: Optional[float] = None
    
    def __init__(self, attendance_id: str, employee_id: str, regular_hours: float,
                 overtime_hours: float, total_hours: float, overtime_rate: Optional[float] = None,
                 occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.regular_hours = regular_hours
        self.overtime_hours = overtime_hours
        self.total_hours = total_hours
        self.overtime_rate = overtime_rate
    
    def get_event_type(self) -> str:
        return "AttendanceOvertime"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "regular_hours": self.regular_hours,
            "overtime_hours": self.overtime_hours,
            "total_hours": self.total_hours,
            "overtime_rate": self.overtime_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceOvertimeEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            regular_hours=data["regular_hours"],
            overtime_hours=data["overtime_hours"],
            total_hours=data["total_hours"],
            overtime_rate=data.get("overtime_rate"),
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceAbsentEvent(AttendanceDomainEvent):
    """Event published when an employee is marked absent"""
    absence_reason: Optional[str] = None
    marked_by: str = "system"
    
    def __init__(self, attendance_id: str, employee_id: str, absence_date: str,
                 absence_reason: Optional[str] = None, marked_by: str = "system", occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.absence_date = absence_date
        self.absence_reason = absence_reason
        self.marked_by = marked_by
    
    def get_event_type(self) -> str:
        return "AttendanceAbsent"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "absence_date": self.absence_date,
            "absence_reason": self.absence_reason,
            "marked_by": self.marked_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceAbsentEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            absence_date=data["absence_date"],
            absence_reason=data.get("absence_reason"),
            marked_by=data.get("marked_by", "system"),
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceHalfDayEvent(AttendanceDomainEvent):
    """Event published when an employee works half day"""
    
    def __init__(self, attendance_id: str, employee_id: str, working_hours: float,
                 minimum_hours_threshold: float, full_day_threshold: float, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.working_hours = working_hours
        self.minimum_hours_threshold = minimum_hours_threshold
        self.full_day_threshold = full_day_threshold
    
    def get_event_type(self) -> str:
        return "AttendanceHalfDay"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "working_hours": self.working_hours,
            "minimum_hours_threshold": self.minimum_hours_threshold,
            "full_day_threshold": self.full_day_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceHalfDayEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            working_hours=data["working_hours"],
            minimum_hours_threshold=data["minimum_hours_threshold"],
            full_day_threshold=data["full_day_threshold"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceWorkFromHomeEvent(AttendanceDomainEvent):
    """Event published when an employee works from home"""
    reason: Optional[str] = None
    
    def __init__(self, attendance_id: str, employee_id: str, wfh_date: str,
                 marked_by: str, reason: Optional[str] = None, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.wfh_date = wfh_date
        self.marked_by = marked_by
        self.reason = reason
    
    def get_event_type(self) -> str:
        return "AttendanceWorkFromHome"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "wfh_date": self.wfh_date,
            "marked_by": self.marked_by,
            "reason": self.reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceWorkFromHomeEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            wfh_date=data["wfh_date"],
            marked_by=data["marked_by"],
            reason=data.get("reason"),
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceCommentAddedEvent(AttendanceDomainEvent):
    """Event published when a comment is added to attendance"""
    
    def __init__(self, attendance_id: str, employee_id: str, comment: str,
                 added_by: str, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.comment = comment
        self.added_by = added_by
    
    def get_event_type(self) -> str:
        return "AttendanceCommentAdded"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "comment": self.comment,
            "added_by": self.added_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceCommentAddedEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            comment=data["comment"],
            added_by=data["added_by"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceBulkUpdateEvent(AttendanceDomainEvent):
    """Event published when multiple attendance records are updated"""
    
    def __init__(self, attendance_id: str, employee_id: str, updated_count: int,
                 update_type: str, updated_by: str, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.updated_count = updated_count
        self.update_type = update_type
        self.updated_by = updated_by
    
    def get_event_type(self) -> str:
        return "AttendanceBulkUpdate"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "updated_count": self.updated_count,
            "update_type": self.update_type,
            "updated_by": self.updated_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceBulkUpdateEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            updated_count=data["updated_count"],
            update_type=data["update_type"],
            updated_by=data["updated_by"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )



class AttendanceReportGeneratedEvent(AttendanceDomainEvent):
    """Event published when an attendance report is generated"""
    
    def __init__(self, attendance_id: str, employee_id: str, report_type: str,
                 report_period_start: str, report_period_end: str, generated_by: str,
                 report_format: str, occurred_at: datetime = None):
        super().__init__(attendance_id, employee_id, occurred_at)
        self.report_type = report_type
        self.report_period_start = report_period_start
        self.report_period_end = report_period_end
        self.generated_by = generated_by
        self.report_format = report_format
    
    def get_event_type(self) -> str:
        return "AttendanceReportGenerated"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "report_type": self.report_type,
            "report_period_start": self.report_period_start,
            "report_period_end": self.report_period_end,
            "generated_by": self.generated_by,
            "report_format": self.report_format
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceReportGeneratedEvent':
        return cls(
            attendance_id=data["aggregate_id"],
            employee_id=data["employee_id"],
            report_type=data["report_type"],
            report_period_start=data["report_period_start"],
            report_period_end=data["report_period_end"],
            generated_by=data["generated_by"],
            report_format=data["report_format"],
            occurred_at=datetime.fromisoformat(data["occurred_at"])
        )


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