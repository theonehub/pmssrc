"""
Leave Domain Events
Events related to employee leave operations
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any

from app.domain.events.base_event import DomainEvent


@dataclass
class EmployeeLeaveCreatedEvent(DomainEvent):
    """Event raised when an employee leave is created"""
    
    employee_id: str
    leave_id: str
    leave_name: str
    start_date: date
    end_date: date
    applied_days: int
    created_by: str
    
    def __post_init__(self):
        """Initialize the base class after dataclass initialization"""
        super().__init__(aggregate_id=self.employee_id)
    
    def get_event_type(self) -> str:
        """Get the event type identifier"""
        return "EmployeeLeaveCreated"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_id": self.leave_id,
            "leave_name": self.leave_name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "applied_days": self.applied_days,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmployeeLeaveCreatedEvent':
        """Create event from dictionary representation"""
        event = cls(
            employee_id=data["employee_id"],
            leave_id=data["leave_id"],
            leave_name=data["leave_name"],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            applied_days=data["applied_days"],
            created_by=data["created_by"]
        )
        event.event_id = data["event_id"]
        event.occurred_at = datetime.fromisoformat(data["occurred_at"])
        return event


@dataclass
class EmployeeLeaveUpdatedEvent(DomainEvent):
    """Event raised when an employee leave is updated"""
    
    employee_id: str
    leave_id: str
    leave_name: str
    updated_by: str
    
    def __post_init__(self):
        """Initialize the base class after dataclass initialization"""
        super().__init__(aggregate_id=self.employee_id)
    
    def get_event_type(self) -> str:
        """Get the event type identifier"""
        return "EmployeeLeaveUpdated"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_id": self.leave_id,
            "leave_name": self.leave_name,
            "updated_by": self.updated_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmployeeLeaveUpdatedEvent':
        """Create event from dictionary representation"""
        event = cls(
            employee_id=data["employee_id"],
            leave_id=data["leave_id"],
            leave_name=data["leave_name"],
            updated_by=data["updated_by"]
        )
        event.event_id = data["event_id"]
        event.occurred_at = datetime.fromisoformat(data["occurred_at"])
        return event


@dataclass
class EmployeeLeaveDeletedEvent(DomainEvent):
    """Event raised when an employee leave is deleted"""
    
    employee_id: str
    leave_id: str
    leave_name: str
    deleted_by: str
    deletion_reason: Optional[str] = None
    
    def __post_init__(self):
        """Initialize the base class after dataclass initialization"""
        super().__init__(aggregate_id=self.employee_id)
    
    def get_event_type(self) -> str:
        """Get the event type identifier"""
        return "EmployeeLeaveDeleted"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_id": self.leave_id,
            "leave_name": self.leave_name,
            "deleted_by": self.deleted_by,
            "deletion_reason": self.deletion_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmployeeLeaveDeletedEvent':
        """Create event from dictionary representation"""
        event = cls(
            employee_id=data["employee_id"],
            leave_id=data["leave_id"],
            leave_name=data["leave_name"],
            deleted_by=data["deleted_by"],
            deletion_reason=data.get("deletion_reason")
        )
        event.event_id = data["event_id"]
        event.occurred_at = datetime.fromisoformat(data["occurred_at"])
        return event


@dataclass
class EmployeeLeaveApprovedEvent(DomainEvent):
    """Event raised when an employee leave is approved"""
    
    employee_id: str
    leave_id: str
    leave_name: str
    approved_by: str
    approved_days: int
    event_id: str = field(init=False, default=None)
    aggregate_id: str = field(init=False, default=None)
    occurred_at: datetime = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(aggregate_id=self.employee_id)

    def get_event_type(self) -> str:
        return "EmployeeLeaveApproved"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_id": self.leave_id,
            "leave_name": self.leave_name,
            "approved_by": self.approved_by,
            "approved_days": self.approved_days
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmployeeLeaveApprovedEvent':
        event = cls(
            employee_id=data["employee_id"],
            leave_id=data["leave_id"],
            leave_name=data["leave_name"],
            approved_by=data["approved_by"],
            approved_days=data["approved_days"]
        )
        event.event_id = data["event_id"]
        event.occurred_at = datetime.fromisoformat(data["occurred_at"])
        return event


@dataclass
class EmployeeLeaveRejectedEvent(DomainEvent):
    """Event raised when an employee leave is rejected"""
    
    employee_id: str
    leave_id: str
    leave_name: str
    rejected_by: str
    rejection_reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": "EmployeeLeaveRejected",
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_id": self.leave_id,
            "leave_name": self.leave_name,
            "rejected_by": self.rejected_by,
            "rejection_reason": self.rejection_reason
        }


@dataclass
class EmployeeLeaveCancelledEvent(DomainEvent):
    """Event raised when an employee leave is cancelled"""
    
    employee_id: str
    leave_id: str
    leave_name: str
    cancelled_by: str
    cancellation_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": "EmployeeLeaveCancelled",
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_id": self.leave_id,
            "leave_name": self.leave_name,
            "cancelled_by": self.cancelled_by,
            "cancellation_reason": self.cancellation_reason
        }


@dataclass
class EmployeeLeaveBalanceUpdatedEvent(DomainEvent):
    """Event raised when employee leave balance is updated"""
    
    employee_id: str
    leave_name: str
    previous_balance: float
    new_balance: float
    change_reason: str
    
    def get_aggregate_id(self) -> str:
        """Get aggregate identifier for this event"""
        return f"{self.employee_id}_{self.leave_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": "EmployeeLeaveBalanceUpdated",
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_name": self.leave_name,
            "previous_balance": self.previous_balance,
            "new_balance": self.new_balance,
            "change_reason": self.change_reason
        }


@dataclass
class EmployeeLeaveAccrualEvent(DomainEvent):
    """Event raised when employee leave is accrued"""
    
    employee_id: str
    leave_name: str
    accrued_days: float
    accrual_period: str  # monthly, quarterly, annually
    
    def get_aggregate_id(self) -> str:
        """Get aggregate identifier for this event"""
        return f"{self.employee_id}_{self.leave_name}_{self.accrual_period}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": "EmployeeLeaveAccrual",
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_name": self.leave_name,
            "accrued_days": self.accrued_days,
            "accrual_period": self.accrual_period
        }


@dataclass
class EmployeeLeaveCarryForwardEvent(DomainEvent):
    """Event raised when employee leave is carried forward to next year"""
    
    employee_id: str
    leave_name: str
    carried_forward_days: float
    from_year: int
    to_year: int
    
    def get_aggregate_id(self) -> str:
        """Get aggregate identifier for this event"""
        return f"{self.employee_id}_{self.leave_name}_{self.from_year}_{self.to_year}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": "EmployeeLeaveCarryForward",
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_name": self.leave_name,
            "carried_forward_days": self.carried_forward_days,
            "from_year": self.from_year,
            "to_year": self.to_year
        }


@dataclass
class EmployeeLeaveEncashmentEvent(DomainEvent):
    """Event raised when employee leave is encashed"""
    
    employee_id: str
    leave_name: str
    encashed_days: float
    encashment_amount: float
    
    def get_aggregate_id(self) -> str:
        """Get aggregate identifier for this event"""
        return f"{self.employee_id}_{self.leave_name}_encashment_{self.occurred_at.strftime('%Y%m%d')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": "EmployeeLeaveEncashment",
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_name": self.leave_name,
            "encashed_days": self.encashed_days,
            "encashment_amount": self.encashment_amount
        }


@dataclass
class EmployeeLeaveExpiredEvent(DomainEvent):
    """Event raised when employee leave expires"""
    
    employee_id: str
    leave_name: str
    expired_days: float
    expiry_reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": "EmployeeLeaveExpired",
            "occurred_at": self.occurred_at.isoformat(),
            "employee_id": self.employee_id,
            "leave_name": self.leave_name,
            "expired_days": self.expired_days,
            "expiry_reason": self.expiry_reason
        } 