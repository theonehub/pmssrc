"""
Employee Salary Domain Exceptions
"""

from typing import List


class EmployeeSalaryError(Exception):
    """Base exception for employee salary operations."""
    pass


class EmployeeSalaryValidationError(EmployeeSalaryError):
    """Raised when employee salary validation fails."""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class EmployeeSalaryNotFoundError(EmployeeSalaryError):
    """Raised when employee salary is not found."""
    
    def __init__(self, employee_id: str):
        super().__init__(f"Employee salary not found: {employee_id}")
        self.employee_id = employee_id


class SalaryRevisionError(EmployeeSalaryError):
    """Raised when salary revision operation fails."""
    pass 