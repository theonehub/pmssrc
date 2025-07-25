"""
Date Range Value Object
Immutable value object representing date ranges with validation
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Iterator


@dataclass(frozen=True)
class DateRange:
    """
    Date range value object ensuring immutability and validation.
    
    Follows SOLID principles:
    - SRP: Only handles date range representation and operations
    - OCP: Can be extended without modification
    - LSP: Can be substituted anywhere DateRange is expected
    - ISP: Provides only date range operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    start_date: date
    end_date: date
    
    def __post_init__(self):
        """Validate date range on creation"""
        if not isinstance(self.start_date, date):
            raise ValueError("Start date must be a date object")
        
        if not isinstance(self.end_date, date):
            raise ValueError("End date must be a date object")
        
        if self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
    
    @classmethod
    def create(cls, start_date: date, end_date: date) -> 'DateRange':
        """Create date range with validation"""
        return cls(start_date, end_date)
    
    @classmethod
    def single_day(cls, target_date: date) -> 'DateRange':
        """Create single day date range"""
        return cls(target_date, target_date)
    
    @classmethod
    def current_month(cls) -> 'DateRange':
        """Create date range for current month"""
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        
        # Calculate last day of month
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        return cls(start_of_month, end_of_month)
    
    @classmethod
    def current_year(cls) -> 'DateRange':
        """Create date range for current year"""
        today = date.today()
        start_of_year = date(today.year, 1, 1)
        end_of_year = date(today.year, 12, 31)
        return cls(start_of_year, end_of_year)
    
    @classmethod
    def financial_year(cls, year: Optional[int] = None) -> 'DateRange':
        """Create date range for financial year (April to March)"""
        if year is None:
            today = date.today()
            # If current month is Jan-Mar, FY started previous year
            if today.month <= 3:
                year = today.year - 1
            else:
                year = today.year
        
        start_date = date(year, 4, 1)
        end_date = date(year + 1, 3, 31)
        return cls(start_date, end_date)
    
    @classmethod
    def last_n_days(cls, days: int) -> 'DateRange':
        """Create date range for last N days"""
        if days <= 0:
            raise ValueError("Days must be positive")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        return cls(start_date, end_date)
    
    @classmethod
    def next_n_days(cls, days: int) -> 'DateRange':
        """Create date range for next N days"""
        if days <= 0:
            raise ValueError("Days must be positive")
        
        start_date = date.today()
        end_date = start_date + timedelta(days=days - 1)
        return cls(start_date, end_date)
    
    def duration_in_days(self) -> int:
        """Get duration in days (inclusive)"""
        return (self.end_date - self.start_date).days + 1
    
    def contains(self, target_date: date) -> bool:
        """Check if date is within range (inclusive)"""
        return self.start_date <= target_date <= self.end_date
    
    def overlaps_with(self, other: 'DateRange') -> bool:
        """Check if this range overlaps with another range"""
        return (self.start_date <= other.end_date and 
                self.end_date >= other.start_date)
    
    def is_adjacent_to(self, other: 'DateRange') -> bool:
        """Check if this range is adjacent to another range"""
        return (self.end_date + timedelta(days=1) == other.start_date or
                other.end_date + timedelta(days=1) == self.start_date)
    
    def merge_with(self, other: 'DateRange') -> 'DateRange':
        """Merge with another date range (must overlap or be adjacent)"""
        if not (self.overlaps_with(other) or self.is_adjacent_to(other)):
            raise ValueError("Date ranges must overlap or be adjacent to merge")
        
        new_start = min(self.start_date, other.start_date)
        new_end = max(self.end_date, other.end_date)
        return DateRange(new_start, new_end)
    
    def intersect_with(self, other: 'DateRange') -> Optional['DateRange']:
        """Get intersection with another date range"""
        if not self.overlaps_with(other):
            return None
        
        new_start = max(self.start_date, other.start_date)
        new_end = min(self.end_date, other.end_date)
        return DateRange(new_start, new_end)
    
    def extend_by_days(self, days: int) -> 'DateRange':
        """Extend range by specified days (positive extends end, negative extends start)"""
        if days >= 0:
            return DateRange(self.start_date, self.end_date + timedelta(days=days))
        else:
            return DateRange(self.start_date + timedelta(days=days), self.end_date)
    
    def shift_by_days(self, days: int) -> 'DateRange':
        """Shift entire range by specified days"""
        delta = timedelta(days=days)
        return DateRange(self.start_date + delta, self.end_date + delta)
    
    def split_by_months(self) -> Iterator['DateRange']:
        """Split date range into monthly ranges"""
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Start of current month
            month_start = max(current_date, self.start_date)
            
            # End of current month
            if current_date.month == 12:
                next_month_start = date(current_date.year + 1, 1, 1)
            else:
                next_month_start = date(current_date.year, current_date.month + 1, 1)
            
            month_end = min(next_month_start - timedelta(days=1), self.end_date)
            
            yield DateRange(month_start, month_end)
            
            current_date = next_month_start
    
    def get_weekdays(self) -> Iterator[date]:
        """Get all weekdays (Monday-Friday) in the range"""
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.weekday() < 5:  # Monday=0, Friday=4
                yield current_date
            current_date += timedelta(days=1)
    
    def get_weekends(self) -> Iterator[date]:
        """Get all weekend days (Saturday-Sunday) in the range"""
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.weekday() >= 5:  # Saturday=5, Sunday=6
                yield current_date
            current_date += timedelta(days=1)
    
    def count_weekdays(self) -> int:
        """Count weekdays in the range"""
        return sum(1 for _ in self.get_weekdays())
    
    def count_weekends(self) -> int:
        """Count weekend days in the range"""
        return sum(1 for _ in self.get_weekends())
    
    def is_single_day(self) -> bool:
        """Check if range represents a single day"""
        return self.start_date == self.end_date
    
    def is_current_month(self) -> bool:
        """Check if range represents current month"""
        current_month_range = self.current_month()
        return self == current_month_range
    
    def is_current_year(self) -> bool:
        """Check if range represents current year"""
        current_year_range = self.current_year()
        return self == current_year_range
    
    def format(self, date_format: str = "%Y-%m-%d") -> str:
        """Format date range as string"""
        if self.is_single_day():
            return self.start_date.strftime(date_format)
        else:
            return f"{self.start_date.strftime(date_format)} to {self.end_date.strftime(date_format)}"
    
    def __str__(self) -> str:
        """String representation"""
        return self.format()
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"DateRange(start_date={self.start_date}, end_date={self.end_date})"
    
    def __contains__(self, target_date: date) -> bool:
        """Support 'in' operator"""
        return self.contains(target_date)
    
    def __iter__(self) -> Iterator[date]:
        """Iterate over all dates in range"""
        current_date = self.start_date
        while current_date <= self.end_date:
            yield current_date
            current_date += timedelta(days=1)
    
    def __len__(self) -> int:
        """Length of date range in days"""
        return self.duration_in_days() 