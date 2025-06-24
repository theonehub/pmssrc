"""
Component Type Value Objects
Enums for salary component types and value types
"""

from enum import Enum


class ComponentType(Enum):
    """
    Type of salary component indicating its purpose in payroll calculation.
    """
    EARNING = "EARNING"
    DEDUCTION = "DEDUCTION"
    REIMBURSEMENT = "REIMBURSEMENT"
    
    @classmethod
    def from_string(cls, value: str) -> 'ComponentType':
        """Create ComponentType from string"""
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid component type: {value}")


class ValueType(Enum):
    """
    How the component value is determined.
    """
    FIXED = "FIXED"          # Fixed amount
    FORMULA = "FORMULA"      # Calculated using formula
    VARIABLE = "VARIABLE"    # Manually entered each time
    
    @classmethod
    def from_string(cls, value: str) -> 'ValueType':
        """Create ValueType from string"""
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid value type: {value}")


class CalculationFrequency(Enum):
    """
    How often the component is calculated/applied.
    """
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"
    ONE_TIME = "ONE_TIME"
    
    @classmethod
    def from_string(cls, value: str) -> 'CalculationFrequency':
        """Create CalculationFrequency from string"""
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid calculation frequency: {value}") 