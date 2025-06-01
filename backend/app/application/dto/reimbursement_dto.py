"""
Reimbursement Data Transfer Objects
DTOs for reimbursement API operations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from decimal import Decimal
from pydantic import BaseModel, Field, validator


# Request DTOs

class ReimbursementTypeCreateRequestDTO(BaseModel):
    """DTO for creating reimbursement types"""
    
    code: str = Field(..., min_length=1, max_length=20, description="Reimbursement type code")
    name: str = Field(..., min_length=1, max_length=100, description="Reimbursement type name")
    category: str = Field(..., description="Reimbursement category")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    max_limit: Optional[Decimal] = Field(None, ge=0, description="Maximum limit")
    frequency: str = Field("unlimited", description="Frequency limit")
    approval_level: str = Field("manager", description="Required approval level")
    requires_receipt: bool = Field(True, description="Whether receipt is required")
    tax_applicable: bool = Field(False, description="Whether tax is applicable")
    
    @validator('code')
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError("Code cannot be empty")
        return v.upper().strip()
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = [
            "travel", "medical", "food", "accommodation", "communication",
            "office_supplies", "training", "entertainment", "fuel", "maintenance", "miscellaneous"
        ]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v
    
    @validator('frequency')
    def validate_frequency(cls, v):
        valid_frequencies = ["daily", "weekly", "monthly", "quarterly", "annually", "unlimited"]
        if v not in valid_frequencies:
            raise ValueError(f"Frequency must be one of: {', '.join(valid_frequencies)}")
        return v
    
    @validator('approval_level')
    def validate_approval_level(cls, v):
        valid_levels = ["auto_approve", "manager", "admin", "finance", "multi_level"]
        if v not in valid_levels:
            raise ValueError(f"Approval level must be one of: {', '.join(valid_levels)}")
        return v


class ReimbursementTypeUpdateRequestDTO(BaseModel):
    """DTO for updating reimbursement types"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Reimbursement type name")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    max_limit: Optional[Decimal] = Field(None, ge=0, description="Maximum limit")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v


class ReimbursementRequestCreateDTO(BaseModel):
    """DTO for creating reimbursement requests"""
    
    employee_id: str = Field(..., description="Employee ID")
    reimbursement_type_id: str = Field(..., description="Reimbursement type ID")
    amount: Decimal = Field(..., gt=0, description="Reimbursement amount")
    currency: str = Field("INR", description="Currency")
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Employee ID cannot be empty")
        return v.strip()
    
    @validator('reimbursement_type_id')
    def validate_reimbursement_type_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Reimbursement type ID cannot be empty")
        return v.strip()
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        if v > Decimal('9999999.99'):
            raise ValueError("Amount cannot exceed ₹99,99,999.99")
        return v


class ReimbursementRequestUpdateDTO(BaseModel):
    """DTO for updating reimbursement requests"""
    
    amount: Optional[Decimal] = Field(None, gt=0, description="Reimbursement amount")
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("Amount must be positive")
            if v > Decimal('9999999.99'):
                raise ValueError("Amount cannot exceed ₹99,99,999.99")
        return v


class ReimbursementApprovalDTO(BaseModel):
    """DTO for approving reimbursement requests"""
    
    approved_amount: Optional[Decimal] = Field(None, gt=0, description="Approved amount")
    approval_level: str = Field("manager", description="Approval level")
    comments: Optional[str] = Field(None, max_length=1000, description="Approval comments")
    
    @validator('approved_amount')
    def validate_approved_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("Approved amount must be positive")
            if v > Decimal('9999999.99'):
                raise ValueError("Approved amount cannot exceed ₹99,99,999.99")
        return v
    
    @validator('approval_level')
    def validate_approval_level(cls, v):
        valid_levels = ["manager", "admin", "finance", "auto"]
        if v not in valid_levels:
            raise ValueError(f"Approval level must be one of: {', '.join(valid_levels)}")
        return v


class ReimbursementRejectionDTO(BaseModel):
    """DTO for rejecting reimbursement requests"""
    
    rejection_reason: str = Field(..., min_length=1, max_length=1000, description="Rejection reason")
    
    @validator('rejection_reason')
    def validate_rejection_reason(cls, v):
        if not v or not v.strip():
            raise ValueError("Rejection reason cannot be empty")
        return v.strip()


