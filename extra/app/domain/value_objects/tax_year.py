"""
Tax Year Value Object
Immutable value object for Indian financial year handling
"""

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Union


@dataclass(frozen=True)
class TaxYear:
    """
    Tax year value object for Indian financial year (April to March).
    
    Handles Indian financial year validation and operations.
    """
    
    start_year: int
    end_year: int
    
    def __post_init__(self):
        """Validate tax year after initialization."""
        if self.end_year != self.start_year + 1:
            raise ValueError("Tax year must be consecutive (e.g., 2023-24)")
        
        if self.start_year < 2000 or self.start_year > 2050:
            raise ValueError("Invalid tax year range")
    
    def __str__(self) -> str:
        """String representation (e.g., '2023-24')."""
        return f"{self.start_year}-{str(self.end_year)[2:]}"
    
    def get_display_name(self) -> str:
        """Get display name for tax year."""
        return f"FY {self.start_year}-{str(self.end_year)[2:]}"
    
    def get_assessment_year(self) -> str:
        """Get assessment year (next year)."""
        return f"AY {self.end_year}-{str(self.end_year + 1)[2:]}"
    
    def get_start_date(self) -> date:
        """Get financial year start date (1st April)."""
        return date(self.start_year, 4, 1)
    
    def get_end_date(self) -> date:
        """Get financial year end date (31st March)."""
        return date(self.end_year, 3, 31)
    
    def contains_date(self, check_date: Union[date, datetime]) -> bool:
        """Check if a date falls within this financial year."""
        if isinstance(check_date, datetime):
            check_date = check_date.date()
        
        return self.get_start_date() <= check_date <= self.get_end_date()
    
    def is_current_year(self) -> bool:
        """Check if this is the current financial year."""
        return self == TaxYear.current()
    
    def is_past_year(self) -> bool:
        """Check if this is a past financial year."""
        return self.end_year < TaxYear.current().end_year
    
    def is_future_year(self) -> bool:
        """Check if this is a future financial year."""
        return self.start_year > TaxYear.current().start_year
    
    def get_previous_year(self) -> 'TaxYear':
        """Get previous financial year."""
        return TaxYear(self.start_year - 1, self.end_year - 1)
    
    def get_next_year(self) -> 'TaxYear':
        """Get next financial year."""
        return TaxYear(self.start_year + 1, self.end_year + 1)
    
    @classmethod
    def from_string(cls, year_str: str) -> 'TaxYear':
        """
        Create from string like '2023-24' or '2023-2024'.
        
        Args:
            year_str: String representation of tax year
            
        Returns:
            TaxYear: Validated tax year object
        """
        year_str = year_str.strip()
        
        # Handle YYYY-YY format (e.g., "2023-24")
        if re.match(r'^\d{4}-\d{2}$', year_str):
            start_year = int(year_str[:4])
            end_year_suffix = int(year_str[5:])
            
            # Handle century transition
            if end_year_suffix < 50:  # Assume 2000s
                end_year = 2000 + end_year_suffix
            else:  # Assume 1900s (for historical data)
                end_year = 1900 + end_year_suffix
                
            return cls(start_year, end_year)
        
        # Handle YYYY-YYYY format (e.g., "2023-2024")
        elif re.match(r'^\d{4}-\d{4}$', year_str):
            start_year = int(year_str[:4])
            end_year = int(year_str[5:])
            return cls(start_year, end_year)
        
        # Handle FY prefix (e.g., "FY 2023-24")
        elif year_str.upper().startswith("FY "):
            return cls.from_string(year_str[3:])
        
        else:
            raise ValueError(f"Invalid tax year format: '{year_str}'. Use 'YYYY-YY' or 'YYYY-YYYY'")
    
    @classmethod
    def current(cls) -> 'TaxYear':
        """Get current financial year based on today's date."""
        today = date.today()
        
        if today.month >= 4:  # April onwards - same year FY
            return cls(today.year, today.year + 1)
        else:  # Jan-March - previous year FY
            return cls(today.year - 1, today.year)
    
    @classmethod
    def from_date(cls, input_date: Union[date, datetime]) -> 'TaxYear':
        """Get financial year for a specific date."""
        if isinstance(input_date, datetime):
            input_date = input_date.date()
        
        if input_date.month >= 4:  # April onwards
            return cls(input_date.year, input_date.year + 1)
        else:  # Jan-March
            return cls(input_date.year - 1, input_date.year)
    
    @classmethod
    def for_assessment_year(cls, assessment_year: str) -> 'TaxYear':
        """
        Create financial year from assessment year string.
        
        Args:
            assessment_year: Assessment year like "AY 2024-25"
            
        Returns:
            TaxYear: Corresponding financial year
        """
        # Remove AY prefix if present
        if assessment_year.upper().startswith("AY "):
            assessment_year = assessment_year[3:]
        
        # Parse assessment year
        if re.match(r'^\d{4}-\d{2}$', assessment_year):
            ay_start = int(assessment_year[:4])
            # Financial year is previous year
            return cls(ay_start - 1, ay_start)
        else:
            raise ValueError(f"Invalid assessment year format: '{assessment_year}'")
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, TaxYear):
            return False
        return self.start_year == other.start_year and self.end_year == other.end_year
    
    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, TaxYear):
            return NotImplemented
        return self.start_year < other.start_year
    
    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, TaxYear):
            return NotImplemented
        return self.start_year <= other.start_year
    
    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        if not isinstance(other, TaxYear):
            return NotImplemented
        return self.start_year > other.start_year
    
    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, TaxYear):
            return NotImplemented
        return self.start_year >= other.start_year
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash((self.start_year, self.end_year)) 