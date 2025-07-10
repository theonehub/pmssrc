"""
Company Leave Domain Entity
Aggregate root for company leave policies and configurations
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from uuid import uuid4

@dataclass
class CompanyLeave:
    """
    Company Leave aggregate root following DDD principles.
    
    Follows SOLID principles:
    - SRP: Only handles company leave policy management
    - OCP: Can be extended with new leave types without modification
    - LSP: Can be substituted anywhere CompanyLeave is expected
    - ISP: Provides focused leave policy operations
    - DIP: Depends on abstractions (value objects, events)
    """
    
    # Identity
    company_leave_id: str
    leave_name: str  # This acts as both the type and name (e.g., "Casual Leave", "Sick Leave")
    accrual_type: str
    annual_allocation: int
    encashable: bool = False
    computed_monthly_allocation: int = 0
    is_active: bool = True
    description: Optional[str] = None
    
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        """Post initialization validation"""
        self._validate_company_leave_data()
    
    @classmethod
    def create_new_company_leave(
        cls,
        leave_name: str,
        accrual_type: str,
        annual_allocation: int,
        created_by: str,
        is_active: bool = True,
        description: Optional[str] = None,
        encashable: bool = False
    ) -> 'CompanyLeave':
        """Factory method to create new company leave"""
        
        company_leave_id = str(uuid4())
        
        company_leave = cls(
            company_leave_id=company_leave_id,
            leave_name=leave_name,
            accrual_type=accrual_type,
            annual_allocation=annual_allocation,
            computed_monthly_allocation=annual_allocation / 12,
            created_by=created_by,
            is_active=is_active,
            description=description,
            encashable=encashable
        )
        
        return company_leave
    
    def update_company_leave(
        self,
        leave_name: str,
        accrual_type: str,
        annual_allocation: int,
        updated_by: str,
        is_active: bool = True,
        description: Optional[str] = None,
        encashable: Optional[bool] = None
    ) -> 'CompanyLeave':
        """Update company leave"""
        
        self.leave_name = leave_name
        self.accrual_type = accrual_type
        self.is_active = is_active  
        self.annual_allocation = annual_allocation
        self.computed_monthly_allocation = annual_allocation / 12
        self.description = description
        
        if encashable is not None:
            self.encashable = encashable
            
        self.updated_at = datetime.now()
        self.updated_by = updated_by
        
        return self
    
    def deactivate(self, deactivated_by: str):
        """Deactivate company leave"""
        
        if not self.is_active:
            raise ValueError("Company leave is already deactivated")
        
        self.is_active = False
        self.updated_at = datetime.now()
        self.updated_by = deactivated_by
        
        return self
    
    def activate(self, activated_by: str):
        """Activate company leave"""
        
        if self.is_active:
            raise ValueError("Company leave is already activated")
        
        self.is_active = True
        self.updated_at = datetime.now()
        self.updated_by = activated_by
        
        return self
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "company_leave_id": self.company_leave_id,
            "leave_name": self.leave_name,
            "accrual_type": self.accrual_type,
            "annual_allocation": self.annual_allocation,
            "computed_monthly_allocation": self.computed_monthly_allocation,
            "is_active": self.is_active,
            "description": self.description,
            "encashable": self.encashable,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }
    
    def __str__(self) -> str:
        """String representation"""
        return f"CompanyLeave(id={self.company_leave_id}, leave_name={self.leave_name}, accrual={self.accrual_type})"
    
    def _validate_company_leave_data(self):
        """Validate company leave data"""
        if not self.company_leave_id:
            raise ValueError("Company leave ID is required")
        
        if not self.leave_name:
            raise ValueError("Leave name is required")
        
        if not self.accrual_type:
            raise ValueError("Accrual type is required")
        
        if self.annual_allocation < 0:
            raise ValueError("Annual allocation must be non-negative")
    