class ReimbursementPaymentDTO(BaseModel):
    """DTO for processing reimbursement payments"""
    
    payment_method: str = Field(..., description="Payment method")
    payment_reference: Optional[str] = Field(None, max_length=100, description="Payment reference")
    bank_details: Optional[str] = Field(None, max_length=500, description="Bank details")
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        valid_methods = ["bank_transfer", "cash", "cheque", "digital_wallet"]
        if v not in valid_methods:
            raise ValueError(f"Payment method must be one of: {', '.join(valid_methods)}")
        return v


class ReimbursementReceiptUploadDTO(BaseModel):
    """DTO for uploading receipts"""
    
    file_name: str = Field(..., min_length=1, max_length=255, description="File name")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    
    @validator('file_name')
    def validate_file_name(cls, v):
        if not v or not v.strip():
            raise ValueError("File name cannot be empty")
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"File must have one of these extensions: {', '.join(allowed_extensions)}")
        
        return v.strip()
    
    @validator('file_size')
    def validate_file_size(cls, v):
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError("File size cannot exceed 10MB")
        return v


# Response DTOs

@dataclass
class ReimbursementTypeResponseDTO:
    """DTO for reimbursement type responses"""
    
    type_id: str
    code: str
    name: str
    category: str
    description: Optional[str]
    max_limit: Optional[Decimal]
    frequency: str
    approval_level: str
    requires_receipt: bool
    tax_applicable: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type_id": self.type_id,
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "max_limit": float(self.max_limit) if self.max_limit else None,
            "frequency": self.frequency,
            "approval_level": self.approval_level,
            "requires_receipt": self.requires_receipt,
            "tax_applicable": self.tax_applicable,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }


@dataclass
class ReimbursementResponseDTO:
    """DTO for reimbursement responses"""
    
    request_id: str
    employee_id: str
    reimbursement_type: ReimbursementTypeResponseDTO
    amount: Decimal
    currency: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    
    # Receipt information
    receipt_file_name: Optional[str] = None
    receipt_uploaded_at: Optional[datetime] = None
    
    # Approval information
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_amount: Optional[Decimal] = None
    approval_level: Optional[str] = None
    approval_comments: Optional[str] = None
    
    # Rejection information
    rejection_reason: Optional[str] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    
    # Payment information
    paid_by: Optional[str] = None
    paid_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    
    # Audit fields
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "employee_id": self.employee_id,
            "reimbursement_type": self.reimbursement_type.to_dict(),
            "amount": float(self.amount),
            "currency": self.currency,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "receipt": {
                "file_name": self.receipt_file_name,
                "uploaded_at": self.receipt_uploaded_at.isoformat() if self.receipt_uploaded_at else None
            } if self.receipt_file_name else None,
            "approval": {
                "approved_by": self.approved_by,
                "approved_at": self.approved_at.isoformat() if self.approved_at else None,
                "approved_amount": float(self.approved_amount) if self.approved_amount else None,
                "approval_level": self.approval_level,
                "comments": self.approval_comments
            } if self.approved_by else None,
            "rejection": {
                "reason": self.rejection_reason,
                "rejected_by": self.rejected_by,
                "rejected_at": self.rejected_at.isoformat() if self.rejected_at else None
            } if self.rejection_reason else None,
            "payment": {
                "paid_by": self.paid_by,
                "paid_at": self.paid_at.isoformat() if self.paid_at else None,
                "payment_method": self.payment_method,
                "payment_reference": self.payment_reference
            } if self.paid_by else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }


@dataclass
class ReimbursementSummaryDTO:
    """DTO for reimbursement summary responses"""
    
    request_id: str
    employee_id: str
    reimbursement_type_name: str
    amount: Decimal
    currency: str
    status: str
    submitted_at: Optional[datetime]
    final_amount: Optional[Decimal] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "employee_id": self.employee_id,
            "reimbursement_type_name": self.reimbursement_type_name,
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "final_amount": float(self.final_amount) if self.final_amount else None
        }


@dataclass
class ReimbursementStatisticsDTO:
    """DTO for reimbursement statistics"""
    
    total_requests: int
    total_amount: Decimal
    approved_requests: int
    approved_amount: Decimal
    pending_requests: int
    pending_amount: Decimal
    rejected_requests: int
    rejected_amount: Decimal
    paid_requests: int
    paid_amount: Decimal
    
    # Category breakdown
    category_breakdown: Dict[str, Dict[str, Any]]
    
    # Status breakdown
    status_breakdown: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "total_amount": float(self.total_amount),
            "approved_requests": self.approved_requests,
            "approved_amount": float(self.approved_amount),
            "pending_requests": self.pending_requests,
            "pending_amount": float(self.pending_amount),
            "rejected_requests": self.rejected_requests,
            "rejected_amount": float(self.rejected_amount),
            "paid_requests": self.paid_requests,
            "paid_amount": float(self.paid_amount),
            "category_breakdown": self.category_breakdown,
            "status_breakdown": self.status_breakdown
        }


