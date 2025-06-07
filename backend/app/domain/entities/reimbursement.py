"""
Reimbursement Domain Entity
Aggregate root for reimbursement request management
"""

from decimal import Decimal
import uuid
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum

from app.domain.value_objects.reimbursement_type import ReimbursementType as ReimbursementTypeVO
from app.domain.value_objects.employee_id import EmployeeId


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
    approved_amount: Decimal
    comments: Optional[str] = None

@dataclass
class ReimbursementRejection:
    """Value object for rejection information"""
    rejected_by: str
    rejected_at: datetime
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
    
    reimbursement_id: str
    employee_id: EmployeeId
    reimbursement_type: ReimbursementTypeVO
    amount: Decimal
    description: Optional[str]
    status: ReimbursementStatus = ReimbursementStatus.DRAFT

    # Receipt information
    receipt: Optional[ReimbursementReceipt] = None
    
    # Approval information
    approval: Optional[ReimbursementApproval] = None
    rejection: Optional[ReimbursementRejection] = None
    
    # Payment information
    payment: Optional[ReimbursementPayment] = None
    
    # Audit fields
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate reimbursement data"""
        if not self.reimbursement_id:
            raise ValueError("Reimbursement ID cannot be empty")
        
        if not isinstance(self.employee_id, EmployeeId):
            raise ValueError("Employee ID must be a valid EmployeeId")
        
        if not isinstance(self.reimbursement_type, ReimbursementTypeVO):
            raise ValueError("Reimbursement type must be a valid ReimbursementTypeVO")
        
        if not isinstance(self.amount, Decimal):
            raise ValueError("Amount must be a valid Decimal")
    
    @classmethod
    def create_request(
        cls,
        employee_id: EmployeeId,
        reimbursement_type: ReimbursementTypeVO,
        amount: Decimal,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> 'Reimbursement':
        """Factory method for creating reimbursement requests"""
        reimbursement_id = str(uuid.uuid4())
        
        reimbursement = cls(
            reimbursement_id=reimbursement_id,
            employee_id=employee_id,
            reimbursement_type=reimbursement_type,
            amount=amount,
            description=description,
            created_by=created_by
        )
        
        return reimbursement
    
    def update_details(
        self,
        amount: Optional[Decimal] = None,
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
        self.updated_at = datetime.now()
        
    def submit_request(self, submitted_by: Optional[str] = None):
        """Submit reimbursement request for approval"""
        if self.status != ReimbursementStatus.DRAFT:
            raise ValueError("Can only submit draft reimbursements")
        
        # Validate business rules
        self._validate_submission()
        
        self.status = ReimbursementStatus.SUBMITTED
        self.submitted_at = datetime.now()
        self.updated_by = submitted_by
        self.updated_at = datetime.now()
        
        # Check if auto-approval is possible
        if not self.reimbursement_type.is_approval_required:
            self._auto_approve()
    
    def approve_request(
        self,
        approved_by: str,
        approved_amount: Optional[Decimal] = None,      
        comments: Optional[str] = None
    ):
        """Approve reimbursement request"""
        if self.status not in [ReimbursementStatus.SUBMITTED, ReimbursementStatus.UNDER_REVIEW]:
            raise ValueError("Can only approve submitted or under review reimbursements")
        
        final_amount = approved_amount or self.amount
        
        self.approval = ReimbursementApproval(
            approved_by=approved_by,
            approved_at=datetime.now(),
            approved_amount=final_amount,
            comments=comments
        )
        
        self.status = ReimbursementStatus.APPROVED
        self.updated_by = approved_by
        self.updated_at = datetime.now()
        
        
    
    def reject_request(
        self,
        rejected_by: str,
        rejection_comments: str
    ):
        """Reject reimbursement request"""
        if self.status not in [ReimbursementStatus.SUBMITTED, ReimbursementStatus.UNDER_REVIEW]:
            raise ValueError("Can only reject submitted or under review reimbursements")
        
        self.status = ReimbursementStatus.REJECTED
        self.rejection = ReimbursementRejection(
            rejected_by=rejected_by,
            rejected_at=datetime.now(),
            comments=rejection_comments
        )
        self.updated_by = rejected_by
        self.updated_at = datetime.now()
        
    
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
        self.updated_at = datetime.now()
        
    
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
            paid_at=datetime.now(),
            payment_method=payment_method,
            payment_reference=payment_reference,
            bank_details=bank_details
        )
        
        self.status = ReimbursementStatus.PAID
        self.updated_by = paid_by
        self.updated_at = datetime.now()
        
    
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
            uploaded_at=datetime.now(),
            uploaded_by=uploaded_by
        )
        
        self.updated_by = uploaded_by
        self.updated_at = datetime.now()
    
    def _validate_submission(self):
        """Validate reimbursement before submission"""
        # Check if receipt is required
        if self.reimbursement_type.is_receipt_required and not self.receipt:
            raise ValueError("Receipt is required for this reimbursement type")
        
        # Check amount limits
        if self.reimbursement_type.max_limit is not None:
            limit_amount = self.reimbursement_type.max_limit
            # Convert ReimbursementAmount to Decimal for comparison
            amount_decimal = self.amount.amount if hasattr(self.amount, 'amount') else self.amount
            if amount_decimal > limit_amount:
                raise ValueError("Amount exceeds the limit for this reimbursement type")
    
    def _auto_approve(self):
        """Auto-approve reimbursement if eligible"""
        if not self.reimbursement_type.is_approval_required:
            return
        
        # Additional checks for auto-approval
        if self.reimbursement_type.max_limit is not None:
            limit_amount = self.reimbursement_type.max_limit
            # Convert ReimbursementAmount to Decimal for comparison
            amount_decimal = self.amount.amount if hasattr(self.amount, 'amount') else self.amount
            if amount_decimal > limit_amount:
                return  # Don't auto-approve if over limit
        
        self.approve_request(
            approved_by="system",
            approved_amount=self.amount,
            comments="Auto-approved based on reimbursement type settings"
        )
    
    def get_final_amount(self) -> Decimal:
        """Get final approved/paid amount"""
        if self.approval:
            return self.approval.approved_amount
        return self.amount
    
    def is_pending_approval(self) -> bool:
        """Check if reimbursement is pending approval"""
        return self.status in [ReimbursementStatus.DRAFT, ReimbursementStatus.SUBMITTED, ReimbursementStatus.UNDER_REVIEW]
    
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
    
    def get_domain_events(self) -> List:
        """Get domain events (placeholder implementation)"""
        # TODO: Implement proper domain events collection
        return []
    
    def clear_domain_events(self):
        """Clear domain events (placeholder implementation)"""
        # TODO: Implement proper domain events clearing
        pass
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "reimbursement_id": self.reimbursement_id,
            "employee_id": self.employee_id.value,
            "reimbursement_type": self.reimbursement_type.to_dict(),
            "amount": self.amount,
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
                "approved_amount": self.approval.approved_amount,
                "comments": self.approval.comments
            } if self.approval else None,
            "rejection": {
                "rejected_by": self.rejection.rejected_by,
                "rejected_at": self.rejection.rejected_at.isoformat(),
                "comments": self.rejection.comments
            } if self.rejection else None,
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