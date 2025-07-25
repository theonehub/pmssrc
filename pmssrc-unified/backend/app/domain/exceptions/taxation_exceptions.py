"""
Taxation Domain Exceptions
Custom exceptions for taxation domain operations
"""

from typing import Any, Dict, Optional


class TaxationDomainError(Exception):
    """Base exception for taxation domain errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class TaxationRecordNotFoundError(TaxationDomainError):
    """Raised when taxation record is not found."""
    
    def __init__(self, taxation_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Taxation record not found: {taxation_id}"
        super().__init__(message, details)


class TaxationValidationError(TaxationDomainError):
    """Raised when taxation data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.field = field
        if field:
            message = f"Validation error in {field}: {message}"
        super().__init__(message, details)


class TaxCalculationError(TaxationDomainError):
    """Raised when tax calculation fails."""
    
    def __init__(self, message: str, calculation_step: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.calculation_step = calculation_step
        if calculation_step:
            message = f"Tax calculation error in {calculation_step}: {message}"
        super().__init__(message, details)


class InsufficientTaxDataError(TaxationDomainError):
    """Raised when insufficient data is available for tax calculation."""
    
    def __init__(self, missing_data: str, details: Optional[Dict[str, Any]] = None):
        message = f"Insufficient tax data: {missing_data}"
        super().__init__(message, details)


class TaxRegimeError(TaxationDomainError):
    """Raised when tax regime related errors occur."""
    
    def __init__(self, message: str, regime: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.regime = regime
        if regime:
            message = f"Tax regime error ({regime}): {message}"
        super().__init__(message, details)


class DeductionLimitExceededError(TaxationDomainError):
    """Raised when deduction limits are exceeded."""
    
    def __init__(self, section: str, limit: float, attempted: float, details: Optional[Dict[str, Any]] = None):
        self.section = section
        self.limit = limit
        self.attempted = attempted
        message = f"Deduction limit exceeded for {section}: attempted ₹{attempted:,.2f}, limit ₹{limit:,.2f}"
        super().__init__(message, details)


class InvalidTaxYearError(TaxationDomainError):
    """Raised when invalid tax year is provided."""
    
    def __init__(self, tax_year: str, details: Optional[Dict[str, Any]] = None):
        message = f"Invalid tax year: {tax_year}"
        super().__init__(message, details)


class FinalizedRecordError(TaxationDomainError):
    """Raised when attempting to modify a finalized tax record."""
    
    def __init__(self, taxation_id: str, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Cannot {operation} finalized tax record: {taxation_id}"
        super().__init__(message, details)


class IncomeValidationError(TaxationValidationError):
    """Raised when income validation fails."""
    
    def __init__(self, income_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Income validation error for {income_type}: {message}", income_type, details)


class HRAValidationError(TaxationValidationError):
    """Raised when HRA validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"HRA validation error: {message}", "hra", details)


class AgeValidationError(TaxationValidationError):
    """Raised when age validation fails."""
    
    def __init__(self, age: int, details: Optional[Dict[str, Any]] = None):
        message = f"Invalid age for taxation: {age}"
        super().__init__(message, "age", details)


class DuplicateTaxationRecordError(TaxationDomainError):
    """Raised when attempting to create duplicate taxation record."""
    
    def __init__(self, employee_id: str, tax_year: str, details: Optional[Dict[str, Any]] = None):
        message = f"Taxation record already exists for user {employee_id} in tax year {tax_year}"
        super().__init__(message, details)


class TaxationRepositoryError(TaxationDomainError):
    """Raised when taxation repository operations fail."""
    
    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Repository operation '{operation}' failed: {message}", details)


class TaxationServiceError(TaxationDomainError):
    """Raised when taxation service operations fail."""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Service '{service}' error: {message}", details) 