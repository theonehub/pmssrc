"""
Reimbursement Type Value Object
Immutable representation of reimbursement types and categories
"""

from typing import Optional
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ReimbursementType:
    """
    Value object representing a reimbursement type.
    
    Follows SOLID principles:
    - SRP: Only represents reimbursement type data
    - OCP: Extensible through composition
    - LSP: Maintains value object contracts
    - ISP: Focused interface for reimbursement types
    - DIP: No dependencies on external systems
    """
    
    reimbursement_type_id: str
    category_name: str
    description: Optional[str] = None
    max_limit: Optional[Decimal] = None
    is_approval_required: bool = True
    is_receipt_required: bool = True
    is_active: bool = True
    
    def __post_init__(self):
        """Validate reimbursement type data"""
        if not self.reimbursement_type_id or len(self.reimbursement_type_id.strip()) == 0:
            raise ValueError("Reimbursement type id cannot be empty")
        
        if not self.category_name or len(self.category_name.strip()) == 0:
            raise ValueError("Reimbursement type category name cannot be empty")
        
        if len(self.reimbursement_type_id) > 50:
            raise ValueError("Reimbursement type id cannot exceed 50 characters")
        
        if len(self.category_name) > 100:    
            raise ValueError("Reimbursement type category name cannot exceed 100 characters")
        
        if self.max_limit is not None and self.max_limit <= 0:
            raise ValueError("Maximum limit must be positive")
        
        # Ensure reimbursement type id is uppercase
        object.__setattr__(self, 'category_name', self.category_name.strip())
    
    def is_approval_required_check(self) -> bool:
        """Check if approval is required"""
        return self.is_approval_required
    
    def is_receipt_required_check(self) -> bool:
        """Check if receipt is required"""
        return self.is_receipt_required
    
    def has_limit(self) -> bool:
        """Check if reimbursement type has a limit"""
        return self.max_limit is not None
    
    def is_within_limit(self, amount: Decimal) -> bool:
        """Check if amount is within the limit"""
        if not self.has_limit():
            return True
        return amount <= self.max_limit
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "reimbursement_type_id": self.reimbursement_type_id,
            "category_name": self.category_name,
            "description": self.description,
            "max_limit": float(self.max_limit) if self.max_limit else None,
            "is_approval_required": self.is_approval_required,
            "is_receipt_required": self.is_receipt_required,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ReimbursementType':
        """Create from dictionary"""
        return cls(
            reimbursement_type_id=data["reimbursement_type_id"],
            category_name=data["category_name"],
            description=data.get("description"),
            max_limit=Decimal(str(data["max_limit"])) if data.get("max_limit") else None,
            is_approval_required=data.get("is_approval_required", True),
            is_receipt_required=data.get("is_receipt_required", True),
            is_active=data.get("is_active", True)
        )