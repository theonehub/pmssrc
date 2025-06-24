"""
Tax Regime Value Object
Represents different tax regimes in India
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TaxRegimeType(Enum):
    """Tax regime types."""
    OLD = "old"
    NEW = "new"


@dataclass
class TaxRegime:
    """Tax regime value object."""
    
    regime_type: TaxRegimeType
    effective_from: Optional[str] = None  # Format: YYYY-MM-DD
    effective_until: Optional[str] = None  # Format: YYYY-MM-DD
    
    def __post_init__(self):
        """Validate the tax regime."""
        if not isinstance(self.regime_type, TaxRegimeType):
            raise ValueError("Invalid tax regime type")
        
        if self.effective_from and not self._is_valid_date(self.effective_from):
            raise ValueError("Invalid effective from date format")
        
        if self.effective_until and not self._is_valid_date(self.effective_until):
            raise ValueError("Invalid effective until date format")
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if date string is in valid format."""
        try:
            year, month, day = map(int, date_str.split("-"))
            return 1 <= month <= 12 and 1 <= day <= 31
        except (ValueError, TypeError):
            return False
    
    def is_active(self, date_str: str) -> bool:
        """
        Check if tax regime is active on given date.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            bool: True if active, False otherwise
        """
        if not self._is_valid_date(date_str):
            raise ValueError("Invalid date format")
        
        if self.effective_from and date_str < self.effective_from:
            return False
        
        if self.effective_until and date_str > self.effective_until:
            return False
        
        return True
    
    def __eq__(self, other: object) -> bool:
        """Compare tax regimes."""
        if not isinstance(other, TaxRegime):
            return False
        
        return (
            self.regime_type == other.regime_type and
            self.effective_from == other.effective_from and
            self.effective_until == other.effective_until
        )
    
    def __hash__(self) -> int:
        """Get hash of tax regime."""
        return hash((
            self.regime_type,
            self.effective_from,
            self.effective_until
        )) 