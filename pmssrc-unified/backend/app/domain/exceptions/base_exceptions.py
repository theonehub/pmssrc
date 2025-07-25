class DomainException(Exception):
    """Base exception for all domain-related errors."""
    pass

class RepositoryError(DomainException):
    """Exception raised for errors in repository operations."""
    pass 