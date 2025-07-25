"""
Organisation ID Value Object
Represents a unique identifier for an organisation
"""

import uuid
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class OrganisationId:
    """
    Value object representing an organisation identifier.
    
    Follows SOLID principles:
    - SRP: Encapsulates organisation ID logic
    - OCP: Extensible through new validation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for ID operations
    - DIP: Depends on abstractions (string)
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the organisation ID"""
        if not self.value:
            raise ValueError("Organisation ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Organisation ID must be a string")
        
        if len(self.value.strip()) == 0:
            raise ValueError("Organisation ID cannot be whitespace only")
        
        # Validate UUID format if it looks like a UUID
        if len(self.value) == 36 and '-' in self.value:
            try:
                uuid.UUID(self.value)
            except ValueError:
                raise ValueError("Invalid UUID format for organisation ID")
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"OrganisationId('{self.value}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if isinstance(other, OrganisationId):
            return self.value == other.value
        return False
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self.value)
    
    @classmethod
    def generate(cls) -> 'OrganisationId':
        """Generate a new random organisation ID"""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: Union[str, 'OrganisationId']) -> 'OrganisationId':
        """Create OrganisationId from string or existing OrganisationId"""
        if isinstance(value, OrganisationId):
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
    def from_dict(cls, data: dict) -> 'OrganisationId':
        """Create from dictionary representation"""
        return cls(data["value"]) 