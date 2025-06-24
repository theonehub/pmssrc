"""
Tax Computation ID Value Object
"""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TaxComputationId:
    """Value object for tax computation identifiers"""
    
    value: str
    
    def __post_init__(self):
        """Validate the tax computation ID format"""
        if not self.value:
            raise ValueError("Tax Computation ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Tax Computation ID must be a string")
        
        if len(self.value) < 3:
            raise ValueError("Tax Computation ID must be at least 3 characters long")
    
    @classmethod
    def generate(cls) -> 'TaxComputationId':
        """Generate a new unique tax computation ID"""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: str) -> 'TaxComputationId':
        """Create TaxComputationId from string"""
        return cls(value.strip())
    
    def __str__(self) -> str:
        return self.value 