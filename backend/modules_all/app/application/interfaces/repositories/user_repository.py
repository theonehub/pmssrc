"""
User Repository Interfaces
Following Interface Segregation Principle for user data access
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.user import User
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_credentials import UserRole, UserStatus, Gender
from app.application.dto.user_dto import (
    UserSearchFiltersDTO, UserStatisticsDTO, 
    UserAnalyticsDTO, UserProfileCompletionDTO
)


class UserCommandRepository(ABC):
    """
    Repository interface for user write operations.
    
    Follows SOLID principles:
    - SRP: Only handles write operations
    - OCP: Can be extended with new implementations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def save(self, user: User, hostname: str) -> User:
        """
        Save a user (create or update).
        
        Args:
            user: User entity to save
            hostname: Organisation hostname for database selection
            
        Returns:
            Saved user entity
            
        Raises:
            UserConflictError: If user conflicts with existing data
            UserValidationError: If user data is invalid
        """
        pass
    
    @abstractmethod
    async def save_batch(self, users: List[User], organisation_id: Optional[str] = None) -> List[User]:
        """
        Save multiple users in a batch operation.
        
        Args:
            users: List of user entities to save
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of saved user entities
            
        Raises:
            UserValidationError: If any user data is invalid
        """
        pass
    
    @abstractmethod
    async def delete(self, employee_id: EmployeeId, soft_delete: bool = True, organisation_id: Optional[str] = None) -> bool:
        """
        Delete a user by ID.
        
        Args:
            employee_id: User ID to delete
            soft_delete: Whether to soft delete (mark as deleted) or hard delete
            organisation_id: Organisation ID for database selection
            
        Returns:
            True if user was deleted, False if not found
            
        Raises:
            UserValidationError: If deletion validation fails
        """
        pass


class UserQueryRepository(ABC):
    """
    Repository interface for user read operations.
    
    Follows SOLID principles:
    - SRP: Only handles read operations
    - OCP: Can be extended with new query methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for query operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_by_id(self, employee_id: EmployeeId, organisation_id: Optional[str] = None) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            employee_id: User ID to search for
            organisation_id: Organisation ID for database selection
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str, organisation_id: Optional[str] = None) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            organisation_id: Organisation ID for database selection
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str, organisation_id: Optional[str] = None) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            organisation_id: Organisation ID for database selection
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_mobile(self, mobile: str, organisation_id: Optional[str] = None) -> Optional[User]:
        """
        Get user by mobile number.
        
        Args:
            mobile: Mobile number to search for
            organisation_id: Organisation ID for database selection
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_pan_number(self, pan_number: str, organisation_id: Optional[str] = None) -> Optional[User]:
        """
        Get user by PAN number.
        
        Args:
            pan_number: PAN number to search for
            organisation_id: Organisation ID for database selection
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False,
        include_deleted: bool = False,
        organisation_id: Optional[str] = None
    ) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive users
            include_deleted: Whether to include deleted users
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of user entities
        """
        pass
    
    @abstractmethod
    async def search(self, filters: UserSearchFiltersDTO, organisation_id: Optional[str] = None) -> List[User]:
        """
        Search users with filters.
        
        Args:
            filters: Search filters and pagination parameters
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of user entities matching filters
        """
        pass
    
    @abstractmethod
    async def get_by_role(self, role: UserRole, organisation_id: Optional[str] = None) -> List[User]:
        """
        Get users by role.
        
        Args:
            role: User role to filter by
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of users with specified role
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, status: UserStatus, organisation_id: Optional[str] = None) -> List[User]:
        """
        Get users by status.
        
        Args:
            status: User status to filter by
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of users with specified status
        """
        pass
    
    @abstractmethod
    async def get_by_department(self, department: str, organisation_id: Optional[str] = None) -> List[User]:
        """
        Get users by department.
        
        Args:
            department: Department to filter by
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of users in specified department
        """
        pass
    
    @abstractmethod
    async def get_by_manager(self, manager_id: EmployeeId, organisation_id: Optional[str] = None) -> List[User]:
        """
        Get users by manager.
        
        Args:
            manager_id: Manager ID to filter by
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of users under specified manager
        """
        pass
    
    @abstractmethod
    async def get_active_users(self, organisation_id: Optional[str] = None) -> List[User]:
        """
        Get all active users.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of active user entities
        """
        pass
    
    @abstractmethod
    async def get_locked_users(self, organisation_id: Optional[str] = None) -> List[User]:
        """
        Get all locked users.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of locked user entities
        """
        pass
    
    @abstractmethod
    async def count_total(self, include_deleted: bool = False, organisation_id: Optional[str] = None) -> int:
        """
        Count total number of users.
        
        Args:
            include_deleted: Whether to include deleted users
            organisation_id: Organisation ID for database selection
            
        Returns:
            Total count of users
        """
        pass
    
    @abstractmethod
    async def count_by_status(self, status: UserStatus, organisation_id: Optional[str] = None) -> int:
        """
        Count users by status.
        
        Args:
            status: User status to count
            organisation_id: Organisation ID for database selection
            
        Returns:
            Count of users with specified status
        """
        pass
    
    @abstractmethod
    async def count_by_role(self, role: UserRole, organisation_id: Optional[str] = None) -> int:
        """
        Count users by role.
        
        Args:
            role: User role to count
            organisation_id: Organisation ID for database selection
            
        Returns:
            Count of users with specified role
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str, exclude_id: Optional[EmployeeId] = None, organisation_id: Optional[str] = None) -> bool:
        """
        Check if user exists by email.
        
        Args:
            email: Email to check
            exclude_id: User ID to exclude from check (for updates)
            organisation_id: Organisation ID for database selection
            
        Returns:
            True if user exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_mobile(self, mobile: str, exclude_id: Optional[EmployeeId] = None, organisation_id: Optional[str] = None) -> bool:
        """
        Check if user exists by mobile number.
        
        Args:
            mobile: Mobile number to check
            exclude_id: User ID to exclude from check (for updates)
            organisation_id: Organisation ID for database selection
            
        Returns:
            True if user exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[EmployeeId] = None, organisation_id: Optional[str] = None) -> bool:
        """
        Check if user exists by PAN number.
        
        Args:
            pan_number: PAN number to check
            exclude_id: User ID to exclude from check (for updates)
            organisation_id: Organisation ID for database selection
            
        Returns:
            True if user exists, False otherwise
        """
        pass


