"""
User Service Implementation
SOLID-compliant implementation of all user service interfaces
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, timedelta

from app.application.interfaces.services.user_service import (
    UserCommandService, UserQueryService, UserAuthenticationService,
    UserAuthorizationService, UserAnalyticsService, UserProfileService,
    UserBulkOperationsService, UserValidationService, UserNotificationService,
    UserService
)
from app.application.interfaces.repositories.user_repository import UserRepository
from app.application.interfaces.repositories.company_leave_repository import CompanyLeaveQueryRepository
from app.application.interfaces.repositories.organisation_repository import (
    OrganisationQueryRepository, OrganisationCommandRepository
)
from app.application.use_cases.user.create_user_use_case import CreateUserUseCase
from app.application.use_cases.user.authenticate_user_use_case import AuthenticateUserUseCase
from app.application.use_cases.user.get_user_use_case import GetUserUseCase
from app.application.use_cases.user.delete_user_use_case import DeleteUserUseCase
from app.application.dto.user_dto import (
    CreateUserRequestDTO, UpdateUserRequestDTO, UpdateUserDocumentsRequestDTO,
    ChangeUserPasswordRequestDTO, ChangeUserRoleRequestDTO, UserStatusUpdateRequestDTO,
    UserSearchFiltersDTO, UserLoginRequestDTO, UserResponseDTO, UserSummaryDTO,
    UserListResponseDTO, UserStatisticsDTO, UserAnalyticsDTO, UserLoginResponseDTO,
    UserProfileCompletionDTO, BulkUserUpdateDTO, BulkUserUpdateResultDTO
)
from app.domain.entities.user import User
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_credentials import UserRole, UserStatus
from app.infrastructure.services.password_service import PasswordService
from app.infrastructure.services.notification_service import NotificationService
from app.infrastructure.services.file_upload_service import FileUploadService

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class UserServiceImpl(UserService):
    """
    Complete implementation of all user service interfaces.
    
    Follows SOLID principles:
    - SRP: Delegates to specific use cases and services
    - OCP: Extensible through dependency injection
    - LSP: Implements all interface contracts correctly
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        company_leave_query_repository: CompanyLeaveQueryRepository,
        organisation_query_repository: OrganisationQueryRepository,
        organisation_command_repository: OrganisationCommandRepository,
        password_service: PasswordService,
        notification_service: NotificationService,
        file_upload_service: FileUploadService
    ):
        """
        Initialize service with dependencies.
        
        Args:
            user_repository: User repository for data access
            company_leave_query_repository: Company leave repository for data access
            organisation_query_repository: Organisation repository for data access
            organisation_command_repository: Organisation command repository for data access
            password_service: Service for password operations
            notification_service: Service for sending notifications
            file_upload_service: Service for file operations
        """
        self.user_repository = user_repository
        self.company_leave_query_repository = company_leave_query_repository
        self.organisation_query_repository = organisation_query_repository
        self.organisation_command_repository = organisation_command_repository
        self.password_service = password_service
        self.notification_service = notification_service
        self.file_upload_service = file_upload_service
        
        # Initialize use cases
        self._create_user_use_case = CreateUserUseCase(
            command_repository=user_repository,
            query_repository=user_repository,
            validation_service=self,
            notification_service=self,
            company_leave_query_repository=company_leave_query_repository,
            organisation_query_repository=organisation_query_repository,
            organisation_command_repository=organisation_command_repository
        )
        self._authenticate_user_use_case = AuthenticateUserUseCase(
            command_repository=user_repository,
            query_repository=user_repository,
            notification_service=self
        )
        self._get_user_use_case = GetUserUseCase(
            query_repository=user_repository,
            authorization_service=self
        )
        self._delete_user_use_case = DeleteUserUseCase(
            command_repository=user_repository,
            query_repository=user_repository,
            organisation_query_repository=organisation_query_repository,
            organisation_command_repository=organisation_command_repository,
            notification_service=self
        )
    
    # Command Service Implementation
    async def create_user(self, request: CreateUserRequestDTO, current_user: "CurrentUser") -> UserResponseDTO:
        """Create a new user with organisation context from current_user."""
        try:
            logger.info(f"Creating user: {request.employee_id} in organisation: {current_user.hostname}")
            # Pass current_user to use case for organisation context
            return await self._create_user_use_case.execute(request, current_user)
        except Exception as e:
            logger.error(f"Error creating user {request.employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def update_user(
        self, 
        employee_id: str, 
        request: UpdateUserRequestDTO,
        current_user: "CurrentUser"
    ) -> UserResponseDTO:
        """Update an existing user with organisation context from current_user."""
        try:
            logger.info(f"Updating user: {employee_id} in organisation: {current_user.hostname}")
            
            # Get existing user (repository will handle organisation context via database service)
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            # Update user fields
            if request.name is not None:
                user.name = request.name
            if request.email is not None:
                user.email = request.email
            if request.mobile is not None:
                user.mobile = request.mobile
            if request.department is not None:
                user.department = request.department
            if request.designation is not None:
                user.designation = request.designation
            if request.location is not None:
                user.location = request.location
            if request.manager_id is not None:
                user.manager_id = EmployeeId(request.manager_id)
            
            # Update personal details if any personal fields are provided
            if any([request.gender, request.date_of_birth, request.date_of_joining, 
                   request.pan_number, request.aadhar_number, request.uan_number, request.esi_number]):
                
                # Create updated personal details
                from app.domain.value_objects.personal_details import PersonalDetails
                from app.domain.value_objects.user_credentials import Gender
                from datetime import datetime
                
                # Get current personal details or create new ones
                current_details = user.personal_details
                
                updated_personal_details = PersonalDetails(
                    gender=Gender(request.gender.lower()) if request.gender else current_details.gender,
                    date_of_birth=datetime.fromisoformat(request.date_of_birth).date() if request.date_of_birth else current_details.date_of_birth,
                    date_of_joining=datetime.fromisoformat(request.date_of_joining).date() if request.date_of_joining else current_details.date_of_joining,
                    mobile=request.mobile if request.mobile else current_details.mobile,
                    pan_number=request.pan_number if request.pan_number is not None else current_details.pan_number,
                    aadhar_number=request.aadhar_number if request.aadhar_number is not None else current_details.aadhar_number,
                    uan_number=request.uan_number if request.uan_number is not None else current_details.uan_number,
                    esi_number=request.esi_number if request.esi_number is not None else current_details.esi_number
                )
                
                # Update the user's personal details
                user.update_profile(
                    personal_details=updated_personal_details,
                    updated_by=request.updated_by
                )
            
            # Update banking details if any banking fields are provided
            if any([request.account_number, request.bank_name, request.ifsc_code, 
                   request.account_holder_name, request.branch_name, request.account_type]):
                
                from app.domain.value_objects.bank_details import BankDetails
                
                # Create updated bank details
                updated_bank_details = BankDetails(
                    account_number=request.account_number or '',
                    bank_name=request.bank_name or '',
                    ifsc_code=request.ifsc_code or '',
                    account_holder_name=request.account_holder_name or '',
                    branch_name=request.branch_name or '',
                    account_type=request.account_type or 'savings'
                )
                
                # Update the user's bank details
                user.update_bank_details(updated_bank_details, request.updated_by)
            
            # Save updated user
            updated_user = await self.user_repository.save(user, current_user.hostname)
            
            # Send notification
            await self.send_user_updated_notification(updated_user)
            
            return UserResponseDTO.from_entity(updated_user)
            
        except Exception as e:
            logger.error(f"Error updating user {employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def update_user_documents(
        self, 
        employee_id: str, 
        request: UpdateUserDocumentsRequestDTO,
        current_user: "CurrentUser"
    ) -> UserResponseDTO:
        """Update user documents."""
        try:
            logger.info(f"Updating documents for user: {employee_id}")
            
            # Get existing user
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            # Update document paths
            if request.photo_path:
                user.update_photo_path(request.photo_path)
            if request.pan_document_path:
                user.update_pan_document_path(request.pan_document_path)
            if request.aadhar_document_path:
                user.update_aadhar_document_path(request.aadhar_document_path)
            
            # Save updated user
            updated_user = await self.user_repository.save(user, current_user.hostname)
            
            return UserResponseDTO.from_entity(updated_user)
            
        except Exception as e:
            logger.error(f"Error updating documents for user {employee_id}: {e}")
            raise
    
    async def change_user_password(
        self, 
        employee_id: str, 
        request: ChangeUserPasswordRequestDTO,
        current_user: "CurrentUser"
    ) -> UserResponseDTO:
        """Change user password."""
        try:
            logger.info(f"Changing password for user: {employee_id} in organisation: {current_user.hostname}")
            
            # Get existing user
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            # Verify current password if provided
            if request.current_password:
                if not self.password_service.verify_password(
                    request.current_password, 
                    user.credentials.password_hash
                ):
                    raise ValueError("Current password is incorrect")
            
            # Hash new password
            new_password_hash = self.password_service.hash_password(request.new_password)
            
            # Update password
            user.change_password(new_password_hash, request.changed_by)
            
            # Save updated user
            updated_user = await self.user_repository.save(user, current_user.hostname)
            
            # Send notification
            is_self_change = request.changed_by == employee_id
            await self.send_password_changed_notification(updated_user, is_self_change)
            
            return UserResponseDTO.from_entity(updated_user)
            
        except Exception as e:
            logger.error(f"Error changing password for user {employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def change_user_role(
        self, 
        employee_id: str, 
        request: ChangeUserRoleRequestDTO,
        current_user: "CurrentUser"
    ) -> UserResponseDTO:
        """Change user role."""
        try:
            logger.info(f"Changing role for user: {employee_id} in organisation: {current_user.hostname}")
            
            # Get existing user
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            old_role = user.credentials.role.value
            
            # Update role
            user.change_role(UserRole(request.new_role.lower()), request.changed_by, request.reason)
            
            # Save updated user
            updated_user = await self.user_repository.save(user, current_user.hostname)
            
            # Send notification
            await self.send_role_changed_notification(
                updated_user, old_role, request.new_role, request.reason
            )
            
            return UserResponseDTO.from_entity(updated_user)
            
        except Exception as e:
            logger.error(f"Error changing role for user {employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def update_user_status(
        self, 
        employee_id: str, 
        request: UserStatusUpdateRequestDTO,
        current_user: "CurrentUser"
    ) -> UserResponseDTO:
        """Update user status with organisation context from current_user."""
        try:
            logger.info(f"Updating status for user: {employee_id} in organisation: {current_user.hostname}")
            
            # Get existing user
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            old_status = user.credentials.status.value
            
            # Update status
            user.update_status(UserStatus(request.new_status.lower()), request.updated_by, request.reason)
            
            # Save updated user
            updated_user = await self.user_repository.save(user, current_user.hostname)
            
            # Send notification
            await self.send_status_change_notification(
                updated_user, old_status, request.new_status, request.reason
            )
            
            return UserResponseDTO.from_entity(updated_user)
            
        except Exception as e:
            logger.error(f"Error updating status for user {employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def assign_manager(
        self, 
        employee_id: str, 
        manager_id: str,
        assigned_by: str
    ) -> UserResponseDTO:
        """Assign manager to user."""
        try:
            logger.info(f"Assigning manager {manager_id} to user: {employee_id}")
            
            # Get existing user
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            # Verify manager exists
            manager = await self.user_repository.get_by_id(EmployeeId(manager_id), current_user.hostname)
            if not manager:
                raise ValueError(f"Manager not found: {manager_id}")
            
            # Assign manager
            user.assign_manager(EmployeeId(manager_id))
            user.update_updated_by(assigned_by)
            
            # Save updated user
            updated_user = await self.user_repository.save(user, current_user.hostname)
            
            return UserResponseDTO.from_entity(updated_user)
            
        except Exception as e:
            logger.error(f"Error assigning manager to user {employee_id}: {e}")
            raise
    
    async def delete_user(
        self, 
        employee_id: str, 
        deletion_reason: str,
        current_user: "CurrentUser",
        deleted_by: Optional[str] = None,
        soft_delete: bool = True
    ) -> bool:
        """Delete a user with organisation context from current_user."""
        try:
            logger.info(f"Deleting user: {employee_id} (soft: {soft_delete})")
            
            # Use the delete user use case
            result = await self._delete_user_use_case.execute(
                employee_id=employee_id,
                deletion_reason=deletion_reason,
                current_user=current_user,
                deleted_by=deleted_by or current_user.employee_id,
                soft_delete=soft_delete
            )
            
            if result:
                logger.info(f"User deleted successfully: {employee_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting user {employee_id}: {e}")
            raise
    
    # Query Service Implementation
    async def get_user_by_id(self, employee_id: str, current_user: "CurrentUser") -> Optional[UserResponseDTO]:
        """Get user by ID with organisation context from current_user."""
        try:
            logger.info(f"Getting user {employee_id} from organisation {current_user.hostname}")
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            return UserResponseDTO.from_entity(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by ID {employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_user_by_email(self, email: str, current_user: "CurrentUser") -> Optional[UserResponseDTO]:
        """Get user by email."""
        try:
            logger.info(f"Getting user by email {email} from organisation {current_user.hostname}")
            user = await self.user_repository.get_by_email(email, current_user.hostname)
            return UserResponseDTO.from_entity(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by email {email} in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_user_by_mobile(self, mobile: str, current_user: "CurrentUser") -> Optional[UserResponseDTO]:
        """Get user by mobile."""
        try:
            logger.info(f"Getting user by mobile {mobile} from organisation {current_user.hostname}")
            user = await self.user_repository.get_by_mobile(mobile, current_user.hostname)
            return UserResponseDTO.from_entity(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by mobile {mobile} in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_all_users(
        self, 
        skip: int = 0, 
        limit: int = 20,
        include_inactive: bool = False,
        include_deleted: bool = False,
        current_user: "CurrentUser" = None
    ) -> UserListResponseDTO:
        """Get all users with pagination and organisation context from current_user."""
        try:
            logger.info(f"Getting all users from organisation {current_user.hostname if current_user else 'global'}")
            users = await self.user_repository.get_all(
                skip=skip, 
                limit=limit,
                include_inactive=include_inactive,
                include_deleted=include_deleted,
                organisation_id=current_user.hostname if current_user else None
            )
            
            total_count = await self.user_repository.count_total(
                include_deleted=include_deleted,
                organisation_id=current_user.hostname if current_user else None
            )
            
            user_summaries = [UserSummaryDTO.from_entity(user) for user in users]
            
            # Calculate pagination info
            page = (skip // limit) + 1 if limit > 0 else 1
            total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
            has_next = skip + limit < total_count
            has_previous = skip > 0
            
            return UserListResponseDTO(
                users=user_summaries,
                total_count=total_count,
                page=page,
                page_size=limit,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as e:
            logger.error(f"Error getting all users in organisation {current_user.hostname if current_user else 'unknown'}: {e}")
            raise
    
    async def search_users(self, filters: UserSearchFiltersDTO, current_user: "CurrentUser") -> UserListResponseDTO:
        """Search users with filters."""
        try:
            logger.info(f"Searching users in organisation {current_user.hostname}")
            users = await self.user_repository.search(filters, current_user.hostname)
            user_summaries = [UserSummaryDTO.from_entity(user) for user in users]
            
            # Calculate pagination info
            total_count = len(user_summaries)  # TODO: Implement proper count
            has_next = filters.page * filters.page_size < total_count
            has_previous = filters.page > 1
            total_pages = (total_count + filters.page_size - 1) // filters.page_size if filters.page_size > 0 else 1
            
            return UserListResponseDTO(
                users=user_summaries,
                total_count=total_count,
                page=filters.page,
                page_size=filters.page_size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as e:
            logger.error(f"Error searching users in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_users_by_role(self, role: str, current_user: "CurrentUser") -> List[UserSummaryDTO]:
        """Get users by role."""
        try:
            users = await self.user_repository.get_by_role(UserRole(role.lower()), current_user.hostname)
            return [UserSummaryDTO.from_entity(user) for user in users]
        except Exception as e:
            logger.error(f"Error getting users by role {role}: {e}")
            raise
    
    async def get_users_by_status(self, status: str, current_user: "CurrentUser") -> List[UserSummaryDTO]:
        """Get users by status."""
        try:
            users = await self.user_repository.get_by_status(UserStatus(status.lower()), current_user.hostname)
            return [UserSummaryDTO.from_entity(user) for user in users]
        except Exception as e:
            logger.error(f"Error getting users by status {status}: {e}")
            raise
    
    async def get_users_by_department(self, department: str, current_user: "CurrentUser") -> List[UserSummaryDTO]:
        """Get users by department."""
        try:
            users = await self.user_repository.get_by_department(department, current_user.hostname)
            return [UserSummaryDTO.from_entity(user) for user in users]
        except Exception as e:
            logger.error(f"Error getting users by department {department}: {e}")
            raise
    
    async def get_users_by_manager(
        self, 
        manager_id: str, 
        current_user: "CurrentUser",
        skip: int = 0,
        limit: int = 20,
        include_inactive: bool = False,
        include_deleted: bool = False
    ) -> UserListResponseDTO:
        """Get users by manager with pagination."""
        try:
            logger.info(f"Getting users by manager {manager_id} in organisation {current_user.hostname}")
            
            # Get users by manager
            users = await self.user_repository.get_by_manager(EmployeeId(manager_id), current_user.hostname)
            
            # Apply filters
            filtered_users = []
            for user in users:
                # Apply status filters
                if not include_inactive and user.status != UserStatus.ACTIVE:
                    continue
                if not include_deleted and getattr(user, 'is_deleted', False):
                    continue
                filtered_users.append(user)
            
            # Apply pagination
            total_count = len(filtered_users)
            paginated_users = filtered_users[skip:skip + limit]
            
            # Convert to DTOs
            user_summaries = [UserSummaryDTO.from_entity(user) for user in paginated_users]
            
            # Calculate pagination info
            page = (skip // limit) + 1 if limit > 0 else 1
            total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
            has_next = skip + limit < total_count
            has_previous = skip > 0
            
            return UserListResponseDTO(
                users=user_summaries,
                total_count=total_count,
                page=page,
                page_size=limit,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as e:
            logger.error(f"Error getting users by manager {manager_id}: {e}")
            raise
    
    async def get_users_by_manager_simple(
        self, 
        manager_id: str, 
        current_user: "CurrentUser"
    ) -> List[UserResponseDTO]:
        """Get users by manager (simple version matching interface)."""
        try:
            logger.info(f"Getting users by manager {manager_id} in organisation {current_user.hostname}")
            
            # Get users by manager
            users = await self.user_repository.get_by_manager(EmployeeId(manager_id), current_user.hostname)
            
            # Convert to response DTOs
            return [UserResponseDTO.from_entity(user) for user in users]
            
        except Exception as e:
            logger.error(f"Error getting users by manager {manager_id}: {e}")
            raise
    
    async def check_user_exists(
        self, 
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> Dict[str, bool]:
        """Check if user exists by various identifiers."""
        try:
            organisation_context = f" in organisation {current_user.hostname}" if current_user else ""
            logger.info(f"Checking user existence{organisation_context}")
            
            result = {}
            exclude_employee_id = EmployeeId(exclude_id) if exclude_id else None
            organisation_id = current_user.hostname if current_user else None
            
            if email:
                result["email"] = await self.user_repository.exists_by_email(
                    email, exclude_employee_id, organisation_id
                )
            
            if mobile:
                result["mobile"] = await self.user_repository.exists_by_mobile(
                    mobile, exclude_employee_id, organisation_id
                )
            
            if pan_number:
                result["pan_number"] = await self.user_repository.exists_by_pan_number(
                    pan_number, exclude_employee_id, organisation_id
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking user existence in organisation {current_user.hostname if current_user else 'unknown'}: {e}")
            raise
    
    # Authentication Service Implementation
    async def authenticate_user(self, request: UserLoginRequestDTO) -> UserLoginResponseDTO:
        """Authenticate user with credentials."""
        try:
            logger.info(f"Authenticating user: {request.username}")
            return await self._authenticate_user_use_case.execute(request)
        except Exception as e:
            logger.error(f"Error authenticating user {request.username}: {e}")
            raise
    
    async def logout_user(
        self, 
        employee_id: str, 
        session_token: str,
        logout_method: str = "manual"
    ) -> bool:
        """Logout user and invalidate session."""
        try:
            logger.info(f"Logging out user: {employee_id}")
            # TODO: Implement session management
            return True
        except Exception as e:
            logger.error(f"Error logging out user {employee_id}: {e}")
            raise
    
    async def refresh_token(self, refresh_token: str) -> UserLoginResponseDTO:
        """Refresh access token."""
        try:
            # TODO: Implement token refresh logic
            raise NotImplementedError("Token refresh not implemented yet")
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
    
    async def reset_password(
        self, 
        employee_id: str, 
        reset_by: str,
        current_user: "CurrentUser",
        send_email: bool = True
    ) -> str:
        """Reset user password."""
        try:
            logger.info(f"Resetting password for user: {employee_id}")
            
            # Get user
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            # Generate temporary password
            temp_password = self.password_service.generate_temporary_password()
            temp_password_hash = self.password_service.hash_password(temp_password)
            
            # Update user password
            user.change_password(temp_password_hash, reset_by)
            await self.user_repository.save(user, current_user.hostname)
            
            # Send email if requested
            if send_email:
                await self.notification_service.send_password_reset_email(
                    user.email.value, temp_password
                )
            
            return temp_password
            
        except Exception as e:
            logger.error(f"Error resetting password for user {employee_id}: {e}")
            raise
    
    async def validate_session(self, session_token: str) -> Optional[UserResponseDTO]:
        """Validate session token."""
        try:
            # TODO: Implement session validation
            return None
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            raise
    
    async def get_active_sessions(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get active sessions for user."""
        try:
            # TODO: Implement session management
            return []
        except Exception as e:
            logger.error(f"Error getting active sessions for user {employee_id}: {e}")
            raise
    
    async def terminate_all_sessions(self, employee_id: str, terminated_by: str) -> int:
        """Terminate all sessions for user."""
        try:
            # TODO: Implement session termination
            return 0
        except Exception as e:
            logger.error(f"Error terminating sessions for user {employee_id}: {e}")
            raise
    
    # Authorization Service Implementation
    async def check_permission(self, employee_id: str, permission: str, current_user: "CurrentUser") -> bool:
        """Check if user has permission."""
        try:
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                return False
            
            # Check role-based permissions
            role_permissions = self._get_role_permissions(user.credentials.role)
            if permission in role_permissions:
                return True
            
            # Check custom permissions
            return permission in user.custom_permissions
            
        except Exception as e:
            logger.error(f"Error checking permission {permission} for user {employee_id}: {e}")
            return False
    
    async def check_resource_permission(
        self, 
        employee_id: str, 
        resource: str, 
        action: str
    ) -> bool:
        """Check resource-specific permission."""
        try:
            permission = f"{resource}:{action}"
            return await self.check_permission(employee_id, permission, current_user)
        except Exception as e:
            logger.error(f"Error checking resource permission for user {employee_id}: {e}")
            return False
    
    async def get_user_permissions(self, employee_id: str, current_user: "CurrentUser") -> List[str]:
        """Get all permissions for user."""
        try:
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                return []
            
            # Get role permissions
            role_permissions = self._get_role_permissions(user.credentials.role)
            
            # Combine with custom permissions
            all_permissions = set(role_permissions + user.custom_permissions)
            return list(all_permissions)
            
        except Exception as e:
            logger.error(f"Error getting permissions for user {employee_id}: {e}")
            return []
    
    def _get_role_permissions(self, role: UserRole) -> List[str]:
        """Get permissions for a role."""
        role_permissions = {
            UserRole.SUPERADMIN: [
                "user:create", "user:read", "user:update", "user:delete",
                "organisation:create", "organisation:read", "organisation:update", "organisation:delete",
                "system:admin"
            ],
            UserRole.ADMIN: [
                "user:create", "user:read", "user:update",
                "organisation:read", "organisation:update"
            ],
            UserRole.MANAGER: [
                "user:read", "employee:read", "team:manage"
            ],
            UserRole.USER: [
                "user:read_own", "profile:update_own"
            ]
        }
        return role_permissions.get(role, [])
    
    async def add_custom_permission(
        self, 
        employee_id: str, 
        permission: str,
        granted_by: str,
        current_user: "CurrentUser"
    ) -> UserResponseDTO:
        """Add custom permission to user."""
        try:
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            user.add_custom_permission(permission)
            user.update_updated_by(granted_by)
            
            updated_user = await self.user_repository.save(user, current_user.hostname)
            return UserResponseDTO.from_entity(updated_user)
            
        except Exception as e:
            logger.error(f"Error adding permission {permission} to user {employee_id}: {e}")
            raise
    
    async def remove_custom_permission(
        self, 
        employee_id: str, 
        permission: str,
        removed_by: str,
        current_user: "CurrentUser"
    ) -> UserResponseDTO:
        """Remove custom permission from user."""
        try:
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            user.remove_custom_permission(permission)
            user.update_updated_by(removed_by)
            
            updated_user = await self.user_repository.save(user, current_user.hostname)
            return UserResponseDTO.from_entity(updated_user)
            
        except Exception as e:
            logger.error(f"Error removing permission {permission} from user {employee_id}: {e}")
            raise
    
    async def can_access_user_data(
        self, 
        requesting_employee_id: str, 
        target_employee_id: str,
        current_user: "CurrentUser"
    ) -> bool:
        """Check if user can access another user's data."""
        try:
            # Same user can always access own data
            if requesting_employee_id == target_employee_id:
                return True
            
            # Check if requesting user has admin permissions
            if await self.check_permission(requesting_employee_id, "user:read", current_user):
                return True
            
            # Check if requesting user is manager of target user
            target_user = await self.user_repository.get_by_id(EmployeeId(target_employee_id), current_user.hostname)
            if target_user and target_user.manager_id:
                if str(target_user.manager_id) == requesting_employee_id:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking data access for users {requesting_employee_id}, {target_employee_id}: {e}")
            return False
    
    # Analytics Service Implementation
    async def get_user_statistics(self, current_user: "CurrentUser") -> UserStatisticsDTO:
        """Get user statistics."""
        try:
            logger.info(f"Getting user statistics for organisation {current_user.hostname}")
            organisation_id = current_user.hostname if current_user else None
            return await self.user_repository.get_statistics(organisation_id)
        except Exception as e:
            logger.error(f"Error getting user statistics for organisation {current_user.hostname}: {e}")
            raise
    
    async def get_user_analytics(self) -> UserAnalyticsDTO:
        """Get user analytics."""
        try:
            return await self.user_repository.get_analytics()
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            raise
    
    # Notification Service Implementation
    async def send_user_created_notification(self, user: User) -> bool:
        """Send user created notification."""
        try:
            return await self.notification_service.send_user_created_notification(user)
        except Exception as e:
            logger.error(f"Error sending user created notification: {e}")
            return False
    
    async def send_user_updated_notification(self, user: User) -> bool:
        """Send user updated notification."""
        try:
            return await self.notification_service.send_user_updated_notification(user)
        except Exception as e:
            logger.error(f"Error sending user updated notification: {e}")
            return False
    
    async def send_password_changed_notification(
        self, 
        user: User, 
        is_self_change: bool
    ) -> bool:
        """Send password changed notification."""
        try:
            return await self.notification_service.send_password_changed_notification(
                user, is_self_change
            )
        except Exception as e:
            logger.error(f"Error sending password changed notification: {e}")
            return False
    
    async def send_role_changed_notification(
        self, 
        user: User, 
        old_role: str, 
        new_role: str,
        reason: str
    ) -> bool:
        """Send role changed notification."""
        try:
            return await self.notification_service.send_role_changed_notification(
                user, old_role, new_role, reason
            )
        except Exception as e:
            logger.error(f"Error sending role changed notification: {e}")
            return False
    
    async def send_status_change_notification(
        self, 
        user: User, 
        old_status: str, 
        new_status: str,
        reason: Optional[str] = None
    ) -> bool:
        """Send status change notification."""
        try:
            return await self.notification_service.send_status_change_notification(
                user, old_status, new_status, reason
            )
        except Exception as e:
            logger.error(f"Error sending status change notification: {e}")
            return False
    
    async def send_login_alert_notification(
        self, 
        user: User, 
        login_details: Dict[str, Any]
    ) -> bool:
        """Send login alert notification."""
        try:
            return await self.notification_service.send_login_alert_notification(
                user, login_details
            )
        except Exception as e:
            logger.error(f"Error sending login alert notification: {e}")
            return False
    
    async def send_profile_completion_reminder(self, user: User) -> bool:
        """Send profile completion reminder notification."""
        try:
            await self.notification_service.send_notification(
                employee_id=str(user.employee_id),
                title="Complete Your Profile",
                message=f"Your profile is {user.profile_completion_percentage}% complete. Please update missing information.",
                notification_type="reminder"
            )
            return True
        except Exception as e:
            logger.error(f"Error sending profile completion reminder: {e}")
            return False
    
    # Additional service methods would be implemented here...
    # Profile Service, Bulk Operations Service, Validation Service implementations
    # Following the same pattern of delegating to appropriate services/repositories 

    # Missing Analytics Service Methods
    async def get_login_activity_report(self, days: int = 30) -> Dict[str, Any]:
        """Get login activity report."""
        try:
            return await self.user_repository.get_login_activity_stats(days)
        except Exception as e:
            logger.error(f"Error getting login activity report: {e}")
            return {}

    async def get_role_distribution_report(self) -> Dict[str, Any]:
        """Get role distribution report."""
        try:
            return await self.user_repository.get_users_by_role_count()
        except Exception as e:
            logger.error(f"Error getting role distribution report: {e}")
            return {}

    async def get_department_distribution_report(self) -> Dict[str, Any]:
        """Get department distribution report."""
        try:
            return await self.user_repository.get_users_by_department_count()
        except Exception as e:
            logger.error(f"Error getting department distribution report: {e}")
            return {}

    async def get_profile_completion_report(self) -> Dict[str, Any]:
        """Get profile completion report."""
        try:
            return await self.user_repository.get_profile_completion_stats()
        except Exception as e:
            logger.error(f"Error getting profile completion report: {e}")
            return {}

    async def get_security_metrics_report(self) -> Dict[str, Any]:
        """Get security metrics report."""
        try:
            return await self.user_repository.get_password_security_metrics()
        except Exception as e:
            logger.error(f"Error getting security metrics report: {e}")
            return {}

    async def get_user_growth_trends(self, months: int = 12) -> Dict[str, Any]:
        """Get user growth trends."""
        try:
            # Calculate growth over specified months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            users_in_period = await self.user_repository.get_users_created_in_period(start_date, end_date)
            
            # Group by month
            monthly_growth = {}
            for user in users_in_period:
                if user.created_at:
                    month_key = user.created_at.strftime("%Y-%m")
                    monthly_growth[month_key] = monthly_growth.get(month_key, 0) + 1
            
            return {
                "period_months": months,
                "total_new_users": len(users_in_period),
                "monthly_breakdown": monthly_growth,
                "average_monthly_growth": len(users_in_period) / months if months > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting user growth trends: {e}")
            return {}

    # Missing Profile Service Methods
    async def get_profile_completion(self, employee_id: str, current_user: "CurrentUser") -> UserProfileCompletionDTO:
        """Get profile completion for a user."""
        try:
            return await self.user_repository.get_profile_completion(EmployeeId(employee_id), current_user.hostname)
        except Exception as e:
            logger.error(f"Error getting profile completion for {employee_id}: {e}")
            return UserProfileCompletionDTO(
                employee_id=EmployeeId(employee_id),
                completion_percentage=0.0,
                missing_fields=[],
                completed_fields=[]
            )

    async def get_incomplete_profiles(self, current_user: "CurrentUser", threshold: float = 80.0) -> List[UserProfileCompletionDTO]:
        """Get users with incomplete profiles."""
        try:
            return await self.user_repository.get_incomplete_profiles(threshold, current_user.hostname)
        except Exception as e:
            logger.error(f"Error getting incomplete profiles: {e}")
            return []

    async def upload_document(
        self, 
        employee_id: str, 
        document_type: str,
        file_data: bytes,
        filename: str,
        uploaded_by: str,
        current_user: "CurrentUser"
    ) -> str:
        """Upload a document for a user."""
        try:
            # Use file upload service to store the document
            file_path = await self.file_upload_service.upload_file(
                file_data=file_data,
                filename=filename,
                directory=f"users/{employee_id}/{document_type}"
            )
            
            # Update user with document path
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            # Update appropriate document path based on type
            if document_type == "photo":
                user.update_photo_path(file_path)
            elif document_type == "pan":
                user.update_pan_document_path(file_path)
            elif document_type == "aadhar":
                user.update_aadhar_document_path(file_path)
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            # Save updated user
            await self.user_repository.save(user, current_user.hostname)
            
            logger.info(f"Document uploaded for user {employee_id}: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error uploading document for user {employee_id}: {e}")
            raise

    async def delete_document(
        self, 
        employee_id: str, 
        document_type: str,
        deleted_by: str,
        current_user: "CurrentUser"
    ) -> bool:
        """Delete a document for a user."""
        try:
            # Get user
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {employee_id}")
            
            # Get current document path
            file_path = None
            if document_type == "photo":
                file_path = user.photo_path
                user.update_photo_path(None)
            elif document_type == "pan":
                file_path = user.pan_document_path
                user.update_pan_document_path(None)
            elif document_type == "aadhar":
                file_path = user.aadhar_document_path
                user.update_aadhar_document_path(None)
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            # Delete file if it exists
            if file_path:
                await self.file_upload_service.delete_file(file_path)
            
            # Save updated user
            await self.user_repository.save(user, current_user.hostname)
            
            logger.info(f"Document deleted for user {employee_id}: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document for user {employee_id}: {e}")
            return False

    async def generate_profile_recommendations(self, employee_id: str) -> List[str]:
        """Generate profile improvement recommendations."""
        try:
            completion = await self.get_profile_completion(employee_id)
            recommendations = []
            
            # Generate recommendations based on missing fields
            for field in completion.missing_fields:
                if field == "mobile":
                    recommendations.append("Add your mobile number for better communication")
                elif field == "department":
                    recommendations.append("Update your department information")
                elif field == "designation":
                    recommendations.append("Add your job designation")
                elif field == "photo":
                    recommendations.append("Upload a profile photo")
                elif field == "pan_number":
                    recommendations.append("Add your PAN number for tax calculations")
                elif field == "aadhar_number":
                    recommendations.append("Add your Aadhar number for identity verification")
                elif field == "account_number":
                    recommendations.append("Add bank account details for salary processing")
            
            # Add general recommendations
            if completion.completion_percentage < 50:
                recommendations.append("Complete your basic profile information")
            elif completion.completion_percentage < 80:
                recommendations.append("Add remaining details to complete your profile")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating profile recommendations for {employee_id}: {e}")
            return []

    # Missing Bulk Operations Service Methods
    async def bulk_update_users(
        self, 
        updates: List[BulkUserUpdateDTO],
        updated_by: str
    ) -> BulkUserUpdateResultDTO:
        """Bulk update multiple users."""
        try:
            results = []
            successful_updates = 0
            failed_updates = 0
            
            for update in updates:
                try:
                    # Create update request
                    request = UpdateUserRequestDTO(
                        name=update.name,
                        email=update.email,
                        mobile=update.mobile,
                        department=update.department,
                        designation=update.designation,
                        location=update.location,
                        manager_id=update.manager_id,
                        updated_by=updated_by
                    )
                    
                    # Update user
                    result = await self.update_user(update.employee_id, request)
                    results.append({
                        "employee_id": update.employee_id,
                        "status": "success",
                        "result": result
                    })
                    successful_updates += 1
                    
                except Exception as e:
                    results.append({
                        "employee_id": update.employee_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed_updates += 1
            
            return BulkUserUpdateResultDTO(
                total_requested=len(updates),
                successful_updates=successful_updates,
                failed_updates=failed_updates,
                results=results
            )
            
        except Exception as e:
            logger.error(f"Error in bulk user update: {e}")
            raise

    async def bulk_update_status(
        self, 
        employee_ids: List[str], 
        status: str,
        reason: Optional[str],
        updated_by: str
    ) -> Dict[str, Any]:
        """Bulk update user status."""
        try:
            employee_ids = [EmployeeId(uid) for uid in employee_ids]
            user_status = UserStatus(status.lower())
            
            return await self.user_repository.bulk_update_status(
                employee_ids, user_status, updated_by, reason
            )
        except Exception as e:
            logger.error(f"Error in bulk status update: {e}")
            return {"error": str(e), "status": "failed"}

    async def bulk_update_role(
        self, 
        employee_ids: List[str], 
        role: str,
        reason: str,
        updated_by: str
    ) -> Dict[str, Any]:
        """Bulk update user role."""
        try:
            employee_ids = [EmployeeId(uid) for uid in employee_ids]
            user_role = UserRole(role.lower())
            
            return await self.user_repository.bulk_update_role(
                employee_ids, user_role, updated_by, reason
            )
        except Exception as e:
            logger.error(f"Error in bulk role update: {e}")
            return {"error": str(e), "status": "failed"}

    async def bulk_password_reset(
        self, 
        employee_ids: List[str],
        reset_by: str,
        send_email: bool = True
    ) -> Dict[str, Any]:
        """Bulk password reset for users."""
        try:
            employee_ids = [EmployeeId(uid) for uid in employee_ids]
            
            return await self.user_repository.bulk_password_reset(
                employee_ids, reset_by, send_email
            )
        except Exception as e:
            logger.error(f"Error in bulk password reset: {e}")
            return {"error": str(e), "status": "failed"}

    async def bulk_export_users(
        self, 
        employee_ids: Optional[List[str]] = None,
        format: str = "csv",
        include_sensitive: bool = False
    ) -> bytes:
        """Bulk export user data."""
        try:
            employee_ids = [EmployeeId(uid) for uid in employee_ids] if employee_ids else None
            
            return await self.user_repository.bulk_export(
                employee_ids, format, include_sensitive
            )
        except Exception as e:
            logger.error(f"Error in bulk export: {e}")
            return b""

    async def bulk_import_users(
        self, 
        data: bytes, 
        format: str = "csv",
        created_by: str = "system",
        validate_only: bool = False
    ) -> Dict[str, Any]:
        """Bulk import user data."""
        try:
            return await self.user_repository.bulk_import(
                data, format, created_by, validate_only
            )
        except Exception as e:
            logger.error(f"Error in bulk import: {e}")
            return {"error": str(e), "status": "failed"}

    # Missing Validation Service Methods
    async def validate_user_data(self, request: CreateUserRequestDTO) -> List[str]:
        """Validate user data for creation."""
        try:
            errors = []
            
            # Validate required fields
            if not request.employee_id or not request.employee_id.strip():
                errors.append("Employee ID is required")
            
            if not request.name or not request.name.strip():
                errors.append("Name is required")
            
            if not request.email or not request.email.strip():
                errors.append("Email is required")
            
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if request.email and not re.match(email_pattern, request.email):
                errors.append("Invalid email format")
            
            # Validate mobile format (Indian mobile numbers)
            if request.mobile:
                # Allow Indian mobile formats: 10 digits, with optional +91 prefix or leading 0
                mobile_pattern = r'^(\+91[6-9]\d{9}|[6-9]\d{9}|0[6-9]\d{9}|\d{10})$'
                if not re.match(mobile_pattern, request.mobile):
                    errors.append("Invalid mobile number format (should be 10 digits)")
            
            # Validate PAN format
            if request.pan_number:
                pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
                if not re.match(pan_pattern, request.pan_number):
                    errors.append("Invalid PAN number format")
            
            # Validate Aadhar format
            if request.aadhar_number:
                aadhar_pattern = r'^\d{12}$'
                if not re.match(aadhar_pattern, request.aadhar_number):
                    errors.append("Invalid Aadhar number format (should be 12 digits)")
            
            return errors
            
        except Exception as e:
            logger.error(f"Error validating user data: {e}")
            return [f"Validation error: {str(e)}"]

    async def validate_user_update(
        self, 
        employee_id: str, 
        request: UpdateUserRequestDTO,
        current_user: "CurrentUser"
    ) -> List[str]:
        """Validate user data for update."""
        try:
            errors = []
            
            # Check if user exists
            user = await self.user_repository.get_by_id(EmployeeId(employee_id), current_user.hostname)
            if not user:
                errors.append(f"User not found: {employee_id}")
                return errors
            
            # Validate email format if provided
            if request.email:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, request.email):
                    errors.append("Invalid email format")
                
                # Check email uniqueness
                existing_user = await self.user_repository.get_by_email(request.email, current_user.hostname)
                if existing_user and str(getattr(existing_user, 'employee_id', getattr(existing_user, 'employee_id', ''))) != str(getattr(user, 'employee_id', getattr(user, 'employee_id', ''))):
                    errors.append("Email already in use by another user")
            
            # Validate mobile format if provided (Indian mobile numbers)
            if request.mobile:
                import re
                # Allow Indian mobile formats: 10 digits, with optional +91 prefix or leading 0
                mobile_pattern = r'^(\+91[6-9]\d{9}|[6-9]\d{9}|0[6-9]\d{9}|\d{10})$'
                if not re.match(mobile_pattern, request.mobile):
                    errors.append("Invalid mobile number format (should be 10 digits)")
                
                # Check mobile uniqueness
                existing_user = await self.user_repository.get_by_mobile(request.mobile, current_user.hostname)
                if existing_user and str(getattr(existing_user, 'employee_id', getattr(existing_user, 'employee_id', ''))) != str(getattr(user, 'employee_id', getattr(user, 'employee_id', ''))):
                    errors.append("Mobile number already in use by another user")
            
            # Validate manager exists if provided
            if request.manager_id:
                manager = await self.user_repository.get_by_id(EmployeeId(request.manager_id), current_user.hostname)
                if not manager:
                    errors.append(f"Manager not found: {request.manager_id}")
                elif request.manager_id == employee_id:
                    errors.append("User cannot be their own manager")
            
            return errors
            
        except Exception as e:
            logger.error(f"Error validating user update: {e}")
            return [f"Validation error: {str(e)}"]

    async def validate_business_rules(self, user: User) -> List[str]:
        """Validate business rules for user."""
        try:
            errors = []
            
            # Check if user is trying to be their own manager
            if user.manager_id and user.manager_id == user.employee_id:
                errors.append("User cannot be their own manager")
            
            # Check if user has required permissions for their role
            if hasattr(user, 'permissions') and hasattr(user.permissions, 'role'):
                role = user.permissions.role
                if hasattr(role, 'value'):
                    role_value = role.value
                elif hasattr(role, 'name'):
                    role_value = role.name
                else:
                    role_value = str(role)
                
                if role_value.upper() == "ADMIN":
                    # Admins should have specific permissions
                    pass
                elif role_value.upper() == "MANAGER":
                    # Managers should have team management permissions
                    pass
            
            # Check profile completion for active users
            if hasattr(user, 'is_active') and callable(user.is_active) and user.is_active():
                if hasattr(user, 'get_profile_completion_percentage'):
                    completion = user.get_profile_completion_percentage()
                    if completion < 50:
                        errors.append("Active users must have at least 50% profile completion")
            
            # Check required documents for employees (simplified validation)
            if hasattr(user, 'personal_details') and hasattr(user.personal_details, 'pan_number'):
                if not user.personal_details.pan_number:
                    errors.append("PAN number is required for employees")
            
            return errors
            
        except Exception as e:
            logger.error(f"Error validating business rules: {e}")
            return [f"Business rule validation error: {str(e)}"]

    async def validate_uniqueness_constraints(
        self, 
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_employee_id: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> Dict[str, bool]:
        """Validate uniqueness constraints."""
        try:
            result = {}
            exclude_id = EmployeeId(exclude_employee_id) if exclude_employee_id else None
            organisation_id = current_user.hostname if current_user else None
            
            if email:
                result["email_exists"] = await self.user_repository.exists_by_email(
                    email, exclude_id, organisation_id
                )
            
            if mobile:
                result["mobile_exists"] = await self.user_repository.exists_by_mobile(
                    mobile, exclude_id, organisation_id
                )
            
            if pan_number:
                result["pan_exists"] = await self.user_repository.exists_by_pan_number(
                    pan_number, exclude_id, organisation_id
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating uniqueness constraints: {e}")
            return {"error": str(e)}

    async def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength."""
        try:
            result = self.password_service.validate_password_strength(password)
            return {
                "is_strong": result["is_strong"],
                "score": result["score"],
                "feedback": result["feedback"],
                "suggestions": result["suggestions"]
            }
        except Exception as e:
            logger.error(f"Error validating password strength: {e}")
            return {
                "is_strong": False,
                "score": 0,
                "feedback": ["Error validating password"],
                "suggestions": ["Please try again"]
            }

    # New methods for the missing API endpoints
    async def health_check(self, current_user: "CurrentUser") -> Dict[str, str]:
        """Health check for user service with organisation context."""
        try:
            # Check if we can access the repository
            user_count = await self.user_repository.count(current_user.hostname)
            
            return {
                "service": "user_service",
                "status": "healthy",
                "organisation": current_user.hostname,
                "user_count": user_count,
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0"
            }
        except Exception as e:
            logger.error(f"Health check failed for organisation {current_user.hostname}: {e}")
            return {
                "service": "user_service",
                "status": "unhealthy",
                "organisation": current_user.hostname,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def import_users(
        self, 
        file_content: bytes, 
        filename: str, 
        current_user: "CurrentUser"
    ) -> Dict[str, Any]:
        """Import users from file with organisation context."""
        try:
            logger.info(f"Importing users from {filename} for organisation {current_user.hostname}")
            
            # Determine file format
            if filename.lower().endswith('.csv'):
                format_type = "csv"
            elif filename.lower().endswith(('.xlsx', '.xls')):
                format_type = "excel"
            else:
                raise ValueError("Unsupported file format. Use CSV or Excel files.")
            
            # Use the existing bulk import method
            result = await self.bulk_import_users(
                data=file_content,
                format=format_type,
                created_by=current_user.employee_id,
                validate_only=False
            )
            
            return {
                "imported_count": result.get("imported_count", 0),
                "errors": result.get("errors", []),
                "total_processed": result.get("total_processed", 0),
                "organisation": current_user.hostname,
                "imported_by": current_user.employee_id
            }
            
        except Exception as e:
            logger.error(f"Error importing users in organisation {current_user.hostname}: {e}")
            raise

    async def export_users(
        self, 
        users: List[UserResponseDTO], 
        format: str, 
        current_user: "CurrentUser"
    ) -> tuple[bytes, str]:
        """Export users to file with organisation context."""
        try:
            logger.info(f"Exporting {len(users)} users in {format} format for organisation {current_user.hostname}")
            
            # Convert UserResponseDTO to dictionary format for export
            user_data = []
            for user in users:
                user_dict = {
                    # Basic Information
                    "employee_id": user.employee_id,
                    "name": user.name,
                    "email": user.email,
                    "mobile": user.personal_details.mobile if user.personal_details else "",
                    "gender": user.personal_details.gender if user.personal_details else "",
                    "date_of_birth": user.personal_details.date_of_birth if user.personal_details else "",
                    "date_of_joining": user.personal_details.date_of_joining if user.personal_details else "",
                    "role": user.permissions.role if user.permissions else "",
                    "department": user.department or "",
                    "designation": user.designation or "",
                    "location": user.location or "",
                    "manager_id": user.manager_id or "",
                    "status": user.status,
                    
                    # Personal Details
                    "pan_number": user.personal_details.pan_number if user.personal_details else "",
                    "aadhar_number": user.personal_details.aadhar_number if user.personal_details else "",
                    "uan_number": user.personal_details.uan_number if user.personal_details else "",
                    "esi_number": user.personal_details.esi_number if user.personal_details else "",
                    
                    # Bank Details
                    "account_number": user.bank_details.account_number if user.bank_details else "",
                    "bank_name": user.bank_details.bank_name if user.bank_details else "",
                    "ifsc_code": user.bank_details.ifsc_code if user.bank_details else "",
                    "account_holder_name": user.bank_details.account_holder_name if user.bank_details else "",
                    "branch_name": user.bank_details.branch_name if user.bank_details else "",
                    "account_type": user.bank_details.account_type if user.bank_details else "",
                    
                    # System Fields
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "last_login_at": user.last_login_at
                }
                user_data.append(user_dict)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"users_export_{current_user.hostname}_{timestamp}.{format}"
            
            # Use the existing bulk export method
            file_content = await self.bulk_export_users(
                employee_ids=[user.employee_id for user in users],
                format=format,
                include_sensitive=False
            )
            
            return file_content, filename
            
        except Exception as e:
            logger.error(f"Error exporting users in organisation {current_user.hostname}: {e}")
            raise

    async def get_user_template(
        self, 
        format: str, 
        current_user: "CurrentUser"
    ) -> tuple[bytes, str]:
        """Get user import template with headers."""
        try:
            logger.info(f"Generating user template in {format} format for organisation {current_user.hostname}")
            
            # Define template headers based on the import format expected by bulk_import
            # Include all user fields and bank details
            template_headers = [
                # Basic Information
                "employee_id",
                "name", 
                "email",
                "mobile",
                "gender",
                "date_of_birth",
                "date_of_joining",
                "role",
                "department",
                "designation",
                "location",
                "manager_id",
                "status",
                
                # Personal Details
                "pan_number",
                "aadhar_number",
                "uan_number",
                "esi_number",
                
                # Bank Details
                "account_number",
                "bank_name",
                "ifsc_code",
                "account_holder_name",
                "branch_name",
                "account_type"
            ]
            
            if format.lower() == "csv":
                import csv
                import io
                
                # Create CSV content with headers only
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(template_headers)
                
                # Add a sample row with empty values
                sample_row = [""] * len(template_headers)
                writer.writerow(sample_row)
                
                file_content = output.getvalue().encode('utf-8')
                filename = f"user_import_template_{current_user.hostname}.csv"
                
            elif format.lower() == "xlsx":
                # For Excel format, we'll create a simple CSV for now
                # TODO: Implement proper Excel generation with openpyxl
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(template_headers)
                
                # Add a sample row with empty values
                sample_row = [""] * len(template_headers)
                writer.writerow(sample_row)
                
                file_content = output.getvalue().encode('utf-8')
                filename = f"user_import_template_{current_user.hostname}.csv"  # Still CSV for now
                
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Successfully generated user template: {filename}")
            return file_content, filename
            
        except Exception as e:
            logger.error(f"Error generating user template in organisation {current_user.hostname}: {e}")
            raise

    async def get_departments(self, current_user: "CurrentUser") -> List[str]:
        """Get list of departments in organisation."""
        try:
            logger.info(f"Getting departments for organisation {current_user.hostname}")
            
            # Get all users in the organisation
            users = await self.user_repository.get_all(
                skip=0,
                limit=10000,  # Large limit to get all users
                hostname=current_user.hostname
            )
            
            # Extract unique departments
            departments = set()
            for user in users:
                if user.department:
                    departments.add(user.department)
            
            # Return sorted list
            return sorted(list(departments))
            
        except Exception as e:
            logger.error(f"Error getting departments in organisation {current_user.hostname}: {e}")
            raise

    async def get_designations(self, current_user: "CurrentUser") -> List[str]:
        """Get list of designations in organisation."""
        try:
            logger.info(f"Getting designations for organisation {current_user.hostname}")
            
            # Get all users in the organisation
            users = await self.user_repository.get_all(
                skip=0,
                limit=10000,  # Large limit to get all users
                hostname=current_user.hostname
            )
            
            # Extract unique designations
            designations = set()
            for user in users:
                if user.designation:
                    designations.add(user.designation)
            
            # Return sorted list
            return sorted(list(designations))
            
        except Exception as e:
            logger.error(f"Error getting designations in organisation {current_user.hostname}: {e}")
            raise

    async def update_user_documents(
        self, 
        user_id: str, 
        documents: Dict[str, str], 
        current_user: "CurrentUser"
    ) -> None:
        """Update user documents."""
        try:
            logger.info(f"Updating documents for user {user_id} in organisation {current_user.hostname}")
            
            # Get existing user
            user = await self.user_repository.get_by_id(EmployeeId(user_id), current_user.hostname)
            if not user:
                raise ValueError(f"User not found: {user_id}")
            
            # Update document paths
            if "photo_path" in documents:
                user.update_photo_path(documents["photo_path"])
            if "pan_document_path" in documents:
                user.update_pan_document_path(documents["pan_document_path"])
            if "aadhar_document_path" in documents:
                user.update_aadhar_document_path(documents["aadhar_document_path"])
            
            # Save updated user
            await self.user_repository.save(user, current_user.hostname)
            
            logger.info(f"Successfully updated documents for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating documents for user {user_id} in organisation {current_user.hostname}: {e}")
            raise 