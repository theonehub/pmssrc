"""
Leave Domain Events
Events that represent important business occurrences in the leave management domain
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from abc import ABC

from domain.value_objects.leave_type import LeaveType
from domain.value_objects.leave_policy import LeavePolicy
from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.date_range import DateRange
from domain.events.employee_events import DomainEvent


# Company Leave Events

@dataclass
class CompanyLeaveCreated(DomainEvent):
    """
    Event raised when a new company leave type is created.
    
    This event can trigger:
    - Employee leave balance initialization
    - Policy communication to employees
    - System configuration updates
    - Audit logging
    """
    
    company_leave_id: str
    leave_type: LeaveType
    policy: LeavePolicy
    created_by: str
    
    def get_event_type(self) -> str:
        return "leave.company_leave_created"
    
    def get_aggregate_id(self) -> str:
        return self.company_leave_id
    
    def get_creation_details(self) -> dict:
        """Get company leave creation details"""
        return {
            "company_leave_id": self.company_leave_id,
            "leave_type": {
                "code": self.leave_type.code,
                "name": self.leave_type.name,
                "category": self.leave_type.category.value
            },
            "policy": {
                "annual_allocation": self.policy.annual_allocation,
                "accrual_type": self.policy.accrual_type.value,
                "requires_approval": self.policy.requires_approval
            },
            "created_by": self.created_by
        }


@dataclass
class CompanyLeaveUpdated(DomainEvent):
    """
    Event raised when company leave details are updated.
    
    This event can trigger:
    - Employee notifications
    - Policy update communications
    - System reconfiguration
    - Audit logging
    """
    
    company_leave_id: str
    leave_type: LeaveType
    changes: Dict[str, Any]
    updated_by: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "leave.company_leave_updated"
    
    def get_aggregate_id(self) -> str:
        return self.company_leave_id
    
    def get_update_details(self) -> dict:
        """Get company leave update details"""
        return {
            "company_leave_id": self.company_leave_id,
            "leave_type": self.leave_type.name,
            "changes": self.changes,
            "updated_by": self.updated_by
        }


@dataclass
class CompanyLeavePolicyChanged(DomainEvent):
    """
    Event raised when company leave policy is changed.
    
    This event can trigger:
    - Employee leave balance recalculation
    - Policy change notifications
    - Compliance updates
    - Historical policy archiving
    """
    
    company_leave_id: str
    leave_type: LeaveType
    old_policy: LeavePolicy
    new_policy: LeavePolicy
    reason: str
    updated_by: str
    
    def get_event_type(self) -> str:
        return "leave.company_leave_policy_changed"
    
    def get_aggregate_id(self) -> str:
        return self.company_leave_id
    
    def get_policy_change_details(self) -> dict:
        """Get policy change details"""
        return {
            "company_leave_id": self.company_leave_id,
            "leave_type": self.leave_type.name,
            "policy_changes": {
                "annual_allocation": {
                    "old": self.old_policy.annual_allocation,
                    "new": self.new_policy.annual_allocation
                },
                "accrual_type": {
                    "old": self.old_policy.accrual_type.value,
                    "new": self.new_policy.accrual_type.value
                },
                "max_carryover_days": {
                    "old": self.old_policy.max_carryover_days,
                    "new": self.new_policy.max_carryover_days
                }
            },
            "reason": self.reason,
            "updated_by": self.updated_by
        }


@dataclass
class CompanyLeaveDeactivated(DomainEvent):
    """
    Event raised when company leave is deactivated.
    
    This event can trigger:
    - Employee leave balance handling
    - Pending application processing
    - Employee notifications
    - System cleanup
    """
    
    company_leave_id: str
    leave_type: LeaveType
    reason: str
    deactivated_by: str
    
    def get_event_type(self) -> str:
        return "leave.company_leave_deactivated"
    
    def get_aggregate_id(self) -> str:
        return self.company_leave_id


# Employee Leave Events

@dataclass
class EmployeeLeaveApplied(DomainEvent):
    """
    Event raised when an employee applies for leave.
    
    This event can trigger:
    - Approval workflow initiation
    - Manager notifications
    - Calendar updates
    - Leave balance updates
    """
    
    leave_application_id: str
    employee_id: EmployeeId
    leave_type: LeaveType
    date_range: DateRange
    requested_days: int
    reason: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "leave.employee_leave_applied"
    
    def get_aggregate_id(self) -> str:
        return self.leave_application_id
    
    def get_application_details(self) -> dict:
        """Get leave application details"""
        return {
            "leave_application_id": self.leave_application_id,
            "employee_id": str(self.employee_id),
            "leave_type": self.leave_type.name,
            "date_range": str(self.date_range),
            "requested_days": self.requested_days,
            "reason": self.reason
        }


@dataclass
class EmployeeLeaveApproved(DomainEvent):
    """
    Event raised when employee leave is approved.
    
    This event can trigger:
    - Employee notifications
    - Calendar updates
    - Leave balance deduction
    - Team notifications
    """
    
    leave_application_id: str
    employee_id: EmployeeId
    leave_type: LeaveType
    date_range: DateRange
    approved_days: int
    approved_by: str
    approval_comments: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "leave.employee_leave_approved"
    
    def get_aggregate_id(self) -> str:
        return self.leave_application_id


@dataclass
class EmployeeLeaveRejected(DomainEvent):
    """
    Event raised when employee leave is rejected.
    
    This event can trigger:
    - Employee notifications
    - Leave balance restoration
    - Feedback collection
    - Alternative suggestions
    """
    
    leave_application_id: str
    employee_id: EmployeeId
    leave_type: LeaveType
    date_range: DateRange
    rejected_by: str
    rejection_reason: str
    
    def get_event_type(self) -> str:
        return "leave.employee_leave_rejected"
    
    def get_aggregate_id(self) -> str:
        return self.leave_application_id


@dataclass
class EmployeeLeaveCancelled(DomainEvent):
    """
    Event raised when employee cancels their leave.
    
    This event can trigger:
    - Leave balance restoration
    - Calendar updates
    - Team notifications
    - Manager notifications
    """
    
    leave_application_id: str
    employee_id: EmployeeId
    leave_type: LeaveType
    date_range: DateRange
    cancelled_by: str
    cancellation_reason: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "leave.employee_leave_cancelled"
    
    def get_aggregate_id(self) -> str:
        return self.leave_application_id


@dataclass
class EmployeeLeaveBalanceUpdated(DomainEvent):
    """
    Event raised when employee leave balance is updated.
    
    This event can trigger:
    - Employee notifications
    - Dashboard updates
    - Reporting updates
    - Analytics updates
    """
    
    employee_id: EmployeeId
    leave_type: LeaveType
    old_balance: float
    new_balance: float
    change_reason: str
    updated_by: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "leave.employee_leave_balance_updated"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.leave_type.code}"
    
    def get_balance_change(self) -> float:
        """Get the change in balance"""
        return self.new_balance - self.old_balance
    
    def is_balance_increase(self) -> bool:
        """Check if balance increased"""
        return self.new_balance > self.old_balance
    
    def get_balance_details(self) -> dict:
        """Get balance change details"""
        return {
            "employee_id": str(self.employee_id),
            "leave_type": self.leave_type.name,
            "balance_change": {
                "old": self.old_balance,
                "new": self.new_balance,
                "change": self.get_balance_change()
            },
            "reason": self.change_reason,
            "updated_by": self.updated_by
        }


@dataclass
class EmployeeLeaveAccrued(DomainEvent):
    """
    Event raised when employee leave is accrued (monthly/quarterly).
    
    This event can trigger:
    - Balance updates
    - Employee notifications
    - Accrual reports
    - Policy compliance checks
    """
    
    employee_id: EmployeeId
    leave_type: LeaveType
    accrued_days: float
    accrual_period: str  # "2024-01", "2024-Q1", etc.
    total_balance: float
    
    def get_event_type(self) -> str:
        return "leave.employee_leave_accrued"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.leave_type.code}_{self.accrual_period}"


@dataclass
class EmployeeLeaveCarriedOver(DomainEvent):
    """
    Event raised when employee leave is carried over to next year.
    
    This event can trigger:
    - Balance adjustments
    - Expiry tracking
    - Employee notifications
    - Policy compliance checks
    """
    
    employee_id: EmployeeId
    leave_type: LeaveType
    carried_over_days: float
    from_year: str
    to_year: str
    expiry_date: Optional[datetime] = None
    
    def get_event_type(self) -> str:
        return "leave.employee_leave_carried_over"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.leave_type.code}_{self.from_year}_{self.to_year}"


@dataclass
class EmployeeLeaveEncashed(DomainEvent):
    """
    Event raised when employee encashes leave.
    
    This event can trigger:
    - Payroll processing
    - Balance deduction
    - Tax calculations
    - Financial reporting
    """
    
    employee_id: EmployeeId
    leave_type: LeaveType
    encashed_days: int
    encashment_amount: float
    processed_by: str
    
    def get_event_type(self) -> str:
        return "leave.employee_leave_encashed"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.leave_type.code}_encashment_{self.occurred_at.strftime('%Y%m%d')}"


# Leave Compliance Events

@dataclass
class LeaveComplianceAlert(DomainEvent):
    """
    Event raised when leave compliance issues are detected.
    
    This event can trigger:
    - HR notifications
    - Compliance reports
    - Corrective actions
    - Policy reviews
    """
    
    employee_id: EmployeeId
    leave_type: LeaveType
    alert_type: str  # "excessive_leave", "policy_violation", "balance_negative", etc.
    message: str
    severity: str  # "low", "medium", "high", "critical"
    
    def get_event_type(self) -> str:
        return "leave.compliance_alert"
    
    def get_aggregate_id(self) -> str:
        return f"{self.employee_id}_{self.alert_type}_{self.occurred_at.strftime('%Y%m%d')}"
    
    def is_critical(self) -> bool:
        """Check if this is a critical compliance alert"""
        return self.severity == "critical"


# Event type registry for leave events
LEAVE_EVENT_TYPE_REGISTRY = {
    "leave.company_leave_created": CompanyLeaveCreated,
    "leave.company_leave_updated": CompanyLeaveUpdated,
    "leave.company_leave_policy_changed": CompanyLeavePolicyChanged,
    "leave.company_leave_deactivated": CompanyLeaveDeactivated,
    "leave.employee_leave_applied": EmployeeLeaveApplied,
    "leave.employee_leave_approved": EmployeeLeaveApproved,
    "leave.employee_leave_rejected": EmployeeLeaveRejected,
    "leave.employee_leave_cancelled": EmployeeLeaveCancelled,
    "leave.employee_leave_balance_updated": EmployeeLeaveBalanceUpdated,
    "leave.employee_leave_accrued": EmployeeLeaveAccrued,
    "leave.employee_leave_carried_over": EmployeeLeaveCarriedOver,
    "leave.employee_leave_encashed": EmployeeLeaveEncashed,
    "leave.compliance_alert": LeaveComplianceAlert,
}


def get_leave_event_class(event_type: str) -> type:
    """Get leave event class by event type string"""
    return LEAVE_EVENT_TYPE_REGISTRY.get(event_type)


def is_valid_leave_event_type(event_type: str) -> bool:
    """Check if leave event type is valid"""
    return event_type in LEAVE_EVENT_TYPE_REGISTRY 