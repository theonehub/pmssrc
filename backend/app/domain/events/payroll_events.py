"""
Payroll Domain Events
Events that represent important business occurrences in the payroll domain
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid

from .base_events import DomainEvent


class PayoutStatus(str, Enum):
    """Payout status enumeration"""
    PENDING = "pending"
    CALCULATED = "calculated"
    PROCESSED = "processed"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PayslipFormat(str, Enum):
    """Payslip format enumeration"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"


@dataclass(frozen=True)  
class PayoutCalculated:
    """Event fired when payout is calculated for an employee"""
    employee_id: str
    month: int
    year: int
    gross_salary: float
    net_salary: float
    total_deductions: float
    basic_salary: float
    allowances: float
    tax_deducted: float
    working_days: int
    lwp_days: int
    calculation_method: str
    tax_regime: str
    override_applied: bool = False
    # DomainEvent fields
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)
    event_version: str = "1.0"
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def event_type(self) -> str:
        """Get the event type name"""
        return self.__class__.__name__


@dataclass(frozen=True)
class PayoutCreated(DomainEvent):
    """Event fired when payout record is created"""
    payout_id: str
    employee_id: str
    month: int
    year: int
    gross_salary: float
    net_salary: float
    status: PayoutStatus
    created_by: Optional[str] = None
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class PayoutUpdated(DomainEvent):
    """Event fired when payout record is updated"""
    payout_id: str
    employee_id: str
    previous_status: PayoutStatus
    new_status: PayoutStatus
    updated_by: str
    changes: Dict[str, Any]
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class PayoutStatusChanged:
    """Event fired when payout status changes"""
    payout_id: str
    employee_id: str
    previous_status: PayoutStatus
    new_status: PayoutStatus
    changed_by: str
    reason: Optional[str] = None
    # DomainEvent fields
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)
    event_version: str = "1.0"
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class PayoutApproved(DomainEvent):
    """Event fired when payout is approved"""
    payout_id: str
    employee_id: str
    approved_by: str
    approved_amount: float
    approval_date: datetime
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class PayoutPaid(DomainEvent):
    """Event fired when payout is paid"""
    payout_id: str
    employee_id: str
    paid_amount: float
    payment_date: datetime
    payment_method: str
    transaction_reference: Optional[str] = None
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class PayslipGenerated:
    """Event fired when payslip is generated"""
    payslip_id: str
    payout_id: str
    employee_id: str
    format: PayslipFormat
    file_size: Optional[int] = None
    generated_by: Optional[str] = None
    # DomainEvent fields
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)
    event_version: str = "1.0"
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class PayslipEmailed(DomainEvent):
    """Event fired when payslip is emailed to employee"""
    payslip_id: str
    payout_id: str
    employee_id: str
    recipient_email: str
    email_status: str
    email_provider: Optional[str] = None
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class BulkPayoutStarted(DomainEvent):
    """Event fired when bulk payout processing starts"""
    batch_id: str
    month: int
    year: int
    total_employees: int
    initiated_by: str
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class BulkPayoutCompleted(DomainEvent):
    """Event fired when bulk payout processing completes"""
    batch_id: str
    month: int
    year: int
    total_employees: int
    successful_count: int
    failed_count: int
    processing_duration: float
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class BulkPayslipsGenerated(DomainEvent):
    """Event fired when bulk payslips are generated"""
    batch_id: str
    month: int
    year: int
    total_payslips: int
    successful_generations: int
    failed_generations: int
    format: PayslipFormat
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class BulkPayslipsEmailed(DomainEvent):
    """Event fired when bulk payslips are emailed"""
    batch_id: str
    month: int
    year: int
    total_emails: int
    successful_emails: int
    failed_emails: int
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class PayoutScheduleCreated(DomainEvent):
    """Event fired when automatic payout schedule is created"""
    schedule_id: str
    month: int
    year: int
    scheduled_date: date
    auto_process: bool
    auto_approve: bool
    created_by: str
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class ScheduledPayoutProcessed(DomainEvent):
    """Event fired when scheduled payout is processed"""
    schedule_id: str
    month: int
    year: int
    total_employees: int
    successful_count: int
    failed_count: int
    processing_date: datetime
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class PayrollErrorOccurred(DomainEvent):
    """Event fired when payroll processing error occurs"""
    operation: str
    employee_id: Optional[str] = None
    payout_id: Optional[str] = None
    error_type: str = "unknown"
    error_message: str = ""
    error_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class PayrollDataCorrected(DomainEvent):
    """Event fired when payroll data correction is applied"""
    correction_id: str
    payout_id: str
    employee_id: str
    correction_type: str
    previous_values: Dict[str, Any]
    new_values: Dict[str, Any]
    corrected_by: str
    reason: str
    
    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class PayrollAuditEvent(DomainEvent):
    """Event fired for payroll audit trail"""
    audit_id: str
    operation: str
    entity_type: str  # payout, payslip, schedule
    entity_id: str
    employee_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        super().__init__() 