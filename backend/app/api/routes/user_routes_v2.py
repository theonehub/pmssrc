"""
SOLID-Compliant User Routes
Clean architecture implementation of user HTTP endpoints
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse

from api.controllers.user_controller import UserController
from application.dto.user_dto import (
    CreateUserRequestDTO, UpdateUserRequestDTO, UpdateUserDocumentsRequestDTO,
    ChangeUserPasswordRequestDTO, ChangeUserRoleRequestDTO, UserStatusUpdateRequestDTO,
    UserSearchFiltersDTO, UserLoginRequestDTO, UserResponseDTO, UserSummaryDTO,
    UserListResponseDTO, UserStatisticsDTO, UserAnalyticsDTO, UserLoginResponseDTO
)
from config.dependency_container import get_user_controller

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/users", tags=["users"])

# Health check endpoint
@router.get("/health")
async def health_check(
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, str]:
    """Health check for user service."""
    return await controller.health_check()

# User creation endpoints
@router.post("", response_model=UserResponseDTO)
async def create_user(
    request: CreateUserRequestDTO,
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """
    Create a new user.
    
    Args:
        request: User creation request
        controller: User controller dependency
        
    Returns:
        Created user response
    """
    return await controller.create_user(request)

@router.post("/with-files", response_model=UserResponseDTO)
async def create_user_with_files(
    user_data: str = Form(..., description="JSON string containing user data"),
    pan_file: Optional[UploadFile] = File(None, description="PAN document file"),
    aadhar_file: Optional[UploadFile] = File(None, description="Aadhar document file"),
    photo: Optional[UploadFile] = File(None, description="User photo file"),
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """
    Create a new user with document uploads.
    
    Args:
        user_data: JSON string containing user information
        pan_file: PAN document file (optional)
        aadhar_file: Aadhar document file (optional)
        photo: User photo file (optional)
        controller: User controller dependency
        
    Returns:
        Created user response
    """
    return await controller.create_user_with_files(
        user_data=user_data,
        pan_file=pan_file,
        aadhar_file=aadhar_file,
        photo=photo
    )

# Authentication endpoints
@router.post("/auth/login", response_model=UserLoginResponseDTO)
async def authenticate_user(
    request: UserLoginRequestDTO,
    controller: UserController = Depends(get_user_controller)
) -> UserLoginResponseDTO:
    """
    Authenticate user and return access tokens.
    
    Args:
        request: Login request with credentials
        controller: User controller dependency
        
    Returns:
        Login response with tokens and user info
    """
    return await controller.authenticate_user(request)

# User query endpoints
@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_user_by_id(
    user_id: str,
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """
    Get user by ID.
    
    Args:
        user_id: User ID to retrieve
        controller: User controller dependency
        
    Returns:
        User response
    """
    return await controller.get_user_by_id(user_id)

@router.get("/email/{email}", response_model=UserResponseDTO)
async def get_user_by_email(
    email: str,
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """
    Get user by email address.
    
    Args:
        email: Email address to search for
        controller: User controller dependency
        
    Returns:
        User response
    """
    return await controller.get_user_by_email(email)

@router.get("", response_model=UserListResponseDTO)
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    include_inactive: bool = Query(False, description="Include inactive users"),
    include_deleted: bool = Query(False, description="Include deleted users"),
    organization_id: Optional[str] = Query(None, description="Filter by organization ID"),
    controller: UserController = Depends(get_user_controller)
) -> UserListResponseDTO:
    """
    Get all users with pagination and filters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_inactive: Whether to include inactive users
        include_deleted: Whether to include deleted users
        organization_id: Filter by organization ID
        controller: User controller dependency
        
    Returns:
        Paginated list of users
    """
    return await controller.get_all_users(
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
        include_deleted=include_deleted,
        organization_id=organization_id
    )

@router.post("/search", response_model=UserListResponseDTO)
async def search_users(
    filters: UserSearchFiltersDTO,
    controller: UserController = Depends(get_user_controller)
) -> UserListResponseDTO:
    """
    Search users with advanced filters.
    
    Args:
        filters: Search filters and pagination parameters
        controller: User controller dependency
        
    Returns:
        Filtered list of users
    """
    return await controller.search_users(filters)

# User update endpoints
@router.put("/{user_id}", response_model=UserResponseDTO)
async def update_user(
    user_id: str,
    request: UpdateUserRequestDTO,
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """
    Update user information.
    
    Args:
        user_id: User ID to update
        request: Update request with new user data
        controller: User controller dependency
        
    Returns:
        Updated user response
    """
    return await controller.update_user(user_id, request)

@router.patch("/{user_id}/password", response_model=UserResponseDTO)
async def change_user_password(
    user_id: str,
    request: ChangeUserPasswordRequestDTO,
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """
    Change user password.
    
    Args:
        user_id: User ID
        request: Password change request
        controller: User controller dependency
        
    Returns:
        Updated user response
    """
    return await controller.change_user_password(user_id, request)

@router.patch("/{user_id}/role", response_model=UserResponseDTO)
async def change_user_role(
    user_id: str,
    request: ChangeUserRoleRequestDTO,
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """
    Change user role.
    
    Args:
        user_id: User ID
        request: Role change request
        controller: User controller dependency
        
    Returns:
        Updated user response
    """
    return await controller.change_user_role(user_id, request)

@router.patch("/{user_id}/status", response_model=UserResponseDTO)
async def update_user_status(
    user_id: str,
    request: UserStatusUpdateRequestDTO,
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """
    Update user status (activate, deactivate, suspend, etc.).
    
    Args:
        user_id: User ID
        request: Status update request
        controller: User controller dependency
        
    Returns:
        Updated user response
    """
    return await controller.update_user_status(user_id, request)

# User existence and validation endpoints
@router.get("/check/exists")
async def check_user_exists(
    email: Optional[str] = Query(None, description="Email to check"),
    mobile: Optional[str] = Query(None, description="Mobile number to check"),
    pan_number: Optional[str] = Query(None, description="PAN number to check"),
    exclude_id: Optional[str] = Query(None, description="User ID to exclude from check"),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, bool]:
    """
    Check if user exists by various identifiers.
    
    Args:
        email: Email to check for existence
        mobile: Mobile number to check for existence
        pan_number: PAN number to check for existence
        exclude_id: User ID to exclude from existence check
        controller: User controller dependency
        
    Returns:
        Dictionary indicating existence for each checked field
    """
    return await controller.check_user_exists(
        email=email,
        mobile=mobile,
        pan_number=pan_number,
        exclude_id=exclude_id
    )

# Analytics and statistics endpoints
@router.get("/analytics/statistics", response_model=UserStatisticsDTO)
async def get_user_statistics(
    controller: UserController = Depends(get_user_controller)
) -> UserStatisticsDTO:
    """
    Get comprehensive user statistics.
    
    Args:
        controller: User controller dependency
        
    Returns:
        User statistics including counts, distributions, and trends
    """
    return await controller.get_user_statistics()

# Legacy compatibility endpoints (for gradual migration)
@router.get("/legacy/all")
async def get_all_users_legacy(
    hostname: str = Query(..., description="Organization hostname"),
    controller: UserController = Depends(get_user_controller)
) -> List[Dict[str, Any]]:
    """
    Legacy endpoint for getting all users (for backward compatibility).
    
    Args:
        hostname: Organization hostname
        controller: User controller dependency
        
    Returns:
        List of users in legacy format
    """
    # Get users using new service
    result = await controller.get_all_users(
        skip=0,
        limit=1000,  # Large limit for legacy compatibility
        include_inactive=True,
        organization_id=hostname
    )
    
    # Convert to legacy format
    legacy_users = []
    for user in result.users:
        legacy_user = {
            "emp_id": user.employee_id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "role": user.role,
            "department": user.department,
            "designation": user.designation,
            "is_active": user.status == "active",
            # Add other fields as needed for legacy compatibility
        }
        legacy_users.append(legacy_user)
    
    return legacy_users

@router.get("/legacy/{emp_id}")
async def get_user_by_emp_id_legacy(
    emp_id: str,
    hostname: str = Query(..., description="Organization hostname"),
    controller: UserController = Depends(get_user_controller)
) -> Optional[Dict[str, Any]]:
    """
    Legacy endpoint for getting user by employee ID.
    
    Args:
        emp_id: Employee ID
        hostname: Organization hostname
        controller: User controller dependency
        
    Returns:
        User in legacy format or None
    """
    try:
        user = await controller.get_user_by_id(emp_id)
        if not user:
            return None
        
        # Convert to legacy format
        return {
            "emp_id": user.employee_id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "role": user.role,
            "department": user.department,
            "designation": user.designation,
            "is_active": user.status == "active",
            "password": user.password_hash,  # For legacy compatibility
            # Add other fields as needed
        }
    except HTTPException as e:
        if e.status_code == 404:
            return None
        raise

# Error Handlers
@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    ) 