# Utility DTOs

@dataclass
class ReimbursementTypeOptionsDTO:
    """DTO for reimbursement type options"""
    
    type_id: str
    code: str
    name: str
    category: str
    max_limit: Optional[Decimal]
    requires_receipt: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type_id": self.type_id,
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "max_limit": float(self.max_limit) if self.max_limit else None,
            "requires_receipt": self.requires_receipt
        }


# Search and Filter DTOs

class ReimbursementSearchFiltersDTO(BaseModel):
    """DTO for reimbursement search filters"""
    
    employee_id: Optional[str] = Field(None, description="Filter by employee ID")
    reimbursement_type_id: Optional[str] = Field(None, description="Filter by reimbursement type")
    status: Optional[str] = Field(None, description="Filter by status")
    category: Optional[str] = Field(None, description="Filter by category")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum amount")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Maximum amount")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    approved_by: Optional[str] = Field(None, description="Filter by approver")
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["draft", "submitted", "under_review", "approved", "rejected", "cancelled", "paid"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            valid_categories = [
                "travel", "medical", "food", "accommodation", "communication",
                "office_supplies", "training", "entertainment", "fuel", "maintenance", "miscellaneous"
            ]
            if v not in valid_categories:
                raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v


# Exception DTOs

class ReimbursementValidationError(Exception):
    """Custom exception for reimbursement validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class ReimbursementBusinessRuleError(Exception):
    """Exception raised for business rule violations in reimbursement operations"""
    def __init__(self, message: str, rule_code: str = None):
        super().__init__(message)
        self.message = message
        self.rule_code = rule_code


class ReimbursementNotFoundError(Exception):
    """Exception raised when reimbursement is not found"""
    def __init__(self, message: str, request_id: str = None):
        super().__init__(message)
        self.message = message
        self.request_id = request_id


# Utility functions

def create_reimbursement_type_response_from_entity(entity) -> ReimbursementTypeResponseDTO:
    """Create response DTO from reimbursement type entity"""
    return ReimbursementTypeResponseDTO(
        type_id=entity.type_id,
        code=entity.reimbursement_type.code,
        name=entity.reimbursement_type.name,
        category=entity.reimbursement_type.category.value,
        description=entity.reimbursement_type.description,
        max_limit=entity.reimbursement_type.max_limit,
        frequency=entity.reimbursement_type.frequency.value,
        approval_level=entity.reimbursement_type.approval_level.value,
        requires_receipt=entity.reimbursement_type.requires_receipt,
        tax_applicable=entity.reimbursement_type.tax_applicable,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        created_by=entity.created_by,
        updated_by=entity.updated_by
    )


def create_reimbursement_response_from_entity(entity, reimbursement_type_entity) -> ReimbursementResponseDTO:
    """Create response DTO from reimbursement entity"""
    reimbursement_type_dto = create_reimbursement_type_response_from_entity(reimbursement_type_entity)
    
    return ReimbursementResponseDTO(
        request_id=entity.request_id,
        employee_id=entity.employee_id.value,
        reimbursement_type=reimbursement_type_dto,
        amount=entity.amount.amount,
        currency=entity.amount.currency,
        description=entity.description,
        status=entity.status.value,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        submitted_at=entity.submitted_at,
        receipt_file_name=entity.receipt.file_name if entity.receipt else None,
        receipt_uploaded_at=entity.receipt.uploaded_at if entity.receipt else None,
        approved_by=entity.approval.approved_by if entity.approval else None,
        approved_at=entity.approval.approved_at if entity.approval else None,
        approved_amount=entity.approval.approved_amount.amount if entity.approval else None,
        approval_level=entity.approval.approval_level if entity.approval else None,
        approval_comments=entity.approval.comments if entity.approval else None,
        rejection_reason=entity.rejection_reason,
        rejected_by=entity.rejected_by,
        rejected_at=entity.rejected_at,
        paid_by=entity.payment.paid_by if entity.payment else None,
        paid_at=entity.payment.paid_at if entity.payment else None,
        payment_method=entity.payment.payment_method.value if entity.payment else None,
        payment_reference=entity.payment.payment_reference if entity.payment else None,
        created_by=entity.created_by,
        updated_by=entity.updated_by
    ) 