"""
User Controller Implementation
SOLID-compliant controller for user HTTP operations with organization segregation
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, UploadFile, Form
import json

from app.application.interfaces.services.user_service import UserService
from app.application.dto.user_dto import (
    CreateUserRequestDTO, UpdateUserRequestDTO, UpdateUserDocumentsRequestDTO,
    ChangeUserPasswordRequestDTO, ChangeUserRoleRequestDTO, UserStatusUpdateRequestDTO,
    UserSearchFiltersDTO, UserLoginRequestDTO, UserResponseDTO, UserSummaryDTO,
    UserListResponseDTO, UserStatisticsDTO, UserAnalyticsDTO, UserLoginResponseDTO
)
from app.infrastructure.services.file_upload_service import FileUploadService, DocumentType
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class UserController:
    """
    User controller following SOLID principles with organization segregation.
    
    - SRP: Only handles HTTP request/response concerns
    - OCP: Can be extended with new endpoints
    - LSP: Can be substituted with other controllers
    - ISP: Focused interface for user HTTP operations
    - DIP: Depends on abstractions (UserService, FileUploadService)
    """
    
    def __init__(
        self,
        user_service: UserService,
        file_upload_service: FileUploadService
    ):
        """
        Initialize controller with dependencies.
        
        Args:
            user_service: User service for business operations
            file_upload_service: Service for file operations
        """
        self.user_service = user_service
        self.file_upload_service = file_upload_service
    
    async def create_user(
        self, 
        request: CreateUserRequestDTO, 
        current_user: CurrentUser
    ) -> UserResponseDTO:
        """Create a new user with organization context."""
        try:
            logger.info(f"Creating user: {request.employee_id} in organization: {current_user.hostname}")
            return await self.user_service.create_user(request, current_user)
        except Exception as e:
            logger.error(f"Error creating user {request.employee_id} in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_user_with_files(
        self,
        user_data: str,
        current_user: CurrentUser,
        pan_file: Optional[UploadFile] = None,
        aadhar_file: Optional[UploadFile] = None,
        photo: Optional[UploadFile] = None
    ) -> UserResponseDTO:
        """Create user with file uploads and organization context."""
        try:
            # Parse user data
            user_dict = json.loads(user_data)
            
            # Handle file uploads with organization-specific paths
            if photo:
                photo_path = await self.file_upload_service.upload_document(
                    photo, DocumentType.PHOTO, current_user.hostname
                )
                user_dict["photo_path"] = photo_path
            
            if pan_file:
                pan_path = await self.file_upload_service.upload_document(
                    pan_file, DocumentType.PAN, current_user.hostname
                )
                user_dict["pan_document_path"] = pan_path
            
            if aadhar_file:
                aadhar_path = await self.file_upload_service.upload_document(
                    aadhar_file, DocumentType.AADHAR, current_user.hostname
                )
                user_dict["aadhar_document_path"] = aadhar_path
            
            # Create request DTO
            request = CreateUserRequestDTO(**user_dict)
            
            # Create user with organization context
            return await self.user_service.create_user(request, current_user)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in user_data: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON in user_data")
        except Exception as e:
            logger.error(f"Error creating user with files in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_user_by_id(
        self, 
        employee_id: str, 
        current_user: CurrentUser
    ) -> UserResponseDTO:
        """Get user by ID with organization context."""
        try:
            user = await self.user_service.get_user_by_id(employee_id, current_user)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user {employee_id} in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def authenticate_user(self, request: UserLoginRequestDTO) -> UserLoginResponseDTO:
        """Authenticate user (no organization context needed for login)."""
        try:
            return await self.user_service.authenticate_user(request)
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 20,
        include_inactive: bool = False,
        include_deleted: bool = False,
        current_user: CurrentUser = None
    ) -> UserListResponseDTO:
        """Get all users with pagination and organization context."""
        try:
            return await self.user_service.get_all_users(
                skip=skip,
                limit=limit,
                include_inactive=include_inactive,
                include_deleted=include_deleted,
                current_user=current_user
            )
        except Exception as e:
            logger.error(f"Error getting all users in organization {current_user.hostname if current_user else 'unknown'}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def search_users(
        self, 
        filters: UserSearchFiltersDTO, 
        current_user: CurrentUser
    ) -> UserListResponseDTO:
        """Search users with filters and organization context."""
        try:
            return await self.user_service.search_users(filters, current_user)
        except Exception as e:
            logger.error(f"Error searching users in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def update_user(
        self,
        employee_id: str,
        request: UpdateUserRequestDTO,
        current_user: CurrentUser
    ) -> UserResponseDTO:
        """Update user with organization context."""
        try:
            return await self.user_service.update_user(employee_id, request, current_user)
        except Exception as e:
            logger.error(f"Error updating user {employee_id} in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def change_user_password(
        self,
        employee_id: str,
        request: ChangeUserPasswordRequestDTO,
        current_user: CurrentUser
    ) -> UserResponseDTO:
        """Change user password with organization context."""
        try:
            return await self.user_service.change_user_password(employee_id, request, current_user)
        except Exception as e:
            logger.error(f"Error changing password for user {employee_id} in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_user_statistics(self, current_user: CurrentUser) -> UserStatisticsDTO:
        """Get user statistics with organization context."""
        try:
            return await self.user_service.get_user_statistics(current_user)
        except Exception as e:
            logger.error(f"Error getting user statistics in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_user_by_email(
        self, 
        email: str, 
        current_user: CurrentUser
    ) -> UserResponseDTO:
        """Get user by email with organization context."""
        try:
            user = await self.user_service.get_user_by_email(email, current_user)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user by email {email} in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def change_user_role(
        self,
        employee_id: str,
        request: ChangeUserRoleRequestDTO,
        current_user: CurrentUser
    ) -> UserResponseDTO:
        """Change user role with organization context."""
        try:
            return await self.user_service.change_user_role(employee_id, request, current_user)
        except Exception as e:
            logger.error(f"Error changing role for user {employee_id} in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    async def update_user_status(
        self,
        employee_id: str,
        request: UserStatusUpdateRequestDTO,
        current_user: CurrentUser
    ) -> UserResponseDTO:
        """Update user status with organization context."""
        try:
            return await self.user_service.update_user_status(employee_id, request, current_user)
        except Exception as e:
            logger.error(f"Error updating status for user {employee_id} in organization {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    async def check_user_exists(
        self,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None,
        current_user: CurrentUser = None
    ) -> Dict[str, bool]:
        """Check if user exists with organization context."""
        try:
            return await self.user_service.check_user_exists(
                email=email,
                mobile=mobile,
                pan_number=pan_number,
                exclude_id=exclude_id,
                current_user=current_user
            )
        except Exception as e:
            logger.error(f"Error checking user existence in organization {current_user.hostname if current_user else 'unknown'}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def health_check(self) -> Dict[str, str]:
        """Health check endpoint (no organization context needed)."""
        return {
            "service": "user_controller",
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "2.0.0-organization-segregated"
        }