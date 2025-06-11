"""
User ID Value Object
Immutable value object for user identification
"""

import uuid
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class UserId:
    """
    User ID value object.
    
    Immutable value object that ensures user ID is always valid.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate user ID after initialization."""
        if not self.value:
            raise ValueError("User ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("User ID must be a string")
        
        if len(self.value.strip()) == 0:
            raise ValueError("User ID cannot be blank")
    
    @classmethod
    def generate(cls) -> 'UserId':
        """Generate a new unique user ID."""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: Union[str, None]) -> 'UserId':
        """Create UserId from string value."""
        if value is None:
            raise ValueError("User ID cannot be None")
        return cls(str(value))
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"UserId({self.value})" 