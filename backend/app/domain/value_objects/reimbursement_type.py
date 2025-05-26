"""
Reimbursement Type Value Object
Immutable representation of reimbursement types and categories
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass
from decimal import Decimal


class ReimbursementCategory(Enum):
    """Enumeration of reimbursement categories"""
    TRAVEL = "travel"
    MEDICAL = "medical"
    FOOD = "food"
    ACCOMMODATION = "accommodation"
    COMMUNICATION = "communication"
    OFFICE_SUPPLIES = "office_supplies"
    TRAINING = "training"
    ENTERTAINMENT = "entertainment"
    FUEL = "fuel"
    MAINTENANCE = "maintenance"
    MISCELLANEOUS = "miscellaneous"


class ReimbursementFrequency(Enum):
    """Enumeration of reimbursement frequency limits"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    UNLIMITED = "unlimited"


class ReimbursementApprovalLevel(Enum):
    """Enumeration of approval levels required"""
    AUTO_APPROVE = "auto_approve"
    MANAGER = "manager"
    ADMIN = "admin"
    FINANCE = "finance"
    MULTI_LEVEL = "multi_level"


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
    
    code: str
    name: str
    category: ReimbursementCategory
    description: Optional[str] = None
    max_limit: Optional[Decimal] = None
    frequency: ReimbursementFrequency = ReimbursementFrequency.UNLIMITED
    approval_level: ReimbursementApprovalLevel = ReimbursementApprovalLevel.MANAGER
    requires_receipt: bool = True
    tax_applicable: bool = False
    
    def __post_init__(self):
        """Validate reimbursement type data"""
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("Reimbursement type code cannot be empty")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Reimbursement type name cannot be empty")
        
        if len(self.code) > 20:
            raise ValueError("Reimbursement type code cannot exceed 20 characters")
        
        if len(self.name) > 100:
            raise ValueError("Reimbursement type name cannot exceed 100 characters")
        
        if self.max_limit is not None and self.max_limit <= 0:
            raise ValueError("Maximum limit must be positive")
        
        # Ensure code is uppercase
        object.__setattr__(self, 'code', self.code.upper().strip())
        object.__setattr__(self, 'name', self.name.strip())
    
    @classmethod
    def travel_expense(
        cls,
        code: str,
        name: str,
        max_limit: Optional[Decimal] = None,
        description: Optional[str] = None
    ) -> 'ReimbursementType':
        """Factory method for travel expenses"""
        return cls(
            code=code,
            name=name,
            category=ReimbursementCategory.TRAVEL,
            description=description,
            max_limit=max_limit,
            frequency=ReimbursementFrequency.MONTHLY,
            approval_level=ReimbursementApprovalLevel.MANAGER,
            requires_receipt=True,
            tax_applicable=False
        )
    
    @classmethod
    def medical_expense(
        cls,
        code: str,
        name: str,
        max_limit: Optional[Decimal] = None,
        description: Optional[str] = None
    ) -> 'ReimbursementType':
        """Factory method for medical expenses"""
        return cls(
            code=code,
            name=name,
            category=ReimbursementCategory.MEDICAL,
            description=description,
            max_limit=max_limit,
            frequency=ReimbursementFrequency.ANNUALLY,
            approval_level=ReimbursementApprovalLevel.ADMIN,
            requires_receipt=True,
            tax_applicable=True
        )
    
    @classmethod
    def food_expense(
        cls,
        code: str,
        name: str,
        max_limit: Optional[Decimal] = None,
        description: Optional[str] = None
    ) -> 'ReimbursementType':
        """Factory method for food expenses"""
        return cls(
            code=code,
            name=name,
            category=ReimbursementCategory.FOOD,
            description=description,
            max_limit=max_limit,
            frequency=ReimbursementFrequency.DAILY,
            approval_level=ReimbursementApprovalLevel.AUTO_APPROVE,
            requires_receipt=False,
            tax_applicable=False
        )
    
    @classmethod
    def communication_expense(
        cls,
        code: str,
        name: str,
        max_limit: Optional[Decimal] = None,
        description: Optional[str] = None
    ) -> 'ReimbursementType':
        """Factory method for communication expenses"""
        return cls(
            code=code,
            name=name,
            category=ReimbursementCategory.COMMUNICATION,
            description=description,
            max_limit=max_limit,
            frequency=ReimbursementFrequency.MONTHLY,
            approval_level=ReimbursementApprovalLevel.MANAGER,
            requires_receipt=True,
            tax_applicable=False
        )
    
    @classmethod
    def training_expense(
        cls,
        code: str,
        name: str,
        max_limit: Optional[Decimal] = None,
        description: Optional[str] = None
    ) -> 'ReimbursementType':
        """Factory method for training expenses"""
        return cls(
            code=code,
            name=name,
            category=ReimbursementCategory.TRAINING,
            description=description,
            max_limit=max_limit,
            frequency=ReimbursementFrequency.ANNUALLY,
            approval_level=ReimbursementApprovalLevel.ADMIN,
            requires_receipt=True,
            tax_applicable=True
        )
    
    def is_auto_approved(self) -> bool:
        """Check if reimbursement type is auto-approved"""
        return self.approval_level == ReimbursementApprovalLevel.AUTO_APPROVE
    
    def requires_manager_approval(self) -> bool:
        """Check if manager approval is required"""
        return self.approval_level in [
            ReimbursementApprovalLevel.MANAGER,
            ReimbursementApprovalLevel.MULTI_LEVEL
        ]
    
    def requires_admin_approval(self) -> bool:
        """Check if admin approval is required"""
        return self.approval_level in [
            ReimbursementApprovalLevel.ADMIN,
            ReimbursementApprovalLevel.FINANCE,
            ReimbursementApprovalLevel.MULTI_LEVEL
        ]
    
    def has_limit(self) -> bool:
        """Check if reimbursement type has a limit"""
        return self.max_limit is not None
    
    def is_within_limit(self, amount: Decimal) -> bool:
        """Check if amount is within the limit"""
        if not self.has_limit():
            return True
        return amount <= self.max_limit
    
    def is_travel_related(self) -> bool:
        """Check if reimbursement is travel-related"""
        return self.category in [
            ReimbursementCategory.TRAVEL,
            ReimbursementCategory.ACCOMMODATION,
            ReimbursementCategory.FUEL
        ]
    
    def is_medical_related(self) -> bool:
        """Check if reimbursement is medical-related"""
        return self.category == ReimbursementCategory.MEDICAL
    
    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.name} ({self.code})"
    
    def get_limit_display(self) -> str:
        """Get formatted limit display"""
        if not self.has_limit():
            return "No Limit"
        return f"₹{self.max_limit:,.2f} per {self.frequency.value}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "code": self.code,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "max_limit": float(self.max_limit) if self.max_limit else None,
            "frequency": self.frequency.value,
            "approval_level": self.approval_level.value,
            "requires_receipt": self.requires_receipt,
            "tax_applicable": self.tax_applicable
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ReimbursementType':
        """Create from dictionary"""
        return cls(
            code=data["code"],
            name=data["name"],
            category=ReimbursementCategory(data["category"]),
            description=data.get("description"),
            max_limit=Decimal(str(data["max_limit"])) if data.get("max_limit") else None,
            frequency=ReimbursementFrequency(data.get("frequency", "unlimited")),
            approval_level=ReimbursementApprovalLevel(data.get("approval_level", "manager")),
            requires_receipt=data.get("requires_receipt", True),
            tax_applicable=data.get("tax_applicable", False)
        )


