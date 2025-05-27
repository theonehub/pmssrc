"""
User Service Interfaces
Following Interface Segregation Principle for user business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.user import User
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_credentials import UserRole, UserStatus, Gender
from app.application.dto.user_dto import (
    CreateUserRequestDTO, UpdateUserRequestDTO, UpdateUserDocumentsRequestDTO,
    ChangeUserPasswordRequestDTO, ChangeUserRoleRequestDTO, UserStatusUpdateRequestDTO,
    UserSearchFiltersDTO, UserLoginRequestDTO, UserResponseDTO, UserSummaryDTO, 
    UserListResponseDTO, UserStatisticsDTO, UserAnalyticsDTO, UserLoginResponseDTO,
    UserProfileCompletionDTO, BulkUserUpdateDTO, BulkUserUpdateResultDTO
)


class UserCommandService(ABC):
    """
    Service interface for user command operations.
    
    Follows SOLID principles:
    - SRP: Only handles command operations
    - OCP: Can be extended with new command operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def create_user(self, request: CreateUserRequestDTO) -> UserResponseDTO:
        """
        Create a new user.
        
        Args:
            request: User creation request DTO
            
        Returns:
            Created user response DTO
            
        Raises:
            UserValidationError: If request data is invalid
            UserConflictError: If user already exists
            UserBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def update_user(
        self, 
        user_id: str, 
        request: UpdateUserRequestDTO
    ) -> UserResponseDTO:
        """
        Update an existing user.
        
        Args:
            user_id: ID of user to update
            request: User update request DTO
            
        Returns:
            Updated user response DTO
            
        Raises:
            UserNotFoundError: If user not found
            UserValidationError: If request data is invalid
            UserBusinessRuleError: If business rules are violated
        """
        pass
    
    @abstractmethod
    async def update_user_documents(
        self, 
        user_id: str, 
        request: UpdateUserDocumentsRequestDTO
    ) -> UserResponseDTO:
        """
        Update user documents.
        
        Args:
            user_id: ID of user to update
            request: Documents update request DTO
            
        Returns:
            Updated user response DTO
            
        Raises:
            UserNotFoundError: If user not found
            UserValidationError: If request data is invalid
        """
        pass
    
    @abstractmethod
    async def change_user_password(
        self, 
        user_id: str, 
        request: ChangeUserPasswordRequestDTO
    ) -> UserResponseDTO:
        """
        Change user password.
        
        Args:
            user_id: ID of user to update
            request: Password change request DTO
            
        Returns:
            Updated user response DTO
            
        Raises:
            UserNotFoundError: If user not found
            UserValidationError: If request data is invalid
            UserAuthenticationError: If current password is incorrect
            UserBusinessRuleError: If password change is not allowed
        """
        pass
    
    @abstractmethod
    async def change_user_role(
        self, 
        user_id: str, 
        request: ChangeUserRoleRequestDTO
    ) -> UserResponseDTO:
        """
        Change user role.
        
        Args:
            user_id: ID of user to update
            request: Role change request DTO
            
        Returns:
            Updated user response DTO
            
        Raises:
            UserNotFoundError: If user not found
            UserValidationError: If request data is invalid
            UserAuthorizationError: If role change is not authorized
            UserBusinessRuleError: If role change violates business rules
        """
        pass
    
    @abstractmethod
    async def update_user_status(
        self, 
        user_id: str, 
        request: UserStatusUpdateRequestDTO
    ) -> UserResponseDTO:
        """
        Update user status (activate, deactivate, suspend, unlock).
        
        Args:
            user_id: ID of user to update
            request: Status update request DTO
            
        Returns:
            Updated user response DTO
            
        Raises:
            UserNotFoundError: If user not found
            UserValidationError: If request data is invalid
            UserBusinessRuleError: If status change is not allowed
        """
        pass
    
    @abstractmethod
    async def assign_manager(
        self, 
        user_id: str, 
        manager_id: str,
        assigned_by: str
    ) -> UserResponseDTO:
        """
        Assign manager to user.
        
        Args:
            user_id: ID of user
            manager_id: ID of manager to assign
            assigned_by: User performing the assignment
            
        Returns:
            Updated user response DTO
            
        Raises:
            UserNotFoundError: If user or manager not found
            UserBusinessRuleError: If assignment violates business rules
        """
        pass
    
    @abstractmethod
    async def delete_user(
        self, 
        user_id: str, 
        deletion_reason: str,
        deleted_by: Optional[str] = None,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: ID of user to delete
            deletion_reason: Reason for deletion
            deleted_by: User performing the deletion
            soft_delete: Whether to perform soft delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            UserNotFoundError: If user not found
            UserBusinessRuleError: If deletion is not allowed
        """
        pass


