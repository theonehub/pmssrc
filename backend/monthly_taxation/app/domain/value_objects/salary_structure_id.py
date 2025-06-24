"""
Salary Structure ID Value Object
"""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class SalaryStructureId:
    """Value object for salary structure identifiers"""
    
    value: str
    
    def __post_init__(self):
        """Validate the salary structure ID format"""
        if not self.value:
            raise ValueError("Salary Structure ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Salary Structure ID must be a string")
        
        if len(self.value) < 3:
            raise ValueError("Salary Structure ID must be at least 3 characters long")
    
    @classmethod
    def generate(cls) -> 'SalaryStructureId':
        """Generate a new unique salary structure ID"""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: str) -> 'SalaryStructureId':
        """Create SalaryStructureId from string"""
        return cls(value.strip())
    
    def __str__(self) -> str:
        return self.value 