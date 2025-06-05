"""
Public Holiday Domain Entity
Aggregate root for public holiday management
"""

import uuid
from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class PublicHoliday:
    """
    Public Holiday aggregate root.
    
    Follows SOLID principles:
    - SRP: Manages public holiday business logic
    - OCP: Extensible through composition and events
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for holiday operations
    - DIP: Depends on value objects and events
    """
    
    holiday_id: str
    holiday_name: str
    holiday_date: date
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    description: Optional[str] = None
    location_specific: Optional[str] = None  # For regional holidays
    
    def __post_init__(self):
        """Validate public holiday data"""
        if not self.holiday_id:
            raise ValueError("Holiday ID cannot be empty")
        
        if not self.holiday_name:
            raise ValueError("Holiday name cannot be empty")
        
        if not isinstance(self.holiday_date, date):
            raise ValueError("Holiday date must be a valid date")
        
        # Business rule: Past holidays cannot be created as active
        if self.is_active and self.holiday_date < date.today():
            raise ValueError("Cannot create active holidays for past dates")
    
    @classmethod
    def create_holiday(
        cls,
        holiday_name: str,
        holiday_date: date,
        created_by: str,
        description: Optional[str] = None,
        location_specific: Optional[str] = None
    ) -> 'PublicHoliday':
        """Factory method for creating national holidays"""
        holiday_id = str(uuid.uuid4())
        
        
        holiday = cls(
            holiday_id=holiday_id,
            holiday_name=holiday_name,
            holiday_date=holiday_date,
            created_by=created_by,
            description=description,
            location_specific=location_specific
        )
        
        return holiday
    
    def change_date(
        self,
        new_date: date,
        updated_by: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """Change holiday date"""
        old_date = self.holiday_date
        
        # Business rule: Cannot change date to past for active holidays
        if self.is_active and new_date < date.today():
            raise ValueError("Cannot change active holiday to past date")
        
        self.holiday_date = new_date
        self.updated_by = updated_by
        self.updated_at = datetime.now()
    
    def activate(self, updated_by: Optional[str] = None):
        """Activate holiday"""
        if self.is_active:
            return  # Already active
        
        # Business rule: Cannot activate past holidays
        if self.holiday_date < date.today():
            raise ValueError("Cannot activate holidays for past dates")
        
        self.is_active = True
        self.updated_by = updated_by
        self.updated_at = datetime.now()
        
    
    def deactivate(self, updated_by: Optional[str] = None, reason: Optional[str] = None):
        """Deactivate holiday"""
        if not self.is_active:
            return  # Already inactive
        
        self.is_active = False
        self.updated_by = updated_by
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "holiday_id": self.holiday_id,
            "holiday_name": self.holiday_name,
            "holiday_date": self.holiday_date,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "description": self.description,
            "location_specific": self.location_specific
        } 