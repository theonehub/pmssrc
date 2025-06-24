"""
Employment Period Value Object
Handles employment periods for mid-year scenarios (joiners, increments)
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.tax_year import TaxYear


@dataclass(frozen=True)
class EmploymentPeriod:
    """
    Represents a period of employment with specific salary.
    Used for handling mid-year joiners and salary increments.
    """
    
    start_date: date
    end_date: Optional[date]  # None for ongoing periods
    description: str  # e.g., "Initial salary", "Post increment", "Mid-year joining"
    
    def __post_init__(self):
        """Validate employment period."""
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
    
    def get_period_months(self, tax_year: TaxYear) -> Decimal:
        """
        Calculate number of months this period spans within the tax year.
        
        Args:
            tax_year: Tax year to calculate within
            
        Returns:
            Decimal: Number of months (including fractional months)
        """
        # Get the actual start and end dates within the tax year
        period_start = max(self.start_date, tax_year.get_start_date())
        period_end = min(self.end_date or tax_year.get_end_date(), tax_year.get_end_date())
        
        if period_start > period_end:
            return Decimal('0')
        
        # Calculate days and convert to months
        days = (period_end - period_start).days + 1  # +1 to include both dates
        return Decimal(str(days)) / Decimal('30.44')  # Average days per month
    
    def get_period_days(self, tax_year: TaxYear) -> int:
        """
        Calculate number of days this period spans within the tax year.
        
        Args:
            tax_year: Tax year to calculate within
            
        Returns:
            int: Number of days
        """
        # Get the actual start and end dates within the tax year
        period_start = max(self.start_date, tax_year.get_start_date())
        period_end = min(self.end_date or tax_year.get_end_date(), tax_year.get_end_date())
        
        if period_start > period_end:
            return 0
        
        return (period_end - period_start).days + 1  # +1 to include both dates
    
    def is_full_year(self, tax_year: TaxYear) -> bool:
        """
        Check if this period covers the full tax year.
        
        Args:
            tax_year: Tax year to check against
            
        Returns:
            bool: True if period covers full year
        """
        return (self.start_date <= tax_year.get_start_date() and 
                (self.end_date is None or self.end_date >= tax_year.get_end_date()))
    
    def overlaps_with(self, other: 'EmploymentPeriod') -> bool:
        """
        Check if this period overlaps with another period.
        
        Args:
            other: Another employment period
            
        Returns:
            bool: True if periods overlap
        """
        if self.end_date is None or other.end_date is None:
            # If either period is ongoing, check if start dates conflict
            return True
        
        return not (self.end_date < other.start_date or other.end_date < self.start_date)
    
    def get_proration_factor(self, tax_year: TaxYear) -> Decimal:
        """
        Get proration factor for this period within the tax year.
        
        Args:
            tax_year: Tax year to calculate for
            
        Returns:
            Decimal: Proration factor (0.0 to 1.0)
        """
        if self.is_full_year(tax_year):
            return Decimal('1.0')
        
        period_months = self.get_period_months(tax_year)
        return period_months / Decimal('12')
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "description": self.description,
            "is_ongoing": self.end_date is None
        }
    
    @classmethod
    def full_year_period(cls, tax_year: TaxYear, description: str = "Full year employment") -> 'EmploymentPeriod':
        """
        Create a full year employment period.
        
        Args:
            tax_year: Tax year
            description: Period description
            
        Returns:
            EmploymentPeriod: Full year period
        """
        return cls(
            start_date=tax_year.get_start_date(),
            end_date=tax_year.get_end_date(),
            description=description
        )
    
    @classmethod
    def mid_year_joiner(cls, joining_date: date, description: str = "Mid-year joining") -> 'EmploymentPeriod':
        """
        Create a mid-year joiner period.
        
        Args:
            joining_date: Date of joining
            description: Period description
            
        Returns:
            EmploymentPeriod: Mid-year joiner period
        """
        return cls(
            start_date=joining_date,
            end_date=None,  # Ongoing
            description=description
        )
    
    @classmethod
    def increment_period(cls, increment_date: date, previous_end_date: Optional[date] = None,
                        description: str = "Post increment") -> 'EmploymentPeriod':
        """
        Create an increment period.
        
        Args:
            increment_date: Date of increment
            previous_end_date: End date (if period has ended)
            description: Period description
            
        Returns:
            EmploymentPeriod: Increment period
        """
        return cls(
            start_date=increment_date,
            end_date=previous_end_date,
            description=description
        ) 