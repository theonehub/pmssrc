"""
Public Holiday Domain Entity
Rich domain entity for public holiday management
"""

import uuid
from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass, field

from app.domain.value_objects.public_holiday_id import PublicHolidayId


@dataclass
class PublicHoliday:
    """
    Public Holiday domain entity with rich behavior.
    
    Follows SOLID principles:
    - SRP: Manages public holiday business logic and state
    - OCP: Extensible through composition and events
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for holiday operations
    - DIP: Depends on value objects and abstractions
    """
    
    id: PublicHolidayId
    name: str
    date: date
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    location_specific: Optional[str] = None  # For regional holidays
    
    def __post_init__(self):
        """Initialize and validate public holiday data"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        
        self._validate()
    
    def _validate(self):
        """Validate public holiday data"""
        if not self.name or not self.name.strip():
            raise ValueError("Holiday name cannot be empty")
        
        if not isinstance(self.date, date):
            raise ValueError("Holiday date must be a valid date")
        
        if len(self.name.strip()) > 100:
            raise ValueError("Holiday name cannot exceed 100 characters")
        
        if self.description and len(self.description) > 500:
            raise ValueError("Holiday description cannot exceed 500 characters")
    
    @classmethod
    def create(
        cls,
        id: PublicHolidayId,
        name: str,
        date: date,
        description: Optional[str] = None,
        is_active: bool = True,
        created_by: Optional[str] = None,
        location_specific: Optional[str] = None
    ) -> 'PublicHoliday':
        """Factory method for creating new public holidays"""
        now = datetime.now()
        
        holiday = cls(
            id=id,
            name=name.strip(),
            date=date,
            description=description.strip() if description else None,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            location_specific=location_specific
        )
        
        return holiday
    
    def update(
        self,
        name: Optional[str] = None,
        date: Optional[date] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
        updated_by: Optional[str] = None,
        location_specific: Optional[str] = None
    ) -> 'PublicHoliday':
        """Update holiday details and return new instance (immutable pattern)"""
        return PublicHoliday(
            id=self.id,
            name=name.strip() if name is not None else self.name,
            date=date if date is not None else self.date,
            description=description.strip() if description is not None else self.description,
            is_active=is_active if is_active is not None else self.is_active,
            created_at=self.created_at,
            updated_at=datetime.now(),
            created_by=self.created_by,
            updated_by=updated_by,
            location_specific=location_specific if location_specific is not None else self.location_specific
        )
    
    def change_date(
        self,
        new_date: date,
        updated_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> 'PublicHoliday':
        """Change holiday date with business rule validation"""
        # Business rule: Cannot change date to past for active holidays
        if self.is_active and new_date < date.today():
            raise ValueError("Cannot change active holiday to past date")
        
        return self.update(date=new_date, updated_by=updated_by)
    
    def activate(self, updated_by: Optional[str] = None) -> 'PublicHoliday':
        """Activate holiday with business rule validation"""
        if self.is_active:
            return self  # Already active
        
        # Business rule: Cannot activate past holidays
        if self.date < date.today():
            raise ValueError("Cannot activate holidays for past dates")
        
        return self.update(is_active=True, updated_by=updated_by)
    
    def deactivate(self, updated_by: Optional[str] = None, reason: Optional[str] = None) -> 'PublicHoliday':
        """Deactivate holiday"""
        if not self.is_active:
            return self  # Already inactive
        
        return self.update(is_active=False, updated_by=updated_by)
    
    def is_in_past(self) -> bool:
        """Check if holiday is in the past"""
        return self.date < date.today()
    
    def is_today(self) -> bool:
        """Check if holiday is today"""
        return self.date == date.today()
    
    def is_upcoming(self) -> bool:
        """Check if holiday is upcoming"""
        return self.date > date.today()
    
    def days_until(self) -> int:
        """Get number of days until holiday (negative if past)"""
        return (self.date - date.today()).days
    
    def is_new(self) -> bool:
        """Check if this is a new holiday (not yet persisted)"""
        return self.created_at is None or self.updated_at is None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "id": str(self.id),
            "name": self.name,
            "date": self.date.isoformat(),
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "location_specific": self.location_specific
        }
    
    def __str__(self) -> str:
        """String representation"""
        return f"PublicHoliday(id={self.id}, name='{self.name}', date={self.date})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return (f"PublicHoliday(id={self.id}, name='{self.name}', date={self.date}, "
                f"is_active={self.is_active})")
    
    def __eq__(self, other) -> bool:
        """Equality based on ID"""
        if isinstance(other, PublicHoliday):
            return self.id == other.id
        return False
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self.id) 