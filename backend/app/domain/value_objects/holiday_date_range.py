"""
Holiday Date Range Value Object
Immutable representation of holiday date ranges and scheduling
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum


class DateRangeType(Enum):
    """Enumeration of date range types"""
    SINGLE_DAY = "single_day"
    MULTI_DAY = "multi_day"
    HALF_DAY = "half_day"
    WEEKEND_BRIDGE = "weekend_bridge"


@dataclass(frozen=True)
class HolidayDateRange:
    """
    Value object representing a holiday date range.
    
    Follows SOLID principles:
    - SRP: Only represents holiday date information
    - OCP: Extensible through composition
    - LSP: Maintains value object contracts
    - ISP: Focused interface for date ranges
    - DIP: No dependencies on external systems
    """
    
    start_date: date
    end_date: Optional[date] = None
    range_type: DateRangeType = DateRangeType.SINGLE_DAY
    is_half_day: bool = False
    half_day_period: Optional[str] = None  # "morning" or "afternoon"
    
    def __post_init__(self):
        """Validate holiday date range data"""
        if not isinstance(self.start_date, date):
            raise ValueError("Start date must be a valid date")
        
        if self.end_date and not isinstance(self.end_date, date):
            raise ValueError("End date must be a valid date")
        
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")
        
        # Auto-determine range type if not specified
        if self.range_type == DateRangeType.SINGLE_DAY:
            if self.end_date and self.end_date != self.start_date:
                object.__setattr__(self, 'range_type', DateRangeType.MULTI_DAY)
            elif self.is_half_day:
                object.__setattr__(self, 'range_type', DateRangeType.HALF_DAY)
        
        # Validate half day settings
        if self.is_half_day:
            if self.half_day_period not in ["morning", "afternoon"]:
                raise ValueError("Half day period must be 'morning' or 'afternoon'")
            if self.end_date and self.end_date != self.start_date:
                raise ValueError("Half day holidays cannot span multiple days")
        
        # Set end_date to start_date for single day holidays
        if not self.end_date:
            object.__setattr__(self, 'end_date', self.start_date)
    
    @classmethod
    def single_day(cls, holiday_date: date) -> 'HolidayDateRange':
        """Factory method for single day holidays"""
        return cls(
            start_date=holiday_date,
            end_date=holiday_date,
            range_type=DateRangeType.SINGLE_DAY
        )
    
    @classmethod
    def multi_day(cls, start_date: date, end_date: date) -> 'HolidayDateRange':
        """Factory method for multi-day holidays"""
        return cls(
            start_date=start_date,
            end_date=end_date,
            range_type=DateRangeType.MULTI_DAY
        )
    
    @classmethod
    def half_day(
        cls, 
        holiday_date: date, 
        period: str = "morning"
    ) -> 'HolidayDateRange':
        """Factory method for half day holidays"""
        if period not in ["morning", "afternoon"]:
            raise ValueError("Period must be 'morning' or 'afternoon'")
        
        return cls(
            start_date=holiday_date,
            end_date=holiday_date,
            range_type=DateRangeType.HALF_DAY,
            is_half_day=True,
            half_day_period=period
        )
    
    @classmethod
    def weekend_bridge(
        cls, 
        start_date: date, 
        end_date: date
    ) -> 'HolidayDateRange':
        """Factory method for weekend bridge holidays"""
        return cls(
            start_date=start_date,
            end_date=end_date,
            range_type=DateRangeType.WEEKEND_BRIDGE
        )
    
    def get_duration_days(self) -> int:
        """Get the duration in days"""
        if self.is_half_day:
            return 0.5
        return (self.end_date - self.start_date).days + 1
    
    def get_all_dates(self) -> List[date]:
        """Get all dates in the range"""
        dates = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates
    
    def contains_date(self, check_date: date) -> bool:
        """Check if a date falls within this range"""
        return self.start_date <= check_date <= self.end_date
    
    def overlaps_with(self, other: 'HolidayDateRange') -> bool:
        """Check if this range overlaps with another"""
        return not (self.end_date < other.start_date or other.end_date < self.start_date)
    
    def is_single_day(self) -> bool:
        """Check if this is a single day holiday"""
        return self.range_type == DateRangeType.SINGLE_DAY
    
    def is_multi_day(self) -> bool:
        """Check if this is a multi-day holiday"""
        return self.range_type == DateRangeType.MULTI_DAY
    
    def is_weekend_bridge(self) -> bool:
        """Check if this is a weekend bridge holiday"""
        return self.range_type == DateRangeType.WEEKEND_BRIDGE
    
    def get_weekday_name(self) -> str:
        """Get the weekday name for single day holidays"""
        if self.is_single_day():
            return self.start_date.strftime("%A")
        return "Multiple Days"
    
    def get_month_name(self) -> str:
        """Get the month name"""
        return self.start_date.strftime("%B")
    
    def get_year(self) -> int:
        """Get the year"""
        return self.start_date.year
    
    def get_formatted_date_range(self) -> str:
        """Get formatted date range string"""
        if self.is_single_day():
            if self.is_half_day:
                return f"{self.start_date.strftime('%B %d, %Y')} ({self.half_day_period})"
            return self.start_date.strftime("%B %d, %Y")
        else:
            return f"{self.start_date.strftime('%B %d')} - {self.end_date.strftime('%B %d, %Y')}"
    
    def is_in_current_year(self) -> bool:
        """Check if holiday is in current year"""
        current_year = datetime.now().year
        return self.start_date.year == current_year
    
    def is_upcoming(self) -> bool:
        """Check if holiday is upcoming"""
        today = date.today()
        return self.start_date >= today
    
    def is_past(self) -> bool:
        """Check if holiday is in the past"""
        today = date.today()
        return self.end_date < today
    
    def days_until_holiday(self) -> int:
        """Get number of days until holiday starts"""
        today = date.today()
        if self.start_date >= today:
            return (self.start_date - today).days
        return -1
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "range_type": self.range_type.value,
            "is_half_day": self.is_half_day,
            "half_day_period": self.half_day_period,
            "duration_days": self.get_duration_days(),
            "formatted_range": self.get_formatted_date_range()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HolidayDateRange':
        """Create from dictionary"""
        start_date = datetime.fromisoformat(data["start_date"]).date()
        end_date = datetime.fromisoformat(data["end_date"]).date() if data.get("end_date") else None
        
        return cls(
            start_date=start_date,
            end_date=end_date,
            range_type=DateRangeType(data["range_type"]),
            is_half_day=data.get("is_half_day", False),
            half_day_period=data.get("half_day_period")
        )
    
    def get_iso_date_string(self) -> str:
        """Get ISO format date string for single day holidays"""
        return self.start_date.isoformat()
    
    def get_calendar_info(self) -> dict:
        """Get calendar information"""
        return {
            "day": self.start_date.day,
            "month": self.start_date.month,
            "year": self.start_date.year,
            "weekday": self.start_date.weekday(),
            "weekday_name": self.get_weekday_name(),
            "month_name": self.get_month_name(),
            "is_weekend": self.start_date.weekday() >= 5
        } 