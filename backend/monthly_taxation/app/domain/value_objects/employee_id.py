"""
Employee ID Value Object
"""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class EmployeeId:
    """Value object for employee identifiers"""
    
    value: str
    
    def __post_init__(self):
        """Validate the employee ID format"""
        if not self.value:
            raise ValueError("Employee ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Employee ID must be a string")
        
        if len(self.value) < 3:
            raise ValueError("Employee ID must be at least 3 characters long")
    
    @classmethod
    def generate(cls) -> 'EmployeeId':
        """Generate a new unique employee ID"""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: str) -> 'EmployeeId':
        """Create EmployeeId from string"""
        return cls(value.strip())
    
    def __str__(self) -> str:
        return self.value 