"""
User Controller Implementation
SOLID-compliant controller for user HTTP operations
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, UploadFile, Form
import json

from application.interfaces.services.user_service import UserService
from application.dto.user_dto import (
    CreateUserRequestDTO, UpdateUserRequestDTO, UpdateUserDocumentsRequestDTO,
    ChangeUserPasswordRequestDTO, ChangeUserRoleRequestDTO, UserStatusUpdateRequestDTO,
    UserSearchFiltersDTO, UserLoginRequestDTO, UserResponseDTO, UserSummaryDTO,
    UserListResponseDTO, UserStatisticsDTO, UserAnalyticsDTO, UserLoginResponseDTO
)
from infrastructure.services.file_upload_service import FileUploadService, DocumentType

logger = logging.getLogger(__name__)


class UserController:
    """
    User controller following SOLID principles.
    
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
    
    async def create_user(self, request: CreateUserRequestDTO) -> UserResponseDTO:
        """Create a new user."""
        try:
            logger.info(f"Creating user: {request.employee_id}")
            return await self.user_service.create_user(request)
        except Exception as e:
            logger.error(f"Error creating user {request.employee_id}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_user_with_files(
        self,
        user_data: str,
        pan_file: Optional[UploadFile] = None,
        aadhar_file: Optional[UploadFile] = None,
        photo: Optional[UploadFile] = None
    ) -> UserResponseDTO:
        """Create user with file uploads."""
        try:
            # Parse user data
            user_dict = json.loads(user_data)
            
            # Handle file uploads
            if photo:
                photo_path = await self.file_upload_service.upload_document(
                    photo, DocumentType.PHOTO
                )
                user_dict["photo_path"] = photo_path
            
            if pan_file:
                pan_path = await self.file_upload_service.upload_document(
                    pan_file, DocumentType.PAN
                )
                user_dict["pan_document_path"] = pan_path
            
            if aadhar_file:
                aadhar_path = await self.file_upload_service.upload_document(
                    aadhar_file, DocumentType.AADHAR
                )
                user_dict["aadhar_document_path"] = aadhar_path
            
            # Create request DTO
            request = CreateUserRequestDTO(**user_dict)
            
            # Create user
            return await self.user_service.create_user(request)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in user_data: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON in user_data")
        except Exception as e:
            logger.error(f"Error creating user with files: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_user_by_id(self, user_id: str) -> UserResponseDTO:
        """Get user by ID."""
        try:
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def authenticate_user(self, request: UserLoginRequestDTO) -> UserLoginResponseDTO:
        """Authenticate user."""
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
        organization_id: Optional[str] = None
    ) -> UserListResponseDTO:
        """Get all users with pagination."""
        try:
            return await self.user_service.get_all_users(
                skip=skip,
                limit=limit,
                include_inactive=include_inactive,
                include_deleted=include_deleted
            )
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def search_users(self, filters: UserSearchFiltersDTO) -> UserListResponseDTO:
        """Search users with filters."""
        try:
            return await self.user_service.search_users(filters)
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def update_user(
        self,
        user_id: str,
        request: UpdateUserRequestDTO
    ) -> UserResponseDTO:
        """Update user."""
        try:
            return await self.user_service.update_user(user_id, request)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def change_user_password(
        self,
        user_id: str,
        request: ChangeUserPasswordRequestDTO
    ) -> UserResponseDTO:
        """Change user password."""
        try:
            return await self.user_service.change_user_password(user_id, request)
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_user_statistics(self) -> UserStatisticsDTO:
        """Get user statistics."""
        try:
            return await self.user_service.get_user_statistics()
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_user_by_email(self, email: str) -> UserResponseDTO:
        """Get user by email."""
        try:
            user = await self.user_service.get_user_by_email(email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def change_user_role(
        self,
        user_id: str,
        request: ChangeUserRoleRequestDTO
    ) -> UserResponseDTO:
        """Change user role."""
        try:
            return await self.user_service.change_user_role(user_id, request)
        except Exception as e:
            logger.error(f"Error changing role for user {user_id}: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    async def update_user_status(
        self,
        user_id: str,
        request: UserStatusUpdateRequestDTO
    ) -> UserResponseDTO:
        """Update user status."""
        try:
            return await self.user_service.update_user_status(user_id, request)
        except Exception as e:
            logger.error(f"Error updating status for user {user_id}: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    async def check_user_exists(
        self,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        pan_number: Optional[str] = None,
        exclude_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """Check if user exists."""
        try:
            return await self.user_service.check_user_exists(
                email=email,
                mobile=mobile,
                pan_number=pan_number,
                exclude_id=exclude_id
            )
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def health_check(self) -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "service": "user_controller"} 