"""
Tax Computation Domain Exceptions
"""

from typing import List


class TaxComputationError(Exception):
    """Base exception for tax computation operations."""
    pass


class TaxComputationValidationError(TaxComputationError):
    """Raised when tax computation validation fails."""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class TaxComputationNotFoundError(TaxComputationError):
    """Raised when tax computation is not found."""
    
    def __init__(self, computation_id: str):
        super().__init__(f"Tax computation not found: {computation_id}")
        self.computation_id = computation_id


class InvalidTaxRegimeError(TaxComputationError):
    """Raised when invalid tax regime is specified."""
    pass


class TaxCalculationError(TaxComputationError):
    """Raised when tax calculation fails."""
    pass 