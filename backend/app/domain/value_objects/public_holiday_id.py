"""
Public Holiday ID Value Object
Following DDD principles for type safety and domain modeling
"""

from dataclasses import dataclass
from typing import Union
import uuid


@dataclass(frozen=True)
class PublicHolidayId:
    """
    Value object representing a public holiday identifier.
    
    Follows DDD principles:
    - Immutable value object
    - Type safety for holiday identifiers
    - Encapsulates validation logic
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the holiday ID after initialization."""
        if not self.value:
            raise ValueError("Public holiday ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Public holiday ID must be a string")
    
    @classmethod
    def generate(cls) -> 'PublicHolidayId':
        """
        Generate a new unique public holiday ID.
        
        Returns:
            New PublicHolidayId instance
        """
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: Union[str, None]) -> 'PublicHolidayId':
        """
        Create PublicHolidayId from string value.
        
        Args:
            value: String representation of the ID
            
        Returns:
            PublicHolidayId instance
            
        Raises:
            ValueError: If value is invalid
        """
        if value is None:
            raise ValueError("Public holiday ID cannot be None")
        
        return cls(str(value))
    
    def __str__(self) -> str:
        """String representation of the holiday ID."""
        return self.value
    
    def __repr__(self) -> str:
        """Developer representation of the holiday ID."""
        return f"PublicHolidayId('{self.value}')"
    
    def __eq__(self, other) -> bool:
        """Check equality with another PublicHolidayId."""
        if not isinstance(other, PublicHolidayId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash function for use in sets and dictionaries."""
        return hash(self.value) 