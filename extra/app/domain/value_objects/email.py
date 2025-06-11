"""
Email Value Object
Immutable value object for email addresses with validation
"""

import re
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Email:
    """
    Email value object.
    
    Immutable value object that ensures email is always valid.
    """
    
    value: str
    
    # Email validation regex pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __post_init__(self):
        """Validate email after initialization."""
        if not self.value:
            raise ValueError("Email cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Email must be a string")
        
        email = self.value.strip().lower()
        if not email:
            raise ValueError("Email cannot be blank")
        
        if not self.EMAIL_PATTERN.match(email):
            raise ValueError(f"Invalid email format: {self.value}")
        
        # Update the value to be normalized (lowercase and trimmed)
        object.__setattr__(self, 'value', email)
    
    @classmethod
    def from_string(cls, value: Union[str, None]) -> 'Email':
        """Create Email from string value."""
        if value is None:
            raise ValueError("Email cannot be None")
        return cls(str(value))
    
    def domain(self) -> str:
        """Get the domain part of the email."""
        return self.value.split('@')[1]
    
    def local_part(self) -> str:
        """Get the local part (before @) of the email."""
        return self.value.split('@')[0]
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Email({self.value})" 