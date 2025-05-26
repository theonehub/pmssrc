"""
Employee ID Value Object
Immutable value object representing employee identifiers
"""

from dataclasses import dataclass
import re
from typing import Union


@dataclass(frozen=True)
class EmployeeId:
    """
    Employee ID value object ensuring immutability and validation.
    
    Follows SOLID principles:
    - SRP: Only handles employee ID representation and validation
    - OCP: Can be extended without modification
    - LSP: Can be substituted anywhere EmployeeId is expected
    - ISP: Provides only ID-related operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    value: str
    
    def __post_init__(self):
        """Validate employee ID on creation"""
        if not self.value:
            raise ValueError("Employee ID cannot be empty")
        
        if not isinstance(self.value, str):
            raise ValueError("Employee ID must be a string")
        
        # Remove whitespace and convert to uppercase
        cleaned_value = self.value.strip().upper()
        object.__setattr__(self, 'value', cleaned_value)
        
        if not self._is_valid_format(cleaned_value):
            raise ValueError(f"Invalid employee ID format: {cleaned_value}")
    
    @classmethod
    def from_string(cls, value: str) -> 'EmployeeId':
        """Create EmployeeId from string"""
        return cls(value)
    
    @classmethod
    def from_int(cls, value: int, prefix: str = "EMP") -> 'EmployeeId':
        """Create EmployeeId from integer with prefix"""
        if value < 0:
            raise ValueError("Employee ID number cannot be negative")
        
        formatted_id = f"{prefix}{value:03d}"  # EMP001, EMP002, etc.
        return cls(formatted_id)
    
    def _is_valid_format(self, value: str) -> bool:
        """
        Validate employee ID format.
        
        Accepted formats:
        - EMP001, EMP002, etc. (3+ digits)
        - USR001, USR002, etc. (3+ digits)
        - Any alphanumeric string 3+ characters
        """
        # Pattern: 3+ letters followed by 3+ digits, OR 3+ alphanumeric characters
        pattern = r'^([A-Z]{3,}\d{3,}|[A-Z0-9]{3,})$'
        return bool(re.match(pattern, value))
    
    def get_prefix(self) -> str:
        """Extract prefix from employee ID (e.g., 'EMP' from 'EMP001')"""
        match = re.match(r'^([A-Z]+)', self.value)
        return match.group(1) if match else ""
    
    def get_number(self) -> int:
        """Extract number from employee ID (e.g., 1 from 'EMP001')"""
        match = re.search(r'(\d+)$', self.value)
        return int(match.group(1)) if match else 0
    
    def is_temporary(self) -> bool:
        """Check if this is a temporary employee ID"""
        return self.value.startswith('TEMP') or self.value.startswith('TMP')
    
    def is_contractor(self) -> bool:
        """Check if this is a contractor employee ID"""
        return self.value.startswith('CTR') or self.value.startswith('CONT')
    
    def is_regular(self) -> bool:
        """Check if this is a regular employee ID"""
        return self.value.startswith('EMP') or self.value.startswith('USR')
    
    def to_string(self) -> str:
        """Convert to string representation"""
        return self.value
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"EmployeeId('{self.value}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if isinstance(other, EmployeeId):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other.upper().strip()
        return False
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self.value)
    
    def __lt__(self, other: 'EmployeeId') -> bool:
        """Less than comparison for sorting"""
        if not isinstance(other, EmployeeId):
            raise TypeError("Cannot compare EmployeeId with non-EmployeeId")
        
        # Compare by prefix first, then by number
        self_prefix = self.get_prefix()
        other_prefix = other.get_prefix()
        
        if self_prefix != other_prefix:
            return self_prefix < other_prefix
        
        return self.get_number() < other.get_number()
    
    def __le__(self, other: 'EmployeeId') -> bool:
        """Less than or equal comparison"""
        return self == other or self < other
    
    def __gt__(self, other: 'EmployeeId') -> bool:
        """Greater than comparison"""
        return not self <= other
    
    def __ge__(self, other: 'EmployeeId') -> bool:
        """Greater than or equal comparison"""
        return self == other or self > other 