class UserQueryService(ABC):
    """
    Service interface for user query operations.
    
    Follows SOLID principles:
    - SRP: Only handles query operations
    - OCP: Can be extended with new query operations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for query operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponseDTO]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserResponseDTO]:
        """
        Get user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_by_mobile(self, mobile: str) -> Optional[UserResponseDTO]:
        """
        Get user by mobile number.
        
        Args:
            mobile: Mobile number to search for
            
        Returns:
            User response DTO if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all_users(
        self, 
        skip: int = 0, 
        limit: int = 20,
        include_inactive: bool = False,
        include_deleted: bool = False
    ) -> UserListResponseDTO:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_inactive: Whether to include inactive users
            include_deleted: Whether to include deleted users
            
        Returns:
            Paginated list of user summary DTOs
        """
        pass
    
    @abstractmethod
    async def search_users(self, filters: UserSearchFiltersDTO) -> UserListResponseDTO:
        """
        Search users with filters.
        
        Args:
            filters: Search filters and pagination parameters
            
        Returns:
            Paginated list of user summary DTOs matching filters
        """
        pass
    
    @abstractmethod
    async def get_users_by_role(self, role: str) -> List[UserSummaryDTO]:
        """
        Get users by role.
        
        Args:
            role: User role to filter by
            
        Returns:
            List of users with specified role
        """
        pass
    
    @abstractmethod
    async def get_users_by_status(self, status: str) -> List[UserSummaryDTO]:
        """
        Get users by status.
        
        Args:
            status: User status to filter by
            
        Returns:
            List of users with specified status
        """
        pass
    
    @abstractmethod
    async def get_users_by_department(self, department: str) -> List[UserSummaryDTO]:
        """
        Get users by department.
        
        Args:
            department: Department to filter by
            
        Returns:
            List of users in specified department
        """
        pass
    
    @abstractmethod
    async def get_users_by_manager(self, manager_id: str) -> List[UserSummaryDTO]:
        """
        Get users by manager.
        
        Args:
            manager_id: Manager ID to filter by
            
        Returns:
            List of users under specified manager
        """
        pass
    
    @abstractmethod
    async def check_user_exists(
        self, 
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Check if user exists by various identifiers.
        
        Args:
            email: Email to check
            mobile: Mobile number to check
            pan_number: PAN number to check
            exclude_id: User ID to exclude from check
            
        Returns:
            Dictionary indicating existence for each checked field
        """
        pass


class UserAuthenticationService(ABC):
    """
    Service interface for user authentication operations.
    
    Handles login, logout, password management, and session management.
    """
    
    @abstractmethod
    async def authenticate_user(self, request: UserLoginRequestDTO) -> UserLoginResponseDTO:
        """
        Authenticate user with credentials.
        
        Args:
            request: Login request DTO
            
        Returns:
            Login response DTO with tokens and user info
            
        Raises:
            UserAuthenticationError: If authentication fails
            UserBusinessRuleError: If user cannot login (locked, inactive, etc.)
        """
        pass
    
    @abstractmethod
    async def logout_user(
        self, 
        user_id: str, 
        session_token: str,
        logout_method: str = "manual"
    ) -> bool:
        """
        Logout user and invalidate session.
        
        Args:
            user_id: User ID
            session_token: Session token to invalidate
            logout_method: Method of logout (manual, timeout, forced)
            
        Returns:
            True if logout successful
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> UserLoginResponseDTO:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New login response DTO with refreshed tokens
            
        Raises:
            UserAuthenticationError: If refresh token is invalid
        """
        pass
    
    @abstractmethod
    async def reset_password(
        self, 
        user_id: str, 
        reset_by: str,
        send_email: bool = True
    ) -> str:
        """
        Reset user password.
        
        Args:
            user_id: User ID
            reset_by: User performing the reset
            send_email: Whether to send reset email
            
        Returns:
            Temporary password or reset token
            
        Raises:
            UserNotFoundError: If user not found
            UserBusinessRuleError: If reset is not allowed
        """
        pass
    
    @abstractmethod
    async def validate_session(self, session_token: str) -> Optional[UserResponseDTO]:
        """
        Validate session token and return user info.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            User response DTO if session is valid, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get active sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active session information
        """
        pass
    
    @abstractmethod
    async def terminate_all_sessions(self, user_id: str, terminated_by: str) -> int:
        """
        Terminate all active sessions for a user.
        
        Args:
            user_id: User ID
            terminated_by: User performing the termination
            
        Returns:
            Number of sessions terminated
        """
        pass


class UserAuthorizationService(ABC):
    """
    Service interface for user authorization operations.
    
    Handles permission checking, role management, and access control.
    """
    
    @abstractmethod
    async def check_permission(
        self, 
        user_id: str, 
        permission: str
    ) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            user_id: User ID
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        pass
    
    @abstractmethod
    async def check_resource_permission(
        self, 
        user_id: str, 
        resource: str, 
        action: str
    ) -> bool:
        """
        Check if user has permission for specific resource action.
        
        Args:
            user_id: User ID
            resource: Resource name
            action: Action to perform
            
        Returns:
            True if user has permission, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of user permissions
        """
        pass
    
    @abstractmethod
    async def add_custom_permission(
        self, 
        user_id: str, 
        permission: str,
        granted_by: str
    ) -> UserResponseDTO:
        """
        Add custom permission to user.
        
        Args:
            user_id: User ID
            permission: Permission to add
            granted_by: User granting the permission
            
        Returns:
            Updated user response DTO
        """
        pass
    
    @abstractmethod
    async def remove_custom_permission(
        self, 
        user_id: str, 
        permission: str,
        removed_by: str
    ) -> UserResponseDTO:
        """
        Remove custom permission from user.
        
        Args:
            user_id: User ID
            permission: Permission to remove
            removed_by: User removing the permission
            
        Returns:
            Updated user response DTO
        """
        pass
    
    @abstractmethod
    async def can_access_user_data(
        self, 
        requesting_user_id: str, 
        target_user_id: str
    ) -> bool:
        """
        Check if requesting user can access target user's data.
        
        Args:
            requesting_user_id: ID of user making the request
            target_user_id: ID of user whose data is being accessed
            
        Returns:
            True if access is allowed, False otherwise
        """
        pass


class UserAnalyticsService(ABC):
    """
    Service interface for user analytics and reporting.
    
    Provides methods for generating user statistics, analytics,
    and insights for business intelligence purposes.
    """
    
    @abstractmethod
    async def get_user_statistics(self) -> UserStatisticsDTO:
        """
        Get comprehensive user statistics.
        
        Returns:
            User statistics including counts, distributions, and trends
        """
        pass
    
    @abstractmethod
    async def get_user_analytics(self) -> UserAnalyticsDTO:
        """
        Get detailed user analytics.
        
        Returns:
            User analytics including activity patterns and insights
        """
        pass
    
    @abstractmethod
    async def get_login_activity_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Get login activity report.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Login activity report with patterns and trends
        """
        pass
    
    @abstractmethod
    async def get_role_distribution_report(self) -> Dict[str, Any]:
        """
        Get role distribution report.
        
        Returns:
            Role distribution statistics and trends
        """
        pass
    
    @abstractmethod
    async def get_department_distribution_report(self) -> Dict[str, Any]:
        """
        Get department distribution report.
        
        Returns:
            Department distribution statistics and trends
        """
        pass
    
    @abstractmethod
    async def get_profile_completion_report(self) -> Dict[str, Any]:
        """
        Get profile completion report.
        
        Returns:
            Profile completion statistics and recommendations
        """
        pass
    
    @abstractmethod
    async def get_security_metrics_report(self) -> Dict[str, Any]:
        """
        Get security metrics report.
        
        Returns:
            Security metrics including password strength, login attempts, etc.
        """
        pass
    
    @abstractmethod
    async def get_user_growth_trends(self, months: int = 12) -> Dict[str, Any]:
        """
        Get user growth trends.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            User growth trends and projections
        """
        pass


class UserProfileService(ABC):
    """
    Service interface for user profile management.
    
    Handles profile completion tracking, document management,
    and profile-related operations.
    """
    
    @abstractmethod
    async def get_profile_completion(self, user_id: str) -> UserProfileCompletionDTO:
        """
        Get profile completion status for a user.
        
        Args:
            user_id: User ID
            
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
    async def upload_document(
        self, 
        user_id: str, 
        document_type: str,
        file_path: str,
        uploaded_by: str
    ) -> UserResponseDTO:
        """
        Upload user document.
        
        Args:
            user_id: User ID
            document_type: Type of document (photo, pan, aadhar)
            file_path: Path to uploaded file
            uploaded_by: User uploading the document
            
        Returns:
            Updated user response DTO
        """
        pass
    
    @abstractmethod
    async def delete_document(
        self, 
        user_id: str, 
        document_type: str,
        deleted_by: str
    ) -> UserResponseDTO:
        """
        Delete user document.
        
        Args:
            user_id: User ID
            document_type: Type of document to delete
            deleted_by: User deleting the document
            
        Returns:
            Updated user response DTO
        """
        pass
    
    @abstractmethod
    async def generate_profile_recommendations(self, user_id: str) -> List[str]:
        """
        Generate profile completion recommendations.
        
        Args:
            user_id: User ID
            
        Returns:
            List of recommendations for profile completion
        """
        pass


class UserBulkOperationsService(ABC):
    """
    Service interface for bulk user operations.
    
    Handles batch operations like bulk updates, imports, exports,
    and mass operations.
    """
    
    @abstractmethod
    async def bulk_update_users(
        self, 
        request: BulkUserUpdateDTO
    ) -> BulkUserUpdateResultDTO:
        """
        Bulk update multiple users.
        
        Args:
            request: Bulk update request DTO
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        user_ids: List[str], 
        status: str,
        reason: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> BulkUserUpdateResultDTO:
        """
        Bulk update user status.
        
        Args:
            user_ids: List of user IDs to update
            status: New status to set
            reason: Reason for status change
            updated_by: User performing the update
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_update_role(
        self, 
        user_ids: List[str], 
        role: str,
        reason: str,
        updated_by: str
    ) -> BulkUserUpdateResultDTO:
        """
        Bulk update user role.
        
        Args:
            user_ids: List of user IDs to update
            role: New role to set
            reason: Reason for role change
            updated_by: User performing the update
            
        Returns:
            Results of bulk update operation
        """
        pass
    
    @abstractmethod
    async def bulk_password_reset(
        self, 
        user_ids: List[str],
        reset_by: str,
        send_email: bool = True
    ) -> BulkUserUpdateResultDTO:
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
    
    @abstractmethod
    async def bulk_export_users(
        self, 
        user_ids: Optional[List[str]] = None,
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
    async def bulk_import_users(
        self, 
        data: bytes, 
        format: str = "csv",
        validate_only: bool = False,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk import user data.
        
        Args:
            data: Import data as bytes
            format: Import format (csv, xlsx, json)
            validate_only: Whether to only validate without importing
            created_by: User performing the import
            
        Returns:
            Results of bulk import operation
        """
        pass


class UserValidationService(ABC):
    """
    Service interface for user validation operations.
    
    Handles data validation, business rule validation,
    and constraint checking.
    """
    
    @abstractmethod
    async def validate_user_data(self, request: CreateUserRequestDTO) -> List[str]:
        """
        Validate user creation data.
        
        Args:
            request: User creation request DTO
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_user_update(
        self, 
        user_id: str, 
        request: UpdateUserRequestDTO
    ) -> List[str]:
        """
        Validate user update data.
        
        Args:
            user_id: User ID being updated
            request: User update request DTO
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_business_rules(self, user: User) -> List[str]:
        """
        Validate user business rules.
        
        Args:
            user: User entity to validate
            
        Returns:
            List of business rule violations (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_uniqueness_constraints(
        self, 
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None
    ) -> List[str]:
        """
        Validate uniqueness constraints.
        
        Args:
            email: Email to check
            mobile: Mobile number to check
            pan_number: PAN number to check
            exclude_id: User ID to exclude from check
            
        Returns:
            List of uniqueness violations (empty if valid)
        """
        pass
    
    @abstractmethod
    async def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Password strength analysis and recommendations
        """
        pass


class UserNotificationService(ABC):
    """
    Service interface for user notification operations.
    
    Handles sending notifications for user events and activities.
    """
    
    @abstractmethod
    async def send_user_created_notification(self, user: User) -> bool:
        """
        Send notification when user is created.
        
        Args:
            user: Created user entity
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_password_changed_notification(
        self, 
        user: User, 
        is_self_change: bool
    ) -> bool:
        """
        Send notification when password is changed.
        
        Args:
            user: User entity
            is_self_change: Whether user changed their own password
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_role_changed_notification(
        self, 
        user: User, 
        old_role: str, 
        new_role: str,
        reason: str
    ) -> bool:
        """
        Send notification when user role is changed.
        
        Args:
            user: User entity
            old_role: Previous role
            new_role: New role
            reason: Reason for change
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_status_change_notification(
        self, 
        user: User, 
        old_status: str, 
        new_status: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Send notification when user status changes.
        
        Args:
            user: User entity
            old_status: Previous status
            new_status: New status
            reason: Reason for change
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_login_alert_notification(
        self, 
        user: User, 
        login_details: Dict[str, Any]
    ) -> bool:
        """
        Send notification for suspicious login activity.
        
        Args:
            user: User entity
            login_details: Login details (IP, location, device, etc.)
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    async def send_profile_completion_reminder(self, user: User) -> bool:
        """
        Send reminder for profile completion.
        
        Args:
            user: User entity
            
        Returns:
            True if notification sent successfully
        """
        pass


class UserServiceFactory(ABC):
    """
    Factory interface for creating user service instances.
    
    Provides a centralized way to create different types of
    user services while maintaining loose coupling.
    """
    
    @abstractmethod
    def create_command_service(self) -> UserCommandService:
        """Create user command service instance"""
        pass
    
    @abstractmethod
    def create_query_service(self) -> UserQueryService:
        """Create user query service instance"""
        pass
    
    @abstractmethod
    def create_authentication_service(self) -> UserAuthenticationService:
        """Create user authentication service instance"""
        pass
    
    @abstractmethod
    def create_authorization_service(self) -> UserAuthorizationService:
        """Create user authorization service instance"""
        pass
    
    @abstractmethod
    def create_analytics_service(self) -> UserAnalyticsService:
        """Create user analytics service instance"""
        pass
    
    @abstractmethod
    def create_profile_service(self) -> UserProfileService:
        """Create user profile service instance"""
        pass
    
    @abstractmethod
    def create_bulk_operations_service(self) -> UserBulkOperationsService:
        """Create user bulk operations service instance"""
        pass
    
    @abstractmethod
    def create_validation_service(self) -> UserValidationService:
        """Create user validation service instance"""
        pass
    
    @abstractmethod
    def create_notification_service(self) -> UserNotificationService:
        """Create user notification service instance"""
        pass


class UserService(
    UserCommandService,
    UserQueryService,
    UserAuthenticationService,
    UserAuthorizationService,
    UserAnalyticsService,
    UserProfileService,
    UserBulkOperationsService,
    UserValidationService,
    UserNotificationService
):
    """
    Combined user service interface.
    
    Aggregates all user service interfaces for convenience
    when a single implementation handles all operations.
    """
    pass 