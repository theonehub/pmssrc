"""
Create User Use Case
Handles the business logic for creating a new user
"""

import logging
from typing import List
from datetime import datetime

from domain.entities.user import User
from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.user_credentials import (
    Password, UserPermissions, UserRole, UserStatus, Gender
)
from domain.value_objects.personal_details import PersonalDetails
from domain.value_objects.user_documents import UserDocuments
from application.dto.user_dto import (
    CreateUserRequestDTO, UserResponseDTO,
    UserValidationError, UserConflictError,
    UserBusinessRuleError
)
from application.interfaces.repositories.user_repository import (
    UserCommandRepository, UserQueryRepository
)
from application.interfaces.services.user_service import (
    UserValidationService, UserNotificationService
)


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
    
    async def execute(self, request: CreateUserRequestDTO) -> UserResponseDTO:
        """
        Execute the create user use case.
        
        Args:
            request: User creation request DTO
            
        Returns:
            Created user response DTO
            
        Raises:
            UserValidationError: If request data is invalid
            UserConflictError: If user already exists
            UserBusinessRuleError: If business rules are violated
        """
        logger.info(f"Creating user: {request.email}")
        
        # Step 1: Validate request data
        await self._validate_request(request)
        
        # Step 2: Check uniqueness constraints
        await self._check_uniqueness_constraints(request)
        
        # Step 3: Create value objects
        employee_id = EmployeeId(request.employee_id)
        password = self._create_password(request.password)
        personal_details = self._create_personal_details(request)
        documents = self._create_user_documents(request)
        permissions = UserPermissions.from_role(UserRole(request.role))
        
        # Step 4: Create user entity
        user = User.create_new_user(
            employee_id=employee_id,
            name=request.name,
            email=request.email,
            password=password,
            role=UserRole(request.role),
            personal_details=personal_details,
            documents=documents,
            permissions=permissions,
            department=request.department,
            designation=request.designation,
            manager_id=EmployeeId(request.manager_id) if request.manager_id else None,
            leave_balance=request.leave_balance or 0.0,
            created_by=request.created_by
        )
        
        # Step 5: Validate business rules
        await self._validate_business_rules(user)
        
        # Step 6: Save user
        saved_user = await self.command_repository.save(user)
        
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
    
    async def _check_uniqueness_constraints(self, request: CreateUserRequestDTO) -> None:
        """Check uniqueness constraints"""
        uniqueness_errors = await self.validation_service.validate_uniqueness_constraints(
            email=request.email,
            mobile=request.mobile,
            pan_number=request.pan_number
        )
        
        if uniqueness_errors:
            raise UserConflictError(
                "User conflicts with existing data",
                "uniqueness"
            )
    
    def _create_password(self, plain_password: str) -> Password:
        """Create password value object"""
        try:
            return Password.from_plain_text(plain_password)
        except ValueError as e:
            raise UserValidationError(f"Invalid password: {e}")
    
    def _create_personal_details(self, request: CreateUserRequestDTO) -> PersonalDetails:
        """Create personal details value object"""
        try:
            return PersonalDetails(
                gender=Gender(request.gender),
                date_of_birth=datetime.fromisoformat(request.date_of_birth).date(),
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
    
    def _convert_to_response_dto(self, user: User) -> UserResponseDTO:
        """Convert user entity to response DTO"""
        return UserResponseDTO(
            user_id=str(user.employee_id),
            employee_id=str(user.employee_id),
            name=user.name,
            email=user.email,
            role=user.role.value,
            status=user.status.value,
            
            # Personal Details
            gender=user.personal_details.gender.value,
            date_of_birth=user.personal_details.date_of_birth.isoformat(),
            mobile=user.personal_details.mobile,
            pan_number=user.personal_details.pan_number,
            aadhar_number=user.personal_details.masked_aadhar,
            uan_number=user.personal_details.uan_number,
            esi_number=user.personal_details.esi_number,
            
            # Work Details
            department=user.department,
            designation=user.designation,
            manager_id=str(user.manager_id) if user.manager_id else None,
            leave_balance=user.leave_balance,
            
            # Documents
            documents=self._convert_documents_to_dto(user.documents),
            
            # Permissions
            permissions=user.permissions.get_all_permissions(),
            
            # Metadata
            is_active=user.is_active(),
            is_locked=user.is_locked(),
            profile_completion_percentage=user.calculate_profile_completion(),
            last_login=user.last_login.isoformat() if user.last_login else None,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
            created_by=user.created_by
        )
    
    def _convert_documents_to_dto(self, documents: UserDocuments) -> dict:
        """Convert user documents to DTO format"""
        return {
            "photo_path": documents.photo_path,
            "pan_document_path": documents.pan_document_path,
            "aadhar_document_path": documents.aadhar_document_path,
            "completion_percentage": documents.calculate_completion_percentage(),
            "missing_documents": documents.get_missing_documents()
        } 