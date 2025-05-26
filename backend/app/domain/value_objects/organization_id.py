"""
Organization ID Value Object
Represents a unique identifier for an organization
"""

import uuid
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class OrganizationId:
    """
    Value object representing an organization identifier.
    
    Follows SOLID principles:
    - SRP: Encapsulates organization ID logic
    - OCP: Extensible through new validation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for ID operations
    - DIP: Depends on abstractions (string)
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the organization ID"""
        if not self.value:
            raise ValueError("Organization ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Organization ID must be a string")
        
        if len(self.value.strip()) == 0:
            raise ValueError("Organization ID cannot be whitespace only")
        
        # Validate UUID format if it looks like a UUID
        if len(self.value) == 36 and '-' in self.value:
            try:
                uuid.UUID(self.value)
            except ValueError:
                raise ValueError("Invalid UUID format for organization ID")
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"OrganizationId('{self.value}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if isinstance(other, OrganizationId):
            return self.value == other.value
        return False
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self.value)
    
    @classmethod
    def generate(cls) -> 'OrganizationId':
        """Generate a new random organization ID"""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: Union[str, 'OrganizationId']) -> 'OrganizationId':
        """Create OrganizationId from string or existing OrganizationId"""
        if isinstance(value, OrganizationId):
            return value
        return cls(value)
    
    def is_uuid(self) -> bool:
        """Check if the ID is in UUID format"""
        try:
            uuid.UUID(self.value)
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {"value": self.value}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OrganizationId':
        """Create from dictionary representation"""
        return cls(data["value"]) 