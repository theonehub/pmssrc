"""
User Repository Interface
Abstract repository interface for user data access
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.domain.entities.user import User
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.email import Email
from app.application.dto.user_dto import UserSearchFiltersDTO


class UserRepository(ABC):
    """
    Abstract repository interface for user data access.
    
    Defines the contract for user data persistence operations
    with organization context support.
    """
    
    @abstractmethod
    async def save(self, user: User, hostname: str) -> User:
        """
        Save user entity to organization-specific database.
        
        Args:
            user: User entity to save
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            User: Saved user entity
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UserId, hostname: str) -> Optional[User]:
        """
        Get user by ID from organization-specific database.
        
        Args:
            user_id: User ID to find
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            Optional[User]: User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: Email, hostname: str) -> Optional[User]:
        """
        Get user by email from organization-specific database.
        
        Args:
            email: Email address to find
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            Optional[User]: User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str, hostname: str) -> Optional[User]:
        """
        Get user by username from organization-specific database.
        
        Args:
            username: Username to find
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            Optional[User]: User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_employee_id(self, employee_id: str, hostname: str) -> Optional[User]:
        """
        Get user by employee ID from organization-specific database.
        
        Args:
            employee_id: Employee ID to find
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            Optional[User]: User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_with_filters(
        self, 
        filters: UserSearchFiltersDTO, 
        hostname: str
    ) -> Tuple[List[User], int]:
        """
        Find users with filters from organization-specific database.
        
        Args:
            filters: Search filters and pagination
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            Tuple[List[User], int]: List of users and total count
        """
        pass
    
    @abstractmethod
    async def find_by_role(self, role: str, hostname: str) -> List[User]:
        """
        Find users by role from organization-specific database.
        
        Args:
            role: Role to search for
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            List[User]: List of users with the specified role
        """
        pass
    
    @abstractmethod
    async def find_active_users(self, hostname: str) -> List[User]:
        """
        Find all active users from organization-specific database.
        
        Args:
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            List[User]: List of active users
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId, hostname: str) -> bool:
        """
        Delete user from organization-specific database.
        
        Args:
            user_id: User ID to delete
            hostname: Organization hostname for multi-tenancy
            
        Returns:
            bool: True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: Email, hostname: str, exclude_user_id: Optional[UserId] = None) -> bool:
        """
        Check if user exists by email in organization-specific database.
        
        Args:
            email: Email address to check
            hostname: Organization hostname for multi-tenancy
            exclude_user_id: User ID to exclude from check (for updates)
            
        Returns:
            bool: True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str, hostname: str, exclude_user_id: Optional[UserId] = None) -> bool:
        """
        Check if user exists by username in organization-specific database.
        
        Args:
            username: Username to check
            hostname: Organization hostname for multi-tenancy
            exclude_user_id: User ID to exclude from check (for updates)
            
        Returns:
            bool: True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_employee_id(self, employee_id: str, hostname: str, exclude_user_id: Optional[UserId] = None) -> bool:
        """
        Check if user exists by employee ID in organization-specific database.
        
        Args:
            employee_id: Employee ID to check
            hostname: Organization hostname for multi-tenancy
            exclude_user_id: User ID to exclude from check (for updates)
            
        Returns:
            bool: True if exists, False otherwise
        """
        pass 