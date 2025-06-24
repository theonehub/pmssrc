"""
Organization ID Value Object
Represents a unique identifier for an organization
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OrganizationId:
    """
    Value object representing an organization identifier.
    
    The organization ID can be either:
    - A UUID string
    - A hostname string (for multi-tenant systems)
    - A custom organization code
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the organization ID value"""
        if not self.value:
            raise ValueError("Organization ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Organization ID must be a string")
        
        # Trim whitespace
        object.__setattr__(self, 'value', self.value.strip())
        
        if not self.value:
            raise ValueError("Organization ID cannot be empty after trimming")
        
        # Validate format based on type
        if self._is_uuid(self.value):
            # UUID format validation
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if not re.match(uuid_pattern, self.value.lower()):
                raise ValueError("Invalid UUID format for organization ID")
        elif self._is_hostname(self.value):
            # Hostname format validation
            hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
            if not re.match(hostname_pattern, self.value):
                raise ValueError("Invalid hostname format for organization ID")
        else:
            # Custom organization code validation
            if len(self.value) > 50:
                raise ValueError("Organization ID cannot exceed 50 characters")
            
            # Allow alphanumeric, hyphens, and underscores
            if not re.match(r'^[a-zA-Z0-9_-]+$', self.value):
                raise ValueError("Organization ID can only contain alphanumeric characters, hyphens, and underscores")
    
    def _is_uuid(self, value: str) -> bool:
        """Check if the value looks like a UUID"""
        return len(value) == 36 and value.count('-') == 4
    
    def _is_hostname(self, value: str) -> bool:
        """Check if the value looks like a hostname"""
        return '.' in value and not value.startswith('.') and not value.endswith('.')
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"OrganizationId('{self.value}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, OrganizationId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    @classmethod
    def from_hostname(cls, hostname: str) -> 'OrganizationId':
        """
        Create an OrganizationId from a hostname.
        
        Args:
            hostname: The hostname string
            
        Returns:
            OrganizationId instance
            
        Raises:
            ValueError: If hostname is invalid
        """
        if not hostname:
            raise ValueError("Hostname cannot be empty")
        
        # Normalize hostname
        normalized_hostname = hostname.lower().strip()
        
        return cls(normalized_hostname)
    
    @classmethod
    def from_uuid(cls, uuid_str: str) -> 'OrganizationId':
        """
        Create an OrganizationId from a UUID string.
        
        Args:
            uuid_str: The UUID string
            
        Returns:
            OrganizationId instance
            
        Raises:
            ValueError: If UUID is invalid
        """
        if not uuid_str:
            raise ValueError("UUID cannot be empty")
        
        # Normalize UUID
        normalized_uuid = uuid_str.lower().strip()
        
        return cls(normalized_uuid)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "organization_id": self.value,
            "type": self._get_type()
        }
    
    def _get_type(self) -> str:
        """Get the type of organization ID"""
        if self._is_uuid(self.value):
            return "uuid"
        elif self._is_hostname(self.value):
            return "hostname"
        else:
            return "custom" 