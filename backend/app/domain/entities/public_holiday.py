"""
Public Holiday Domain Entity
Aggregate root for public holiday management
"""

import uuid
from datetime import datetime, date
from typing import Optional, List
from dataclasses import dataclass, field

from domain.value_objects.holiday_type import HolidayType, HolidayCategory, HolidayObservance, HolidayRecurrence
from domain.value_objects.holiday_date_range import HolidayDateRange
from domain.events.holiday_events import (
    PublicHolidayCreated,
    PublicHolidayUpdated,
    PublicHolidayActivated,
    PublicHolidayDeactivated,
    PublicHolidayDateChanged
)


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
    holiday_type: HolidayType
    date_range: HolidayDateRange
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    notes: Optional[str] = None
    location_specific: Optional[str] = None  # For regional holidays
    substitute_for: Optional[str] = None  # If this is a substitute holiday
    
    # Domain events
    _domain_events: List = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate public holiday data"""
        if not self.holiday_id:
            raise ValueError("Holiday ID cannot be empty")
        
        if not isinstance(self.holiday_type, HolidayType):
            raise ValueError("Holiday type must be a valid HolidayType")
        
        if not isinstance(self.date_range, HolidayDateRange):
            raise ValueError("Date range must be a valid HolidayDateRange")
        
        # Business rule: Past holidays cannot be created as active
        if self.is_active and self.date_range.is_past():
            raise ValueError("Cannot create active holidays for past dates")
    
    @classmethod
    def create_national_holiday(
        cls,
        name: str,
        holiday_date: date,
        created_by: str,
        description: Optional[str] = None,
        notes: Optional[str] = None
    ) -> 'PublicHoliday':
        """Factory method for creating national holidays"""
        holiday_id = str(uuid.uuid4())
        
        holiday_type = HolidayType.national_holiday(
            code=name.upper().replace(" ", "_")[:10],
            name=name,
            description=description
        )
        
        date_range = HolidayDateRange.single_day(holiday_date)
        
        holiday = cls(
            holiday_id=holiday_id,
            holiday_type=holiday_type,
            date_range=date_range,
            created_by=created_by,
            notes=notes
        )
        
        # Add domain event
        holiday._add_domain_event(
            PublicHolidayCreated(
                holiday_id=holiday_id,
                holiday_type=holiday_type,
                date_range=date_range,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return holiday
    
    @classmethod
    def create_religious_holiday(
        cls,
        name: str,
        holiday_date: date,
        created_by: str,
        is_lunar: bool = False,
        description: Optional[str] = None,
        notes: Optional[str] = None
    ) -> 'PublicHoliday':
        """Factory method for creating religious holidays"""
        holiday_id = str(uuid.uuid4())
        
        holiday_type = HolidayType.religious_holiday(
            code=name.upper().replace(" ", "_")[:10],
            name=name,
            description=description,
            is_lunar=is_lunar
        )
        
        date_range = HolidayDateRange.single_day(holiday_date)
        
        holiday = cls(
            holiday_id=holiday_id,
            holiday_type=holiday_type,
            date_range=date_range,
            created_by=created_by,
            notes=notes
        )
        
        # Add domain event
        holiday._add_domain_event(
            PublicHolidayCreated(
                holiday_id=holiday_id,
                holiday_type=holiday_type,
                date_range=date_range,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return holiday
    
    @classmethod
    def create_company_holiday(
        cls,
        name: str,
        holiday_date: date,
        created_by: str,
        description: Optional[str] = None,
        notes: Optional[str] = None
    ) -> 'PublicHoliday':
        """Factory method for creating company holidays"""
        holiday_id = str(uuid.uuid4())
        
        holiday_type = HolidayType.company_holiday(
            code=name.upper().replace(" ", "_")[:10],
            name=name,
            description=description
        )
        
        date_range = HolidayDateRange.single_day(holiday_date)
        
        holiday = cls(
            holiday_id=holiday_id,
            holiday_type=holiday_type,
            date_range=date_range,
            created_by=created_by,
            notes=notes
        )
        
        # Add domain event
        holiday._add_domain_event(
            PublicHolidayCreated(
                holiday_id=holiday_id,
                holiday_type=holiday_type,
                date_range=date_range,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return holiday
    
    @classmethod
    def create_multi_day_holiday(
        cls,
        name: str,
        start_date: date,
        end_date: date,
        category: HolidayCategory,
        created_by: str,
        description: Optional[str] = None,
        notes: Optional[str] = None
    ) -> 'PublicHoliday':
        """Factory method for creating multi-day holidays"""
        holiday_id = str(uuid.uuid4())
        
        holiday_type = HolidayType(
            code=name.upper().replace(" ", "_")[:10],
            name=name,
            category=category,
            observance=HolidayObservance.MANDATORY,
            recurrence=HolidayRecurrence.ANNUAL,
            description=description
        )
        
        date_range = HolidayDateRange.multi_day(start_date, end_date)
        
        holiday = cls(
            holiday_id=holiday_id,
            holiday_type=holiday_type,
            date_range=date_range,
            created_by=created_by,
            notes=notes
        )
        
        # Add domain event
        holiday._add_domain_event(
            PublicHolidayCreated(
                holiday_id=holiday_id,
                holiday_type=holiday_type,
                date_range=date_range,
                created_by=created_by,
                occurred_at=datetime.utcnow()
            )
        )
        
        return holiday
    
    def update_holiday_details(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None
    ):
        """Update holiday details"""
        old_type = self.holiday_type
        
        if name:
            # Create new holiday type with updated name
            self.holiday_type = HolidayType(
                code=self.holiday_type.code,
                name=name,
                category=self.holiday_type.category,
                observance=self.holiday_type.observance,
                recurrence=self.holiday_type.recurrence,
                description=description or self.holiday_type.description
            )
        elif description:
            # Update description only
            self.holiday_type = HolidayType(
                code=self.holiday_type.code,
                name=self.holiday_type.name,
                category=self.holiday_type.category,
                observance=self.holiday_type.observance,
                recurrence=self.holiday_type.recurrence,
                description=description
            )
        
        if notes is not None:
            self.notes = notes
        
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            PublicHolidayUpdated(
                holiday_id=self.holiday_id,
                old_holiday_type=old_type,
                new_holiday_type=self.holiday_type,
                updated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def change_date(
        self,
        new_date: date,
        updated_by: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """Change holiday date"""
        old_date_range = self.date_range
        
        # Business rule: Cannot change date to past for active holidays
        if self.is_active and new_date < date.today():
            raise ValueError("Cannot change active holiday to past date")
        
        self.date_range = HolidayDateRange.single_day(new_date)
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            PublicHolidayDateChanged(
                holiday_id=self.holiday_id,
                old_date_range=old_date_range,
                new_date_range=self.date_range,
                reason=reason,
                updated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def change_date_range(
        self,
        start_date: date,
        end_date: Optional[date] = None,
        updated_by: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """Change holiday date range"""
        old_date_range = self.date_range
        
        # Business rule: Cannot change date to past for active holidays
        if self.is_active and start_date < date.today():
            raise ValueError("Cannot change active holiday to past date")
        
        if end_date:
            self.date_range = HolidayDateRange.multi_day(start_date, end_date)
        else:
            self.date_range = HolidayDateRange.single_day(start_date)
        
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            PublicHolidayDateChanged(
                holiday_id=self.holiday_id,
                old_date_range=old_date_range,
                new_date_range=self.date_range,
                reason=reason,
                updated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def activate(self, updated_by: Optional[str] = None):
        """Activate holiday"""
        if self.is_active:
            return  # Already active
        
        # Business rule: Cannot activate past holidays
        if self.date_range.is_past():
            raise ValueError("Cannot activate holidays for past dates")
        
        self.is_active = True
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            PublicHolidayActivated(
                holiday_id=self.holiday_id,
                holiday_type=self.holiday_type,
                date_range=self.date_range,
                activated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def deactivate(self, updated_by: Optional[str] = None, reason: Optional[str] = None):
        """Deactivate holiday"""
        if not self.is_active:
            return  # Already inactive
        
        self.is_active = False
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self._add_domain_event(
            PublicHolidayDeactivated(
                holiday_id=self.holiday_id,
                holiday_type=self.holiday_type,
                date_range=self.date_range,
                reason=reason,
                deactivated_by=updated_by,
                occurred_at=datetime.utcnow()
            )
        )
    
    def is_on_date(self, check_date: date) -> bool:
        """Check if holiday falls on a specific date"""
        return self.date_range.contains_date(check_date)
    
    def is_mandatory(self) -> bool:
        """Check if holiday is mandatory"""
        return self.holiday_type.is_mandatory()
    
    def is_optional(self) -> bool:
        """Check if holiday is optional"""
        return self.holiday_type.is_optional()
    
    def is_floating(self) -> bool:
        """Check if holiday is floating"""
        return self.holiday_type.is_floating()
    
    def is_national(self) -> bool:
        """Check if holiday is national"""
        return self.holiday_type.category == HolidayCategory.NATIONAL
    
    def is_religious(self) -> bool:
        """Check if holiday is religious"""
        return self.holiday_type.category == HolidayCategory.RELIGIOUS
    
    def is_company_specific(self) -> bool:
        """Check if holiday is company-specific"""
        return self.holiday_type.category == HolidayCategory.COMPANY
    
    def is_regional(self) -> bool:
        """Check if holiday is regional"""
        return self.holiday_type.category == HolidayCategory.REGIONAL
    
    def get_duration_days(self) -> float:
        """Get holiday duration in days"""
        return self.date_range.get_duration_days()
    
    def get_formatted_name(self) -> str:
        """Get formatted holiday name"""
        return self.holiday_type.get_display_name()
    
    def get_calendar_info(self) -> dict:
        """Get calendar information"""
        return self.date_range.get_calendar_info()
    
    def conflicts_with(self, other: 'PublicHoliday') -> bool:
        """Check if this holiday conflicts with another"""
        return (
            self.holiday_id != other.holiday_id and
            self.date_range.overlaps_with(other.date_range) and
            self.is_active and other.is_active
        )
    
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
            "holiday_id": self.holiday_id,
            "holiday_type": self.holiday_type.to_dict(),
            "date_range": self.date_range.to_dict(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "notes": self.notes,
            "location_specific": self.location_specific,
            "substitute_for": self.substitute_for
        } 