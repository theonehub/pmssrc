"""
Create User Use Case
Handles the business logic for creating a new user
"""

import logging
from typing import List
from datetime import datetime

from app.domain.entities.user import User
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_credentials import (
    UserRole, UserStatus, Gender
)
from app.domain.value_objects.user_permissions import UserPermissions
from app.domain.value_objects.personal_details import PersonalDetails
from app.domain.value_objects.user_documents import UserDocuments
from app.application.dto.user_dto import (
    CreateUserRequestDTO, UserResponseDTO,
    UserValidationError, UserConflictError,
    UserBusinessRuleError,
    PersonalDetailsResponseDTO,
    UserPermissionsResponseDTO,
    UserDocumentsResponseDTO
)
from app.application.interfaces.repositories.user_repository import (
    UserCommandRepository, UserQueryRepository
)
from app.application.interfaces.services.user_service import (
    UserValidationService, UserNotificationService
)
from app.auth.auth_dependencies import CurrentUser


logger = logging.getLogger(__name__)


class CreateUserUseCase:
    """
    Use case for creating a new user.
    
    Follows SOLID principles:
    - SRP: Only handles user creation logic
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. Employee ID must be unique
    2. Email must be unique
    3. Mobile number must be unique (if provided)
    4. PAN number must be unique (if provided)
    5. All required fields must be provided
    6. Password must meet security requirements
    7. Personal details must be valid
    8. User role must be valid
    9. Manager must exist (if assigned)
    """
    
    def __init__(
        self,
        command_repository: UserCommandRepository,
        query_repository: UserQueryRepository,
        validation_service: UserValidationService,
        notification_service: UserNotificationService
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.validation_service = validation_service
        self.notification_service = notification_service
    
    async def execute(self, request: CreateUserRequestDTO, current_user: CurrentUser) -> UserResponseDTO:
        """
        Execute the create user use case.
        
        Args:
            request: User creation request DTO
            current_user: Current authenticated user with organisation context
        Returns:
            Created user response DTO
            
        Raises:
            UserValidationError: If request data is invalid
            UserConflictError: If user already exists
            UserBusinessRuleError: If business rules are violated
        """
        logger.info(f"Creating user: {request.email} in organisation: {current_user.hostname}")
        
        # Step 1: Validate request data
        await self._validate_request(request)
        
        # Step 2: Check uniqueness constraints
        await self._check_uniqueness_constraints(request, current_user)
        
        # Step 3: Create value objects
        employee_id = EmployeeId(request.employee_id)
        personal_details = self._create_personal_details(request)
        documents = self._create_user_documents(request)
        
        # Step 3.5: Calculate initial leave balance based on company policies
        initial_leave_balance = await self._calculate_initial_leave_balance(
            UserRole(request.role.lower()), current_user
        )
        
        # Step 4: Create user entity
        user = User.create_new_user(
            employee_id=employee_id,
            name=request.name,
            email=request.email,
            password=request.password,
            role=UserRole(request.role.lower()),
            personal_details=personal_details,
            department=request.department,
            designation=request.designation,
            location=request.location,
            manager_id=EmployeeId(request.manager_id) if request.manager_id else None,
            date_of_joining=request.date_of_joining,
            created_by=request.created_by
        )
        
        # Step 4.5: Set documents and leave balance after user creation
        user.update_documents(documents, user.created_by or "system")
        user.update_leave_balance("annual", int(initial_leave_balance))
        
        # Step 5: Validate business rules
        await self._validate_business_rules(user)
        
        # Step 6: Save user
        saved_user = await self.command_repository.save(user, current_user.hostname)
        
        # Step 7: Send notifications (non-blocking)
        try:
            await self.notification_service.send_user_created_notification(saved_user)
        except Exception as e:
            logger.warning(f"Failed to send user created notification: {e}")
        
        # Step 8: Convert to response DTO
        response = self._convert_to_response_dto(saved_user)
        
        logger.info(f"User created successfully: {saved_user.employee_id}")
        return response
    
    async def _validate_request(self, request: CreateUserRequestDTO) -> None:
        """Validate the request data"""
        validation_errors = await self.validation_service.validate_user_data(request)
        
        if validation_errors:
            raise UserValidationError(
                "User creation data is invalid",
                validation_errors
            )
    
    async def _check_uniqueness_constraints(self, request: CreateUserRequestDTO, current_user: CurrentUser) -> None:
        """Check uniqueness constraints"""
        uniqueness_result = await self.validation_service.validate_uniqueness_constraints(
            email=request.email,
            mobile=request.mobile,
            pan_number=request.pan_number,  
            current_user=current_user
        )
        
        if uniqueness_result.get("email_exists") or uniqueness_result.get("mobile_exists") or uniqueness_result.get("pan_exists"):
            raise UserConflictError(
                "User conflicts with existing data " + str(uniqueness_result),
                "uniqueness"
            )
    
    def _create_personal_details(self, request: CreateUserRequestDTO) -> PersonalDetails:
        """Create personal details value object"""
        try:
            return PersonalDetails(
                gender=Gender(request.gender.lower()),
                date_of_birth=datetime.fromisoformat(request.date_of_birth).date(),
                date_of_joining=datetime.fromisoformat(request.date_of_joining).date(),
                mobile=request.mobile,
                pan_number=request.pan_number,
                aadhar_number=request.aadhar_number,
                uan_number=request.uan_number,
                esi_number=request.esi_number
            )
        except ValueError as e:
            raise UserValidationError(f"Invalid personal details: {e}")
    
    def _create_user_documents(self, request: CreateUserRequestDTO) -> UserDocuments:
        """Create user documents value object"""
        try:
            return UserDocuments(
                photo_path=request.photo_path,
                pan_document_path=request.pan_document_path,
                aadhar_document_path=request.aadhar_document_path
            )
        except ValueError as e:
            raise UserValidationError(f"Invalid user documents: {e}")
    
    async def _validate_business_rules(self, user: User) -> None:
        """Validate business rules"""
        business_rule_errors = await self.validation_service.validate_business_rules(user)
        
        if business_rule_errors:
            raise UserBusinessRuleError(
                "User violates business rules",
                "business_rules"
            )
    
    async def _calculate_initial_leave_balance(self, role: UserRole, current_user: CurrentUser) -> float:
        """
        Calculate initial leave balance based on company leave policies.
        
        Args:
            role: User role
            current_user: Current authenticated user with organisation context
            
        Returns:
            Initial leave balance in days
        """
        try:
            # TODO: Implement proper leave balance calculation based on:
            # - Company leave policies for the organisation
            # - User role and designation
            # - Joining date and pro-rata calculation
            # - Leave type allocations (annual, sick, casual, etc.)
            
            # For now, set default leave balance based on role
            default_leave_balances = {
                UserRole.SUPERADMIN: 30.0,
                UserRole.ADMIN: 25.0,
                UserRole.MANAGER: 25.0,
                UserRole.HR: 25.0,
                UserRole.FINANCE: 25.0,
                UserRole.USER: 20.0,
                UserRole.READONLY: 15.0
            }
            
            initial_balance = default_leave_balances.get(role, 20.0)
            
            logger.info(f"Calculated initial leave balance for role {role.value} in organisation {current_user.hostname}: {initial_balance} days")
            return initial_balance
            
        except Exception as e:
            logger.warning(f"Error calculating initial leave balance, using default: {e}")
            return 20.0  # Default fallback
    
    def _convert_to_response_dto(self, user: User) -> UserResponseDTO:
        """Convert user entity to response DTO"""
        return UserResponseDTO(
            employee_id=str(user.employee_id),
            name=user.name,
            email=user.email,
            status=user.status.value,
            
            # Personal Details
            personal_details=PersonalDetailsResponseDTO(
                gender=user.personal_details.gender.value,
                date_of_birth=user.personal_details.date_of_birth.isoformat(),
                date_of_joining=user.personal_details.date_of_joining.isoformat(),
                mobile=user.personal_details.mobile,
                pan_number=user.personal_details.pan_number,
                aadhar_number=user.personal_details.get_masked_aadhar(),
                uan_number=user.personal_details.uan_number,
                esi_number=user.personal_details.esi_number,
            ),
            
            # Employment Information
            department=user.department,
            designation=user.designation,
            location=user.location,
            manager_id=str(user.manager_id) if user.manager_id else None,
            date_of_joining=user.personal_details.date_of_joining.isoformat() if user.personal_details.date_of_joining else user.date_of_joining,
            date_of_leaving=user.date_of_leaving,
            
            # Authorization
            permissions=UserPermissionsResponseDTO(
                role=user.permissions.role.value,
                custom_permissions=user.permissions.custom_permissions,
                resource_permissions=user.permissions.resource_permissions,
                can_manage_users=user.permissions.can_manage_users(),
                can_view_reports=user.permissions.can_view_reports(),
                can_approve_requests=user.permissions.can_approve_requests(),
                is_admin=user.permissions.is_admin(),
                is_superadmin=user.permissions.is_superadmin(),
            ),
            
            # Documents
            documents=self._convert_documents_to_dto(user.documents),
            
            # Leave Balance
            leave_balance=user.leave_balance,
            
            # System Fields
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
            created_by=user.created_by,
            updated_by=user.updated_by,
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
            
            # Computed fields
            is_active=user.is_active(),
            is_locked=user.is_locked(),
            can_login=user.can_login(),
            profile_completion_percentage=user.get_profile_completion_percentage(),
            display_name=user.get_display_name(),
            role_display=user.get_role_display(),
            status_display=user.get_status_display(),
        )
    
    def _convert_documents_to_dto(self, documents: UserDocuments) -> UserDocumentsResponseDTO:
        """Convert user documents to DTO format"""
        return UserDocumentsResponseDTO(
            photo_path=documents.photo_path,
            pan_document_path=documents.pan_document_path,
            aadhar_document_path=documents.aadhar_document_path,
            completion_percentage=documents.get_document_completion_percentage(),
            missing_documents=documents.get_missing_documents()
        ) 