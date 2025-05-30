"""
User Repository Interfaces
Following Interface Segregation Principle for user data access
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.entities.user import User
from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.user_credentials import UserRole, UserStatus, Gender
from application.dto.user_dto import (
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
    async def save(self, user: User) -> User:
        """
        Save a user (create or update).
        
        Args:
            user: User entity to save
            
        Returns:
            Saved user entity
            
        Raises:
            UserConflictError: If user conflicts with existing data
            UserValidationError: If user data is invalid
        """
        pass
    
    @abstractmethod
    async def save_batch(self, users: List[User]) -> List[User]:
        """
        Save multiple users in a batch operation.
        
        Args:
            users: List of user entities to save
            
        Returns:
            List of saved user entities
            
        Raises:
            UserValidationError: If any user data is invalid
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: EmployeeId, soft_delete: bool = True) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id: ID of user to delete
            soft_delete: Whether to perform soft delete
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            UserBusinessRuleError: If deletion violates business rules
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
    async def get_by_id(self, user_id: EmployeeId) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_mobile(self, mobile: str) -> Optional[User]:
        """
        Get user by mobile number.
        
        Args:
            mobile: Mobile number to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_pan_number(self, pan_number: str) -> Optional[User]:
        """
        Get user by PAN number.
        
        Args:
            pan_number: PAN number to search for
            
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
        include_deleted: bool = False
    ) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive users
            include_deleted: Whether to include deleted users
            
        Returns:
            List of user entities
        """
        pass
    
    @abstractmethod
    async def search(self, filters: UserSearchFiltersDTO) -> List[User]:
        """
        Search users with filters.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            List of user entities matching filters
        """
        pass
    
    @abstractmethod
    async def get_by_role(self, role: UserRole) -> List[User]:
        """
        Get users by role.
        
        Args:
            role: User role to filter by
            
        Returns:
            List of users with specified role
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, status: UserStatus) -> List[User]:
        """
        Get users by status.
        
        Args:
            status: User status to filter by
            
        Returns:
            List of users with specified status
        """
        pass
    
    @abstractmethod
    async def get_by_department(self, department: str) -> List[User]:
        """
        Get users by department.
        
        Args:
            department: Department to filter by
            
        Returns:
            List of users in specified department
        """
        pass
    
    @abstractmethod
    async def get_by_manager(self, manager_id: EmployeeId) -> List[User]:
        """
        Get users by manager.
        
        Args:
            manager_id: Manager ID to filter by
            
        Returns:
            List of users under specified manager
        """
        pass
    
    @abstractmethod
    async def get_active_users(self) -> List[User]:
        """
        Get all active users.
        
        Returns:
            List of active user entities
        """
        pass
    
    @abstractmethod
    async def get_locked_users(self) -> List[User]:
        """
        Get all locked users.
        
        Returns:
            List of locked user entities
        """
        pass
    
    @abstractmethod
    async def count_total(self, include_deleted: bool = False) -> int:
        """
        Count total number of users.
        
        Args:
            include_deleted: Whether to include deleted users
            
        Returns:
            Total count of users
        """
        pass
    
    @abstractmethod
    async def count_by_status(self, status: UserStatus) -> int:
        """
        Count users by status.
        
        Args:
            status: User status to count
            
        Returns:
            Count of users with specified status
        """
        pass
    
    @abstractmethod
    async def count_by_role(self, role: UserRole) -> int:
        """
        Count users by role.
        
        Args:
            role: User role to count
            
        Returns:
            Count of users with specified role
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str, exclude_id: Optional[EmployeeId] = None) -> bool:
        """
        Check if user exists by email.
        
        Args:
            email: Email to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if user exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_mobile(self, mobile: str, exclude_id: Optional[EmployeeId] = None) -> bool:
        """
        Check if user exists by mobile number.
        
        Args:
            mobile: Mobile number to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if user exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[EmployeeId] = None) -> bool:
        """
        Check if user exists by PAN number.
        
        Args:
            pan_number: PAN number to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if user exists, False otherwise
        """
        pass


class UserAnalyticsRepository(ABC):
    """
    Repository interface for user analytics and reporting.
    
    Provides methods for generating user statistics, analytics,
    and insights for business intelligence purposes.
    """
    
    @abstractmethod
    async def get_statistics(self) -> UserStatisticsDTO:
        """
        Get comprehensive user statistics.
        
        Returns:
            User statistics including counts, distributions, and trends
        """
        pass
    
    @abstractmethod
    async def get_analytics(self) -> UserAnalyticsDTO:
        """
        Get detailed user analytics.
        
        Returns:
            User analytics including activity patterns and insights
        """
        pass
    
    @abstractmethod
    async def get_users_by_role_count(self) -> Dict[str, int]:
        """
        Get count of users by role.
        
        Returns:
            Dictionary mapping role to user count
        """
        pass
    
    @abstractmethod
    async def get_users_by_status_count(self) -> Dict[str, int]:
        """
        Get count of users by status.
        
        Returns:
            Dictionary mapping status to user count
        """
        pass
    
    @abstractmethod
    async def get_users_by_department_count(self) -> Dict[str, int]:
        """
        Get count of users by department.
        
        Returns:
            Dictionary mapping department to user count
        """
        pass
    
    @abstractmethod
    async def get_login_activity_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get login activity statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Login activity statistics and patterns
        """
        pass
    
    @abstractmethod
    async def get_profile_completion_stats(self) -> Dict[str, Any]:
        """
        Get profile completion statistics.
        
        Returns:
            Profile completion statistics and trends
        """
        pass
    
    @abstractmethod
    async def get_most_active_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most active users by login frequency.
        
        Args:
            limit: Maximum number of users to return
            
        Returns:
            List of most active users with activity metrics
        """
        pass
    
    @abstractmethod
    async def get_users_created_in_period(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[User]:
        """
        Get users created within a specific period.
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            
        Returns:
            List of users created in the specified period
        """
        pass
    
    @abstractmethod
    async def get_password_security_metrics(self) -> Dict[str, Any]:
        """
        Get password security metrics.
        
        Returns:
            Password security statistics and recommendations
        """
        pass


class UserProfileRepository(ABC):
    """
    Repository interface for user profile management.
    
    Handles profile completion tracking, document management,
    and profile-related analytics.
    """
    
    @abstractmethod
    async def get_profile_completion(self, user_id: EmployeeId) -> UserProfileCompletionDTO:
        """
        Get profile completion status for a user.
        
        Args:
            user_id: User ID to check
            
        Returns:
            Profile completion details and recommendations
        """
        pass
    
    @abstractmethod
    async def get_incomplete_profiles(self, threshold: float = 80.0) -> List[UserProfileCompletionDTO]:
        """
        Get users with incomplete profiles.
        
        Args:
            threshold: Completion percentage threshold
            
        Returns:
            List of users with incomplete profiles
        """
        pass
    
    @abstractmethod
    async def get_users_missing_documents(self) -> List[Dict[str, Any]]:
        """
        Get users with missing documents.
        
        Returns:
            List of users and their missing documents
        """
        pass
    
    @abstractmethod
    async def track_profile_update(self, user_id: EmployeeId, section: str) -> None:
        """
        Track profile section update.
        
        Args:
            user_id: User ID
            section: Profile section that was updated
        """
        pass


class UserBulkOperationsRepository(ABC):
    """
    Repository interface for bulk user operations.
    
    Handles batch operations like bulk updates, imports, exports,
    and mass status changes.
    """
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        user_ids: List[EmployeeId], 
        status: UserStatus,
        updated_by: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk update user status.
        
        Args:
            user_ids: List of user IDs to update
            status: New status to set
            updated_by: User performing the update
            reason: Reason for status change
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_update_role(
        self, 
        user_ids: List[EmployeeId], 
        role: UserRole,
        updated_by: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Bulk update user role.
        
        Args:
            user_ids: List of user IDs to update
            role: New role to set
            updated_by: User performing the update
            reason: Reason for role change
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_update_department(
        self, 
        user_ids: List[EmployeeId], 
        department: str,
        updated_by: str
    ) -> Dict[str, Any]:
        """
        Bulk update user department.
        
        Args:
            user_ids: List of user IDs to update
            department: New department to set
            updated_by: User performing the update
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_export(
        self, 
        user_ids: Optional[List[EmployeeId]] = None,
        format: str = "csv",
        include_sensitive: bool = False
    ) -> bytes:
        """
        Bulk export user data.
        
        Args:
            user_ids: List of user IDs to export (None for all)
            format: Export format (csv, xlsx, json)
            include_sensitive: Whether to include sensitive data
            
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
        validate_only: bool = False
    ) -> Dict[str, Any]:
        """
        Bulk import user data.
        
        Args:
            data: Import data as bytes
            format: Import format (csv, xlsx, json)
            created_by: User performing the import
            validate_only: Whether to only validate without importing
            
        Returns:
            Results of bulk import operation
        """
        pass
    
    @abstractmethod
    async def bulk_password_reset(
        self, 
        user_ids: List[EmployeeId],
        reset_by: str,
        send_email: bool = True
    ) -> Dict[str, Any]:
        """
        Bulk password reset for users.
        
        Args:
            user_ids: List of user IDs to reset passwords
            reset_by: User performing the reset
            send_email: Whether to send reset emails
            
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
    UserBulkOperationsRepository
):
    """
    Combined user repository interface.
    
    Aggregates all user repository interfaces for convenience
    when a single implementation handles all operations.
    """
    pass 