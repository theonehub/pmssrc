"""
Component ID Value Object
Represents a unique identifier for salary components
"""

import uuid
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class ComponentId:
    """
    Value object for component identifiers.
    
    Ensures type safety and validates component ID format.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the component ID format"""
        if not self.value:
            raise ValueError("Component ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Component ID must be a string")
        
        # Allow both UUID format and custom format
        if len(self.value) < 3:
            raise ValueError("Component ID must be at least 3 characters long")
    
    @classmethod
    def generate(cls) -> 'ComponentId':
        """Generate a new unique component ID"""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: str) -> 'ComponentId':
        """Create ComponentId from string"""
        return cls(value.strip())
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, ComponentId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self.value) 