class UserAnalyticsRepository(ABC):
    """
    Repository interface for user analytics and reporting operations.
    
    Provides statistical and analytical data about users for business intelligence.
    """
    
    @abstractmethod
    async def get_statistics(self, organisation_id: Optional[str] = None) -> UserStatisticsDTO:
        """
        Get comprehensive user statistics.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            User statistics data
        """
        pass
    
    @abstractmethod
    async def get_analytics(self, organisation_id: Optional[str] = None) -> UserAnalyticsDTO:
        """
        Get detailed user analytics.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            User analytics data
        """
        pass
    
    @abstractmethod
    async def get_users_by_role_count(self, organisation_id: Optional[str] = None) -> Dict[str, int]:
        """
        Get user count by role.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            Dictionary mapping role to user count
        """
        pass
    
    @abstractmethod
    async def get_users_by_status_count(self, organisation_id: Optional[str] = None) -> Dict[str, int]:
        """
        Get user count by status.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            Dictionary mapping status to user count
        """
        pass
    
    @abstractmethod
    async def get_users_by_department_count(self, organisation_id: Optional[str] = None) -> Dict[str, int]:
        """
        Get user count by department.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            Dictionary mapping department to user count
        """
        pass
    
    @abstractmethod
    async def get_login_activity_stats(self, days: int = 30, organisation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get login activity statistics.
        
        Args:
            days: Number of days to analyze
            organisation_id: Organisation ID for database selection
            
        Returns:
            Login activity statistics
        """
        pass
    
    @abstractmethod
    async def get_profile_completion_stats(self, organisation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get profile completion statistics.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            Profile completion statistics
        """
        pass
    
    @abstractmethod
    async def get_most_active_users(self, limit: int = 10, organisation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get most active users.
        
        Args:
            limit: Maximum number of users to return
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of most active users
        """
        pass
    
    @abstractmethod
    async def get_users_created_in_period(
        self, 
        start_date: datetime, 
        end_date: datetime,
        organisation_id: Optional[str] = None
    ) -> List[User]:
        """
        Get users created in a specific period.
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of users created in the period
        """
        pass
    
    @abstractmethod
    async def get_password_security_metrics(self, organisation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get password security metrics.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            Password security metrics
        """
        pass


class UserProfileRepository(ABC):
    """
    Repository interface for user profile operations.
    
    Handles profile completion tracking, document management,
    and profile-specific analytics.
    """
    
    @abstractmethod
    async def get_profile_completion(self, employee_id: EmployeeId, organisation_id: Optional[str] = None) -> UserProfileCompletionDTO:
        """
        Get profile completion for a user.
        
        Args:
            employee_id: User ID
            organisation_id: Organisation ID for database selection
            
        Returns:
            Profile completion data
        """
        pass
    
    @abstractmethod
    async def get_incomplete_profiles(self, threshold: float = 80.0, organisation_id: Optional[str] = None) -> List[UserProfileCompletionDTO]:
        """
        Get users with incomplete profiles.
        
        Args:
            threshold: Completion percentage threshold
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of incomplete profile data
        """
        pass
    
    @abstractmethod
    async def get_users_missing_documents(self, organisation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get users missing required documents.
        
        Args:
            organisation_id: Organisation ID for database selection
            
        Returns:
            List of users with missing documents
        """
        pass
    
    @abstractmethod
    async def track_profile_update(self, employee_id: EmployeeId, section: str, organisation_id: Optional[str] = None) -> None:
        """
        Track profile section update.
        
        Args:
            employee_id: User ID
            section: Profile section that was updated
            organisation_id: Organisation ID for database selection
        """
        pass


class UserBulkOperationsRepository(ABC):
    """
    Repository interface for bulk user operations.
    
    Handles batch operations like bulk updates, imports, exports,
    and mass data modifications.
    """
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        employee_ids: List[EmployeeId], 
        status: UserStatus,
        updated_by: str,
        reason: Optional[str] = None,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk update user status.
        
        Args:
            employee_ids: List of user IDs to update
            status: New status to set
            updated_by: User performing the update
            reason: Reason for status change
            organisation_id: Organisation ID for database selection
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_update_role(
        self, 
        employee_ids: List[EmployeeId], 
        role: UserRole,
        updated_by: str,
        reason: str,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk update user role.
        
        Args:
            employee_ids: List of user IDs to update
            role: New role to set
            updated_by: User performing the update
            reason: Reason for role change
            organisation_id: Organisation ID for database selection
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_update_department(
        self, 
        employee_ids: List[EmployeeId], 
        department: str,
        updated_by: str,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk update user department.
        
        Args:
            employee_ids: List of user IDs to update
            department: New department to set
            updated_by: User performing the update
            organisation_id: Organisation ID for database selection
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_export(
        self, 
        employee_ids: Optional[List[EmployeeId]] = None,
        format: str = "csv",
        include_sensitive: bool = False,
        organisation_id: Optional[str] = None
    ) -> bytes:
        """
        Bulk export user data.
        
        Args:
            employee_ids: List of user IDs to export (None for all)
            format: Export format (csv, xlsx, json)
            include_sensitive: Whether to include sensitive data
            organisation_id: Organisation ID for database selection
            
        Returns:
            Exported data as bytes
        """
        pass
    
    @abstractmethod
    async def bulk_import(
        self, 
        data: bytes, 
        format: str = "csv",
        created_by: str = "system",
        validate_only: bool = False,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk import user data.
        
        Args:
            data: Import data as bytes
            format: Import format (csv, xlsx, json)
            created_by: User performing the import
            validate_only: Whether to only validate without importing
            organisation_id: Organisation ID for database selection
            
        Returns:
            Results of bulk import operation
        """
        pass
    
    @abstractmethod
    async def bulk_password_reset(
        self, 
        employee_ids: List[EmployeeId],
        reset_by: str,
        send_email: bool = True,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk password reset for users.
        
        Args:
            employee_ids: List of user IDs to reset passwords
            reset_by: User performing the reset
            send_email: Whether to send reset emails
            organisation_id: Organisation ID for database selection
            
        Returns:
            Results of bulk password reset operation
        """
        pass


class UserRepositoryFactory(ABC):
    """
    Factory interface for creating user repository instances.
    
    Provides a centralized way to create different types of
    user repositories while maintaining loose coupling.
    """
    
    @abstractmethod
    def create_command_repository(self) -> UserCommandRepository:
        """Create user command repository instance"""
        pass
    
    @abstractmethod
    def create_query_repository(self) -> UserQueryRepository:
        """Create user query repository instance"""
        pass
    
    @abstractmethod
    def create_analytics_repository(self) -> UserAnalyticsRepository:
        """Create user analytics repository instance"""
        pass
    
    @abstractmethod
    def create_profile_repository(self) -> UserProfileRepository:
        """Create user profile repository instance"""
        pass
    
    @abstractmethod
    def create_bulk_operations_repository(self) -> UserBulkOperationsRepository:
        """Create user bulk operations repository instance"""
        pass


class UserRepository(
    UserCommandRepository,
    UserQueryRepository,
    UserAnalyticsRepository,
    UserProfileRepository,
    UserBulkOperationsRepository,
    UserRepositoryFactory
):
    """
    Combined user repository interface.
    
    Provides a single interface that combines all user repository
    operations while maintaining interface segregation principles.
    """
    pass 