"""
Salary Component Domain Exceptions
Custom exceptions for salary component business logic
"""

from typing import List, Optional


class SalaryComponentError(Exception):
    """Base exception for salary component operations."""
    pass


class SalaryComponentValidationError(SalaryComponentError):
    """Raised when salary component validation fails."""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class SalaryComponentBusinessRuleError(SalaryComponentError):
    """Raised when business rule validation fails."""
    
    def __init__(self, message: str, rule: str = None):
        super().__init__(message)
        self.rule = rule


class SalaryComponentNotFoundError(SalaryComponentError):
    """Raised when salary component is not found."""
    
    def __init__(self, component_id: str):
        super().__init__(f"Salary component not found: {component_id}")
        self.component_id = component_id


class SalaryComponentAlreadyExistsError(SalaryComponentError):
    """Raised when salary component already exists."""
    
    def __init__(self, message: str):
        super().__init__(message)


class SalaryComponentInUseError(SalaryComponentError):
    """Raised when trying to delete/modify a component that is in use."""
    
    def __init__(self, message: str):
        super().__init__(message)


class SalaryComponentConflictError(SalaryComponentError):
    """Raised when salary component operation conflicts with existing data."""
    
    def __init__(self, message: str, conflict_field: str = None):
        super().__init__(message)
        self.conflict_field = conflict_field


class FormulaValidationError(SalaryComponentError):
    """Raised when formula validation fails."""
    
    def __init__(self, formula: str, message: str):
        super().__init__(f"Invalid formula '{formula}': {message}")
        self.formula = formula


class ComponentInUseError(SalaryComponentError):
    """Raised when trying to delete a component that is in use."""
    
    def __init__(self, component_id: str, usage_count: int):
        super().__init__(
            f"Cannot delete component {component_id}: it is used in {usage_count} salary structures"
        )
        self.component_id = component_id
        self.usage_count = usage_count 