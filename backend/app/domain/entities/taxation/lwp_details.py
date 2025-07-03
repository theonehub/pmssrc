from dataclasses import dataclass
from typing import Dict, Any
from decimal import Decimal


@dataclass
class LWPDetails:
    """Leave Without Pay details for a month."""
    
    lwp_days: int = 0
    total_working_days: int = 30
    month: int = 1  # 1-12
    year: int = 2024
    
    def get_lwp_factor(self) -> Decimal:
        """
        Calculate the LWP factor (reduction factor for salary).
        
        Returns:
            Decimal: Factor between 0 and 1 representing salary reduction
        """
        if self.lwp_days <= 0 or self.total_working_days <= 0:
            return Decimal('1.0')  # No LWP
        
        if self.lwp_days >= self.total_working_days:
            return Decimal('0.0')  # Full month LWP
        
        return Decimal('1.0') - (Decimal(str(self.lwp_days)) / Decimal(str(self.total_working_days)))
    
    def get_paid_days(self) -> int:
        """Get number of paid days in the month."""
        return max(0, self.total_working_days - self.lwp_days)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "lwp_days": self.lwp_days,
            "total_working_days": self.total_working_days,
            "paid_days": self.get_paid_days(),
            "lwp_factor": float(self.get_lwp_factor()),
            "month": self.month,
            "year": self.year
        }

