"""
Report ID Value Object
Immutable value object for report identification
"""

from dataclasses import dataclass
from typing import Any
import uuid


@dataclass(frozen=True)
class ReportId:
    """
    Report ID value object.
    
    Immutable identifier for reports with validation.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate report ID format."""
        if not self.value:
            raise ValueError("Report ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Report ID must be a string")
        
        if len(self.value.strip()) == 0:
            raise ValueError("Report ID cannot be whitespace only")
    
    @classmethod
    def generate(cls) -> 'ReportId':
        """Generate a new unique report ID."""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: str) -> 'ReportId':
        """Create report ID from string."""
        return cls(value.strip())
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        """Equality comparison."""
        if not isinstance(other, ReportId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.value) 