# Common reimbursement types for easy reference
class CommonReimbursementTypes:
    """Common reimbursement type definitions"""
    
    TRAVEL_LOCAL = ReimbursementType.travel_expense(
        "TRAVEL_LOCAL", "Local Travel", Decimal("5000"), "Local transportation expenses"
    )
    
    TRAVEL_OUTSTATION = ReimbursementType.travel_expense(
        "TRAVEL_OUT", "Outstation Travel", Decimal("25000"), "Outstation travel expenses"
    )
    
    MEDICAL_GENERAL = ReimbursementType.medical_expense(
        "MEDICAL_GEN", "Medical Expenses", Decimal("50000"), "General medical expenses"
    )
    
    FOOD_ALLOWANCE = ReimbursementType.food_expense(
        "FOOD_ALLOW", "Food Allowance", Decimal("500"), "Daily food allowance"
    )
    
    MOBILE_BILL = ReimbursementType.communication_expense(
        "MOBILE", "Mobile Bill", Decimal("2000"), "Monthly mobile bill reimbursement"
    )
    
    INTERNET_BILL = ReimbursementType.communication_expense(
        "INTERNET", "Internet Bill", Decimal("1500"), "Monthly internet bill reimbursement"
    )
    
    TRAINING_COURSE = ReimbursementType.training_expense(
        "TRAINING", "Training Course", Decimal("100000"), "Professional training courses"
    )
    
    FUEL_EXPENSE = ReimbursementType(
        code="FUEL",
        name="Fuel Expense",
        category=ReimbursementCategory.FUEL,
        description="Vehicle fuel expenses",
        max_limit=Decimal("10000"),
        frequency=ReimbursementFrequency.MONTHLY,
        approval_level=ReimbursementApprovalLevel.MANAGER,
        requires_receipt=True,
        tax_applicable=False
    ) 