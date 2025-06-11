"""
User Domain Exceptions
Custom exceptions for user-related domain operations
"""

from typing import List, Optional


class UserError(Exception):
    """Base exception for user operations."""
    pass


class UserValidationError(UserError):
    """Raised when user validation fails."""
    
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.errors = errors or []


class UserBusinessRuleError(UserError):
    """Raised when business rule validation fails."""
    
    def __init__(self, message: str, rule: Optional[str] = None):
        super().__init__(message)
        self.rule = rule


class UserNotFoundError(UserError):
    """Raised when user is not found."""
    
    def __init__(self, user_id: str):
        super().__init__(f"User not found: {user_id}")
        self.user_id = user_id


class UserConflictError(UserError):
    """Raised when user operation conflicts with existing data."""
    
    def __init__(self, message: str, conflict_field: Optional[str] = None):
        super().__init__(message)
        self.conflict_field = conflict_field


class UserAuthenticationError(UserError):
    """Raised when user authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class UserAuthorizationError(UserError):
    """Raised when user authorization fails."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message)


class UserInactiveError(UserError):
    """Raised when attempting to use inactive user."""
    
    def __init__(self, user_id: str):
        super().__init__(f"User is inactive: {user_id}")
        self.user_id = user_id


class UserPasswordError(UserError):
    """Raised when password-related operations fail."""
    
    def __init__(self, message: str = "Password operation failed"):
        super().__init__(message)


class UserEmailConflictError(UserConflictError):
    """Raised when email address already exists."""
    
    def __init__(self, email: str):
        super().__init__(f"Email already exists: {email}", "email")
        self.email = email


class UserUsernameConflictError(UserConflictError):
    """Raised when username already exists."""
    
    def __init__(self, username: str):
        super().__init__(f"Username already exists: {username}", "username")
        self.username = username


class UserEmployeeIdConflictError(UserConflictError):
    """Raised when employee ID already exists."""
    
    def __init__(self, employee_id: str):
        super().__init__(f"Employee ID already exists: {employee_id}", "employee_id")
        self.employee_id = employee_id 