"""
Reimbursement Domain Events
Events for reimbursement lifecycle and business operations
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from decimal import Decimal

from domain.events.employee_events import DomainEvent
from domain.value_objects.reimbursement_type import ReimbursementType as ReimbursementTypeVO
from domain.value_objects.reimbursement_amount import ReimbursementAmount


# Reimbursement Type Events

@dataclass
class ReimbursementTypeCreated(DomainEvent):
    """Event raised when a reimbursement type is created"""
    
    type_id: str
    reimbursement_type: ReimbursementTypeVO
    created_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementTypeCreated"
    
    def get_aggregate_id(self) -> str:
        return self.type_id
    
    def get_event_description(self) -> str:
        return f"Reimbursement type '{self.reimbursement_type.name}' created"


@dataclass
class ReimbursementTypeUpdated(DomainEvent):
    """Event raised when a reimbursement type is updated"""
    
    type_id: str
    old_reimbursement_type: ReimbursementTypeVO
    new_reimbursement_type: ReimbursementTypeVO
    updated_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementTypeUpdated"
    
    def get_aggregate_id(self) -> str:
        return self.type_id
    
    def get_event_description(self) -> str:
        return f"Reimbursement type '{self.new_reimbursement_type.name}' updated"


@dataclass
class ReimbursementTypeActivated(DomainEvent):
    """Event raised when a reimbursement type is activated"""
    
    type_id: str
    reimbursement_type: ReimbursementTypeVO
    activated_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementTypeActivated"
    
    def get_aggregate_id(self) -> str:
        return self.type_id
    
    def get_event_description(self) -> str:
        return f"Reimbursement type '{self.reimbursement_type.name}' activated"


@dataclass
class ReimbursementTypeDeactivated(DomainEvent):
    """Event raised when a reimbursement type is deactivated"""
    
    type_id: str
    reimbursement_type: ReimbursementTypeVO
    reason: Optional[str]
    deactivated_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementTypeDeactivated"
    
    def get_aggregate_id(self) -> str:
        return self.type_id
    
    def get_event_description(self) -> str:
        reason_text = f" (Reason: {self.reason})" if self.reason else ""
        return f"Reimbursement type '{self.reimbursement_type.name}' deactivated{reason_text}"


# Reimbursement Request Events

@dataclass
class ReimbursementRequestSubmitted(DomainEvent):
    """Event raised when a reimbursement request is submitted"""
    
    request_id: str
    employee_id: str
    reimbursement_type: ReimbursementTypeVO
    amount: ReimbursementAmount
    description: Optional[str]
    has_receipt: bool
    submitted_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementRequestSubmitted"
    
    def get_aggregate_id(self) -> str:
        return self.request_id
    
    def get_event_description(self) -> str:
        return f"Reimbursement request for {self.amount} submitted by employee {self.employee_id}"


@dataclass
class ReimbursementRequestUpdated(DomainEvent):
    """Event raised when a reimbursement request is updated"""
    
    request_id: str
    employee_id: str
    old_amount: ReimbursementAmount
    new_amount: ReimbursementAmount
    old_description: Optional[str]
    new_description: Optional[str]
    updated_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementRequestUpdated"
    
    def get_aggregate_id(self) -> str:
        return self.request_id
    
    def get_event_description(self) -> str:
        return f"Reimbursement request updated from {self.old_amount} to {self.new_amount}"


@dataclass
class ReimbursementRequestApproved(DomainEvent):
    """Event raised when a reimbursement request is approved"""
    
    request_id: str
    employee_id: str
    reimbursement_type: ReimbursementTypeVO
    amount: ReimbursementAmount
    approved_amount: ReimbursementAmount
    approval_comments: Optional[str]
    approved_by: str
    approval_level: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementRequestApproved"
    
    def get_aggregate_id(self) -> str:
        return self.request_id
    
    def get_event_description(self) -> str:
        return f"Reimbursement request for {self.approved_amount} approved by {self.approved_by}"


@dataclass
class ReimbursementRequestRejected(DomainEvent):
    """Event raised when a reimbursement request is rejected"""
    
    request_id: str
    employee_id: str
    reimbursement_type: ReimbursementTypeVO
    amount: ReimbursementAmount
    rejection_reason: str
    rejected_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementRequestRejected"
    
    def get_aggregate_id(self) -> str:
        return self.request_id
    
    def get_event_description(self) -> str:
        return f"Reimbursement request for {self.amount} rejected: {self.rejection_reason}"


@dataclass
class ReimbursementRequestCancelled(DomainEvent):
    """Event raised when a reimbursement request is cancelled"""
    
    request_id: str
    employee_id: str
    reimbursement_type: ReimbursementTypeVO
    amount: ReimbursementAmount
    cancellation_reason: Optional[str]
    cancelled_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementRequestCancelled"
    
    def get_aggregate_id(self) -> str:
        return self.request_id
    
    def get_event_description(self) -> str:
        reason_text = f" (Reason: {self.cancellation_reason})" if self.cancellation_reason else ""
        return f"Reimbursement request for {self.amount} cancelled{reason_text}"


@dataclass
class ReimbursementRequestPaid(DomainEvent):
    """Event raised when a reimbursement request is paid"""
    
    request_id: str
    employee_id: str
    amount: ReimbursementAmount
    payment_method: str
    payment_reference: Optional[str]
    paid_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementRequestPaid"
    
    def get_aggregate_id(self) -> str:
        return self.request_id
    
    def get_event_description(self) -> str:
        return f"Reimbursement payment of {self.amount} processed for employee {self.employee_id}"


@dataclass
class ReimbursementReceiptUploaded(DomainEvent):
    """Event raised when a receipt is uploaded for a reimbursement"""
    
    request_id: str
    employee_id: str
    file_path: str
    file_name: str
    file_size: int
    uploaded_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementReceiptUploaded"
    
    def get_aggregate_id(self) -> str:
        return self.request_id
    
    def get_event_description(self) -> str:
        return f"Receipt '{self.file_name}' uploaded for reimbursement request"


@dataclass
class ReimbursementLimitExceeded(DomainEvent):
    """Event raised when a reimbursement request exceeds limits"""
    
    request_id: str
    employee_id: str
    reimbursement_type: ReimbursementTypeVO
    requested_amount: ReimbursementAmount
    limit_amount: ReimbursementAmount
    limit_period: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementLimitExceeded"
    
    def get_aggregate_id(self) -> str:
        return self.request_id
    
    def get_event_description(self) -> str:
        return f"Reimbursement request for {self.requested_amount} exceeds {self.limit_period} limit of {self.limit_amount}"


@dataclass
class ReimbursementBulkApproval(DomainEvent):
    """Event raised when multiple reimbursements are approved in bulk"""
    
    batch_id: str
    request_ids: list
    total_amount: ReimbursementAmount
    approved_by: str
    approval_criteria: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementBulkApproval"
    
    def get_aggregate_id(self) -> str:
        return self.batch_id
    
    def get_event_description(self) -> str:
        return f"Bulk approval of {len(self.request_ids)} reimbursements totaling {self.total_amount}"


@dataclass
class ReimbursementComplianceAlert(DomainEvent):
    """Event raised for reimbursement compliance issues"""
    
    alert_id: str
    request_id: str
    employee_id: str
    compliance_issue: str
    severity: str  # "low", "medium", "high", "critical"
    detected_by: Optional[str]
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementComplianceAlert"
    
    def get_aggregate_id(self) -> str:
        return self.request_id
    
    def get_event_description(self) -> str:
        return f"{self.severity.upper()} compliance alert: {self.compliance_issue}"


@dataclass
class ReimbursementReportGenerated(DomainEvent):
    """Event raised when a reimbursement report is generated"""
    
    report_id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    total_requests: int
    total_amount: ReimbursementAmount
    generated_by: str
    occurred_at: datetime
    
    def get_event_type(self) -> str:
        return "ReimbursementReportGenerated"
    
    def get_aggregate_id(self) -> str:
        return self.report_id
    
    def get_event_description(self) -> str:
        return f"{self.report_type} report generated with {self.total_requests} requests totaling {self.total_amount}"


# Event registry for type lookup
REIMBURSEMENT_EVENT_TYPES = {
    "ReimbursementTypeCreated": ReimbursementTypeCreated,
    "ReimbursementTypeUpdated": ReimbursementTypeUpdated,
    "ReimbursementTypeActivated": ReimbursementTypeActivated,
    "ReimbursementTypeDeactivated": ReimbursementTypeDeactivated,
    "ReimbursementRequestSubmitted": ReimbursementRequestSubmitted,
    "ReimbursementRequestUpdated": ReimbursementRequestUpdated,
    "ReimbursementRequestApproved": ReimbursementRequestApproved,
    "ReimbursementRequestRejected": ReimbursementRequestRejected,
    "ReimbursementRequestCancelled": ReimbursementRequestCancelled,
    "ReimbursementRequestPaid": ReimbursementRequestPaid,
    "ReimbursementReceiptUploaded": ReimbursementReceiptUploaded,
    "ReimbursementLimitExceeded": ReimbursementLimitExceeded,
    "ReimbursementBulkApproval": ReimbursementBulkApproval,
    "ReimbursementComplianceAlert": ReimbursementComplianceAlert,
    "ReimbursementReportGenerated": ReimbursementReportGenerated
}


def get_reimbursement_event_class(event_type: str):
    """Get event class by type name"""
    return REIMBURSEMENT_EVENT_TYPES.get(event_type)


def get_all_reimbursement_event_types() -> list:
    """Get all reimbursement event type names"""
    return list(REIMBURSEMENT_EVENT_TYPES.keys()) 