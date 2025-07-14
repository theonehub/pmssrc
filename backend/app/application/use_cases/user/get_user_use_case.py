"""
Get User Use Case
Handles the business logic for retrieving user information
"""

import logging
from typing import Optional

from app.domain.entities.user import User
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_documents import UserDocuments
from app.application.dto.user_dto import (
    UserResponseDTO, UserNotFoundError, UserAuthorizationError
)
from app.application.interfaces.repositories.user_repository import UserQueryRepository
from app.application.interfaces.services.user_service import UserAuthorizationService
from app.auth.auth_dependencies import CurrentUser


logger = logging.getLogger(__name__)


class GetUserUseCase:
    """
    Use case for retrieving a user by ID.
    
    Follows SOLID principles:
    - SRP: Only handles user retrieval logic
    - OCP: Can be extended with new authorization rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. User must exist
    2. Requesting user must have permission to view user data
    3. Sensitive data is filtered based on permissions
    4. Audit trail is maintained for data access
    """
    
    def __init__(
        self,
        query_repository: UserQueryRepository,
        authorization_service: UserAuthorizationService
    ):
        self.query_repository = query_repository
        self.authorization_service = authorization_service
    
    async def execute(
        self, 
        employee_id: str, 
        current_user: CurrentUser
    ) -> UserResponseDTO:
        """
        Execute the get user use case.
        Args:
            employee_id: ID of user to retrieve
            current_user: Current user context (organisation_id is current_user.hostname)
        Returns:
            User response DTO
        Raises:
            UserNotFoundError: If user not found
            UserAuthorizationError: If requesting user lacks permission
        """
        logger.info(f"Retrieving user: {employee_id}")
        # Step 1: Get user by ID (repository should use current_user.hostname for organisation context)
        user = await self._get_user_by_id(employee_id)
        # Step 2: Check authorization
        await self._check_authorization(employee_id, current_user.employee_id)
        # Step 3: Convert to response DTO with appropriate filtering
        response = self._convert_to_response_dto(user, current_user.employee_id)
        logger.info(f"User retrieved successfully: {employee_id}")
        return response
    
    async def _get_user_by_id(self, employee_id: str) -> User:
        """Get user by ID"""
        employee_id = EmployeeId(employee_id)
        user = await self.query_repository.get_by_id(employee_id)
        
        if not user:
            raise UserNotFoundError(
                f"User not found: {employee_id}",
                "user_not_found"
            )
        
        return user
    
    async def _check_authorization(
        self, 
        target_employee_id: str, 
        requesting_employee_id: Optional[str]
    ) -> None:
        """Check if requesting user can access target user's data"""
        if not requesting_employee_id:
            # System access or public API - allow basic info only
            return
        
        # Check if user can access the target user's data
        can_access = await self.authorization_service.can_access_user_data(
            requesting_employee_id, target_employee_id
        )
        
        if not can_access:
            raise UserAuthorizationError(
                "Insufficient permissions to access user data",
                "access_denied"
            )
    
    def _convert_to_response_dto(
        self, 
        user: User, 
        requesting_employee_id: Optional[str]
    ) -> UserResponseDTO:
        """Convert user entity to response DTO with appropriate filtering"""
        
        # Determine what level of detail to include based on permissions
        include_sensitive = self._should_include_sensitive_data(user, requesting_employee_id)
        include_personal = self._should_include_personal_data(user, requesting_employee_id)
        
        response = UserResponseDTO(
            employee_id=str(user.employee_id),
            name=user.name,
            email=user.email,
            role=user.role.value,
            status=user.status.value,
            
            # Work Details
            department=user.department,
            designation=user.designation,
            manager_id=str(user.manager_id) if user.manager_id else None,
            leave_balance=user.leave_balance if include_personal else None,
            
            # Permissions
            permissions=user.permissions.get_all_permissions() if include_sensitive else [],
            
            # Metadata
            is_active=user.is_active(),
            is_locked=user.is_locked() if include_sensitive else None,
            profile_completion_percentage=user.calculate_profile_completion(),
            last_login=user.last_login.isoformat() if user.last_login and include_sensitive else None,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
            created_by=user.created_by if include_sensitive else None
        )
        
        # Add personal details if authorized
        if include_personal:
            response.gender = user.personal_details.gender.value
            response.date_of_birth = user.personal_details.date_of_birth.isoformat()
            response.date_of_joining = user.personal_details.date_of_joining.isoformat()
            response.date_of_leaving = user.personal_details.date_of_leaving.isoformat() if user.personal_details.date_of_leaving else None
            response.mobile = user.personal_details.mobile
            response.uan_number = user.personal_details.uan_number
            response.esi_number = user.personal_details.esi_number
        
        # Add sensitive personal details if authorized
        if include_sensitive:
            response.pan_number = user.personal_details.pan_number
            response.aadhar_number = user.personal_details.aadhar_number
        else:
            # Provide masked versions for non-sensitive access
            response.pan_number = user.personal_details.masked_pan if include_personal else None
            response.aadhar_number = user.personal_details.masked_aadhar if include_personal else None
        
        # Add documents if authorized
        if include_personal:
            response.documents = self._convert_documents_to_dto(user.documents, include_sensitive)
        
        return response
    
    def _should_include_sensitive_data(
        self, 
        user: User, 
        requesting_employee_id: Optional[str]
    ) -> bool:
        """Determine if sensitive data should be included"""
        if not requesting_employee_id:
            return False
        
        # User can always see their own sensitive data
        if str(user.employee_id) == requesting_employee_id:
            return True
        
        # This would typically check if requesting user has admin/HR permissions
        # For now, we'll use a simple check
        return False
    
    def _should_include_personal_data(
        self, 
        user: User, 
        requesting_employee_id: Optional[str]
    ) -> bool:
        """Determine if personal data should be included"""
        if not requesting_employee_id:
            return False
        
        # User can always see their own personal data
        if str(user.employee_id) == requesting_employee_id:
            return True
        
        # This would typically check if requesting user has appropriate permissions
        # For now, we'll use a simple check
        return False
    
    def _convert_documents_to_dto(self, documents: UserDocuments, include_sensitive: bool) -> dict:
        """Convert user documents to DTO format"""
        if include_sensitive:
            return {
                "photo_path": documents.photo_path,
                "pan_document_path": documents.pan_document_path,
                "aadhar_document_path": documents.aadhar_document_path,
                "completion_percentage": documents.calculate_completion_percentage(),
                "missing_documents": documents.get_missing_documents()
            }
        else:
            return {
                "photo_path": documents.photo_path,
                "pan_document_path": "***" if documents.pan_document_path else None,
                "aadhar_document_path": "***" if documents.aadhar_document_path else None,
                "completion_percentage": documents.calculate_completion_percentage(),
                "missing_documents": documents.get_missing_documents()
            } 