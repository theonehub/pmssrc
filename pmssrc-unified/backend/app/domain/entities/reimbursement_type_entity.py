"""
Reimbursement Type Domain Entity
Aggregate root for reimbursement type management
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from decimal import Decimal

from app.domain.value_objects.reimbursement_type import ReimbursementType as ReimbursementTypeVO



@dataclass
class ReimbursementTypeEntity:
    """
    Reimbursement Type aggregate root.
    
    Follows SOLID principles:
    - SRP: Manages reimbursement type business logic
    - OCP: Extensible through composition and events
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for reimbursement type operations
    - DIP: Depends on value objects and events
    """
    
    reimbursement_type_id: str  # This acts as the code
    category_name: str  # Display name
    description: Optional[str] = None
    max_limit: Optional[Decimal] = None
    is_approval_required: bool = True
    is_receipt_required: bool = True
    is_active: bool = True
    
    # Audit fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Computed properties for backward compatibility        
    @property
    def requires_receipt(self) -> bool:
        """Check if receipt is required (for backward compatibility)"""
        return self.is_receipt_required
        
    
    def get_category_name(self) -> str:
        """Get reimbursement type name"""
        return self.category_name
    
    def get_description(self) -> str:
        """Get reimbursement type description"""
        return self.description
    
    def get_max_limit(self) -> Optional[Decimal]:
        """Get maximum limit"""
        return self.max_limit
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "reimbursement_type_id": self.reimbursement_type_id,
            "category_name": self.category_name,
            "description": self.description,
            "max_limit": float(self.max_limit) if self.max_limit else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "is_approval_required": self.is_approval_required,
            "is_receipt_required": self.is_receipt_required,
        } 