"""
Reimbursement Domain Entity
Aggregate root for reimbursement request management
"""

import uuid
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum

from app.domain.value_objects.reimbursement_type import ReimbursementType as ReimbursementTypeVO
from app.domain.value_objects.reimbursement_amount import ReimbursementAmount
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.events.reimbursement_events import (
    ReimbursementRequestSubmitted,
    ReimbursementRequestUpdated,
    ReimbursementRequestApproved,
    ReimbursementRequestRejected,
    ReimbursementRequestCancelled,
    ReimbursementRequestPaid,
    ReimbursementReceiptUploaded,
    ReimbursementLimitExceeded,
    ReimbursementComplianceAlert
)


class ReimbursementStatus(Enum):
    """Enumeration of reimbursement request statuses"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    PAID = "paid"


class PaymentMethod(Enum):
    """Enumeration of payment methods"""
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CHEQUE = "cheque"
    DIGITAL_WALLET = "digital_wallet"


@dataclass
class ReimbursementReceipt:
    """Value object for receipt information"""
    file_path: str
    file_name: str
    file_size: int
    uploaded_at: datetime
    uploaded_by: str


@dataclass
class ReimbursementApproval:
    """Value object for approval information"""
    approved_by: str
    approved_at: datetime
    approved_amount: ReimbursementAmount
    approval_level: str
    comments: Optional[str] = None


@dataclass
class ReimbursementPayment:
    """Value object for payment information"""
    paid_by: str
    paid_at: datetime
    payment_method: PaymentMethod
    payment_reference: Optional[str] = None
    bank_details: Optional[str] = None


@dataclass
class Reimbursement:
    """
    Reimbursement aggregate root.
    
    Follows SOLID principles:
    - SRP: Manages reimbursement request business logic
    - OCP: Extensible through composition and events
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for reimbursement operations
    - DIP: Depends on value objects and events
    """
    
    request_id: str
    employee_id: EmployeeId
    reimbursement_type: ReimbursementTypeVO
    amount: ReimbursementAmount
    description: Optional[str]
    status: ReimbursementStatus = ReimbursementStatus.DRAFT
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    
    # Receipt information
    receipt: Optional[ReimbursementReceipt] = None
    
    # Approval information
    approval: Optional[ReimbursementApproval] = None
    rejection_reason: Optional[str] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    
    # Payment information
    payment: Optional[ReimbursementPayment] = None
    
    # Audit fields
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Domain events
    _domain_events: List = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate reimbursement data"""
        if not self.request_id:
            raise ValueError("Request ID cannot be empty")
        
        if not isinstance(self.employee_id, EmployeeId):
            raise ValueError("Employee ID must be a valid EmployeeId")
        
        if not isinstance(self.reimbursement_type, ReimbursementTypeVO):
            raise ValueError("Reimbursement type must be a valid ReimbursementTypeVO")
        
        if not isinstance(self.amount, ReimbursementAmount):
            raise ValueError("Amount must be a valid ReimbursementAmount")
    
    @classmethod
    def create_request(
        cls,
        employee_id: EmployeeId,
        reimbursement_type: ReimbursementTypeVO,
        amount: ReimbursementAmount,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> 'Reimbursement':
        """Factory method for creating reimbursement requests"""
        request_id = str(uuid.uuid4())
        
        reimbursement = cls(
            request_id=request_id,
            employee_id=employee_id,
            reimbursement_type=reimbursement_type,
            amount=amount,
            description=description,
            created_by=created_by
        )
        
        return reimbursement
    
    def update_details(
        self,
        amount: Optional[ReimbursementAmount] = None,
        description: Optional[str] = None,
        updated_by: Optional[str] = None
    ):
        """Update reimbursement details (only allowed in draft status)"""
        if self.status != ReimbursementStatus.DRAFT:
            raise ValueError("Cannot update reimbursement after submission")
        
        old_amount = self.amount
        old_description = self.description
        
        if amount is not None:
            self.amount = amount
        
        if description is not None:
            self.description = description
        
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementRequestUpdated(
                request_id=self.request_id,
                employee_id=self.employee_id.value,
                old_amount=old_amount,
                new_amount=self.amount,
                old_description=old_description,
                new_description=self.description,
                updated_by=updated_by or "system",
                occurred_at=datetime.utcnow()
            )
        )
    
    def submit_request(self, submitted_by: Optional[str] = None):
        """Submit reimbursement request for approval"""
        if self.status != ReimbursementStatus.DRAFT:
            raise ValueError("Can only submit draft reimbursements")
        
        # Validate business rules
        self._validate_submission()
        
        self.status = ReimbursementStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        self.updated_by = submitted_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementRequestSubmitted(
                request_id=self.request_id,
                employee_id=self.employee_id.value,
                reimbursement_type=self.reimbursement_type,
                amount=self.amount,
                description=self.description,
                has_receipt=self.receipt is not None,
                submitted_by=submitted_by or "system",
                occurred_at=datetime.utcnow()
            )
        )
        
        # Check if auto-approval is possible
        if self.reimbursement_type.is_auto_approved():
            self._auto_approve()
    
    def approve_request(
        self,
        approved_by: str,
        approved_amount: Optional[ReimbursementAmount] = None,
        approval_level: str = "manager",
        comments: Optional[str] = None
    ):
        """Approve reimbursement request"""
        if self.status not in [ReimbursementStatus.SUBMITTED, ReimbursementStatus.UNDER_REVIEW]:
            raise ValueError("Can only approve submitted or under review reimbursements")
        
        final_amount = approved_amount or self.amount
        
        self.approval = ReimbursementApproval(
            approved_by=approved_by,
            approved_at=datetime.utcnow(),
            approved_amount=final_amount,
            approval_level=approval_level,
            comments=comments
        )
        
        self.status = ReimbursementStatus.APPROVED
        self.updated_by = approved_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementRequestApproved(
                request_id=self.request_id,
                employee_id=self.employee_id.value,
                reimbursement_type=self.reimbursement_type,
                amount=self.amount,
                approved_amount=final_amount,
                approval_comments=comments,
                approved_by=approved_by,
                approval_level=approval_level,
                occurred_at=datetime.utcnow()
            )
        )
    
    def reject_request(
        self,
        rejected_by: str,
        rejection_reason: str
    ):
        """Reject reimbursement request"""
        if self.status not in [ReimbursementStatus.SUBMITTED, ReimbursementStatus.UNDER_REVIEW]:
            raise ValueError("Can only reject submitted or under review reimbursements")
        
        self.status = ReimbursementStatus.REJECTED
        self.rejection_reason = rejection_reason
        self.rejected_by = rejected_by
        self.rejected_at = datetime.utcnow()
        self.updated_by = rejected_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementRequestRejected(
                request_id=self.request_id,
                employee_id=self.employee_id.value,
                reimbursement_type=self.reimbursement_type,
                amount=self.amount,
                rejection_reason=rejection_reason,
                rejected_by=rejected_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def cancel_request(
        self,
        cancelled_by: str,
        cancellation_reason: Optional[str] = None
    ):
        """Cancel reimbursement request"""
        if self.status in [ReimbursementStatus.PAID, ReimbursementStatus.CANCELLED]:
            raise ValueError("Cannot cancel paid or already cancelled reimbursements")
        
        self.status = ReimbursementStatus.CANCELLED
        self.updated_by = cancelled_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementRequestCancelled(
                request_id=self.request_id,
                employee_id=self.employee_id.value,
                reimbursement_type=self.reimbursement_type,
                amount=self.amount,
                cancellation_reason=cancellation_reason,
                cancelled_by=cancelled_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def process_payment(
        self,
        paid_by: str,
        payment_method: PaymentMethod,
        payment_reference: Optional[str] = None,
        bank_details: Optional[str] = None
    ):
        """Process payment for approved reimbursement"""
        if self.status != ReimbursementStatus.APPROVED:
            raise ValueError("Can only process payment for approved reimbursements")
        
        payment_amount = self.approval.approved_amount if self.approval else self.amount
        
        self.payment = ReimbursementPayment(
            paid_by=paid_by,
            paid_at=datetime.utcnow(),
            payment_method=payment_method,
            payment_reference=payment_reference,
            bank_details=bank_details
        )
        
        self.status = ReimbursementStatus.PAID
        self.updated_by = paid_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementRequestPaid(
                request_id=self.request_id,
                employee_id=self.employee_id.value,
                amount=payment_amount,
                payment_method=payment_method.value,
                payment_reference=payment_reference,
                paid_by=paid_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def upload_receipt(
        self,
        file_path: str,
        file_name: str,
        file_size: int,
        uploaded_by: str
    ):
        """Upload receipt for reimbursement"""
        self.receipt = ReimbursementReceipt(
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            uploaded_at=datetime.utcnow(),
            uploaded_by=uploaded_by
        )
        
        self.updated_by = uploaded_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementReceiptUploaded(
                request_id=self.request_id,
                employee_id=self.employee_id.value,
                file_path=file_path,
                file_name=file_name,
                file_size=file_size,
                uploaded_by=uploaded_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def _validate_submission(self):
        """Validate reimbursement before submission"""
        # Check if receipt is required
        if self.reimbursement_type.requires_receipt and not self.receipt:
            raise ValueError("Receipt is required for this reimbursement type")
        
        # Check amount limits
        if self.reimbursement_type.has_limit():
            limit_amount = ReimbursementAmount(
                self.reimbursement_type.max_limit,
                self.amount.currency
            )
            
            if self.amount.is_greater_than(limit_amount):
                # Add compliance alert event
                self._add_domain_event(
                    ReimbursementLimitExceeded(
                        request_id=self.request_id,
                        employee_id=self.employee_id.value,
                        reimbursement_type=self.reimbursement_type,
                        requested_amount=self.amount,
                        limit_amount=limit_amount,
                        limit_period=self.reimbursement_type.frequency.value,
                        occurred_at=datetime.utcnow()
                    )
                )
                
                # Still allow submission but flag for manual review
                self.status = ReimbursementStatus.UNDER_REVIEW
    
    def _auto_approve(self):
        """Auto-approve reimbursement if eligible"""
        if not self.reimbursement_type.is_auto_approved():
            return
        
        # Additional checks for auto-approval
        if self.reimbursement_type.has_limit():
            limit_amount = ReimbursementAmount(
                self.reimbursement_type.max_limit,
                self.amount.currency
            )
            
            if self.amount.is_greater_than(limit_amount):
                return  # Don't auto-approve if over limit
        
        self.approve_request(
            approved_by="system",
            approved_amount=self.amount,
            approval_level="auto",
            comments="Auto-approved based on reimbursement type settings"
        )
    
    def get_final_amount(self) -> ReimbursementAmount:
        """Get final approved/paid amount"""
        if self.approval:
            return self.approval.approved_amount
        return self.amount
    
    def is_pending_approval(self) -> bool:
        """Check if reimbursement is pending approval"""
        return self.status in [ReimbursementStatus.SUBMITTED, ReimbursementStatus.UNDER_REVIEW]
    
    def is_approved(self) -> bool:
        """Check if reimbursement is approved"""
        return self.status == ReimbursementStatus.APPROVED
    
    def is_paid(self) -> bool:
        """Check if reimbursement is paid"""
        return self.status == ReimbursementStatus.PAID
    
    def is_rejected(self) -> bool:
        """Check if reimbursement is rejected"""
        return self.status == ReimbursementStatus.REJECTED
    
    def is_cancelled(self) -> bool:
        """Check if reimbursement is cancelled"""
        return self.status == ReimbursementStatus.CANCELLED
    
    def can_be_edited(self) -> bool:
        """Check if reimbursement can be edited"""
        return self.status == ReimbursementStatus.DRAFT
    
    def can_be_cancelled(self) -> bool:
        """Check if reimbursement can be cancelled"""
        return self.status not in [ReimbursementStatus.PAID, ReimbursementStatus.CANCELLED]
    
    def _add_domain_event(self, event):
        """Add domain event"""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List:
        """Get domain events"""
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """Clear domain events"""
        self._domain_events.clear()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "employee_id": self.employee_id.value,
            "reimbursement_type": self.reimbursement_type.to_dict(),
            "amount": self.amount.to_dict(),
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "receipt": {
                "file_path": self.receipt.file_path,
                "file_name": self.receipt.file_name,
                "file_size": self.receipt.file_size,
                "uploaded_at": self.receipt.uploaded_at.isoformat(),
                "uploaded_by": self.receipt.uploaded_by
            } if self.receipt else None,
            "approval": {
                "approved_by": self.approval.approved_by,
                "approved_at": self.approval.approved_at.isoformat(),
                "approved_amount": self.approval.approved_amount.to_dict(),
                "approval_level": self.approval.approval_level,
                "comments": self.approval.comments
            } if self.approval else None,
            "rejection_reason": self.rejection_reason,
            "rejected_by": self.rejected_by,
            "rejected_at": self.rejected_at.isoformat() if self.rejected_at else None,
            "payment": {
                "paid_by": self.payment.paid_by,
                "paid_at": self.payment.paid_at.isoformat(),
                "payment_method": self.payment.payment_method.value,
                "payment_reference": self.payment.payment_reference,
                "bank_details": self.payment.bank_details
            } if self.payment else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by
        } 