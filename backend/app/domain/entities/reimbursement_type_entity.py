"""
Reimbursement Type Domain Entity
Aggregate root for reimbursement type management
"""

import uuid
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from decimal import Decimal

from app.domain.value_objects.reimbursement_type import ReimbursementType as ReimbursementTypeVO
from app.domain.value_objects.reimbursement_amount import ReimbursementAmount
from app.domain.events.reimbursement_events import (
    ReimbursementTypeCreated,
    ReimbursementTypeUpdated,
    ReimbursementTypeActivated,
    ReimbursementTypeDeactivated
)


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
    
    type_id: str
    reimbursement_type: ReimbursementTypeVO
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Domain events
    _domain_events: List = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate reimbursement type entity data"""
        if not self.type_id:
            raise ValueError("Reimbursement type ID cannot be empty")
        
        if not isinstance(self.reimbursement_type, ReimbursementTypeVO):
            raise ValueError("Reimbursement type must be a valid ReimbursementTypeVO")
    
    @classmethod
    def create_travel_type(
        cls,
        name: str,
        max_limit: Optional[Decimal] = None,
        created_by: str = "system",
        description: Optional[str] = None
    ) -> 'ReimbursementTypeEntity':
        """Factory method for creating travel reimbursement types"""
        type_id = str(uuid.uuid4())
        
        reimbursement_type = ReimbursementTypeVO.travel_expense(
            code=name.upper().replace(" ", "_")[:20],
            name=name,
            max_limit=max_limit,
            description=description
        )
        
        entity = cls(
            type_id=type_id,
            reimbursement_type=reimbursement_type,
            created_by=created_by
        )
        
        # Add domain event
        entity._add_domain_event(
            ReimbursementTypeCreated(
                type_id=type_id,
                reimbursement_type=reimbursement_type,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return entity
    
    @classmethod
    def create_medical_type(
        cls,
        name: str,
        max_limit: Optional[Decimal] = None,
        created_by: str = "system",
        description: Optional[str] = None
    ) -> 'ReimbursementTypeEntity':
        """Factory method for creating medical reimbursement types"""
        type_id = str(uuid.uuid4())
        
        reimbursement_type = ReimbursementTypeVO.medical_expense(
            code=name.upper().replace(" ", "_")[:20],
            name=name,
            max_limit=max_limit,
            description=description
        )
        
        entity = cls(
            type_id=type_id,
            reimbursement_type=reimbursement_type,
            created_by=created_by
        )
        
        # Add domain event
        entity._add_domain_event(
            ReimbursementTypeCreated(
                type_id=type_id,
                reimbursement_type=reimbursement_type,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return entity
    
    @classmethod
    def create_food_type(
        cls,
        name: str,
        max_limit: Optional[Decimal] = None,
        created_by: str = "system",
        description: Optional[str] = None
    ) -> 'ReimbursementTypeEntity':
        """Factory method for creating food reimbursement types"""
        type_id = str(uuid.uuid4())
        
        reimbursement_type = ReimbursementTypeVO.food_expense(
            code=name.upper().replace(" ", "_")[:20],
            name=name,
            max_limit=max_limit,
            description=description
        )
        
        entity = cls(
            type_id=type_id,
            reimbursement_type=reimbursement_type,
            created_by=created_by
        )
        
        # Add domain event
        entity._add_domain_event(
            ReimbursementTypeCreated(
                type_id=type_id,
                reimbursement_type=reimbursement_type,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return entity
    
    @classmethod
    def create_communication_type(
        cls,
        name: str,
        max_limit: Optional[Decimal] = None,
        created_by: str = "system",
        description: Optional[str] = None
    ) -> 'ReimbursementTypeEntity':
        """Factory method for creating communication reimbursement types"""
        type_id = str(uuid.uuid4())
        
        reimbursement_type = ReimbursementTypeVO.communication_expense(
            code=name.upper().replace(" ", "_")[:20],
            name=name,
            max_limit=max_limit,
            description=description
        )
        
        entity = cls(
            type_id=type_id,
            reimbursement_type=reimbursement_type,
            created_by=created_by
        )
        
        # Add domain event
        entity._add_domain_event(
            ReimbursementTypeCreated(
                type_id=type_id,
                reimbursement_type=reimbursement_type,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return entity
    
    @classmethod
    def create_custom_type(
        cls,
        reimbursement_type: ReimbursementTypeVO,
        created_by: str = "system"
    ) -> 'ReimbursementTypeEntity':
        """Factory method for creating custom reimbursement types"""
        type_id = str(uuid.uuid4())
        
        entity = cls(
            type_id=type_id,
            reimbursement_type=reimbursement_type,
            created_by=created_by
        )
        
        # Add domain event
        entity._add_domain_event(
            ReimbursementTypeCreated(
                type_id=type_id,
                reimbursement_type=reimbursement_type,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return entity
    
    def update_details(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        max_limit: Optional[Decimal] = None,
        updated_by: Optional[str] = None
    ):
        """Update reimbursement type details"""
        old_type = self.reimbursement_type
        
        # Create new reimbursement type with updated values
        new_type = ReimbursementTypeVO(
            code=self.reimbursement_type.code,
            name=name or self.reimbursement_type.name,
            category=self.reimbursement_type.category,
            description=description if description is not None else self.reimbursement_type.description,
            max_limit=max_limit if max_limit is not None else self.reimbursement_type.max_limit,
            frequency=self.reimbursement_type.frequency,
            approval_level=self.reimbursement_type.approval_level,
            requires_receipt=self.reimbursement_type.requires_receipt,
            tax_applicable=self.reimbursement_type.tax_applicable
        )
        
        self.reimbursement_type = new_type
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementTypeUpdated(
                type_id=self.type_id,
                old_reimbursement_type=old_type,
                new_reimbursement_type=new_type,
                updated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def update_limit(
        self,
        new_limit: Optional[Decimal],
        updated_by: Optional[str] = None
    ):
        """Update reimbursement type limit"""
        old_type = self.reimbursement_type
        
        # Create new reimbursement type with updated limit
        new_type = ReimbursementTypeVO(
            code=self.reimbursement_type.code,
            name=self.reimbursement_type.name,
            category=self.reimbursement_type.category,
            description=self.reimbursement_type.description,
            max_limit=new_limit,
            frequency=self.reimbursement_type.frequency,
            approval_level=self.reimbursement_type.approval_level,
            requires_receipt=self.reimbursement_type.requires_receipt,
            tax_applicable=self.reimbursement_type.tax_applicable
        )
        
        self.reimbursement_type = new_type
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementTypeUpdated(
                type_id=self.type_id,
                old_reimbursement_type=old_type,
                new_reimbursement_type=new_type,
                updated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def activate(self, updated_by: Optional[str] = None):
        """Activate reimbursement type"""
        if self.is_active:
            return  # Already active
        
        self.is_active = True
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementTypeActivated(
                type_id=self.type_id,
                reimbursement_type=self.reimbursement_type,
                activated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def deactivate(self, updated_by: Optional[str] = None, reason: Optional[str] = None):
        """Deactivate reimbursement type"""
        if not self.is_active:
            return  # Already inactive
        
        self.is_active = False
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            ReimbursementTypeDeactivated(
                type_id=self.type_id,
                reimbursement_type=self.reimbursement_type,
                reason=reason,
                deactivated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def validate_amount(self, amount: ReimbursementAmount) -> bool:
        """Validate if amount is within limits"""
        if not self.reimbursement_type.has_limit():
            return True
        
        limit_amount = ReimbursementAmount(self.reimbursement_type.max_limit, amount.currency)
        return not amount.is_greater_than(limit_amount)
    
    def get_name(self) -> str:
        """Get reimbursement type name"""
        return self.reimbursement_type.name
    
    def get_code(self) -> str:
        """Get reimbursement type code"""
        return self.reimbursement_type.code
    
    def get_category(self) -> str:
        """Get reimbursement type category"""
        return self.reimbursement_type.category.value
    
    def get_max_limit(self) -> Optional[Decimal]:
        """Get maximum limit"""
        return self.reimbursement_type.max_limit
    
    def requires_receipt(self) -> bool:
        """Check if receipt is required"""
        return self.reimbursement_type.requires_receipt
    
    def is_auto_approved(self) -> bool:
        """Check if auto-approved"""
        return self.reimbursement_type.is_auto_approved()
    
    def requires_manager_approval(self) -> bool:
        """Check if manager approval is required"""
        return self.reimbursement_type.requires_manager_approval()
    
    def requires_admin_approval(self) -> bool:
        """Check if admin approval is required"""
        return self.reimbursement_type.requires_admin_approval()
    
    def is_travel_related(self) -> bool:
        """Check if travel-related"""
        return self.reimbursement_type.is_travel_related()
    
    def is_medical_related(self) -> bool:
        """Check if medical-related"""
        return self.reimbursement_type.is_medical_related()
    
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
            "type_id": self.type_id,
            "reimbursement_type": self.reimbursement_type.to_dict(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by
        } 