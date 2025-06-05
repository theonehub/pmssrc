"""
SOLID-Compliant User Routes - Complete Implementation
Clean architecture implementation of user HTTP endpoints with organisation-based segregation
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Path, Body
from fastapi import status as http_status
from fastapi.responses import JSONResponse
from datetime import datetime

from app.api.controllers.user_controller import UserController
from app.application.dto.user_dto import (
    CreateUserRequestDTO, UpdateUserRequestDTO, UpdateUserDocumentsRequestDTO,
    ChangeUserPasswordRequestDTO, ChangeUserRoleRequestDTO, UserStatusUpdateRequestDTO,
    UserSearchFiltersDTO, UserLoginRequestDTO, UserResponseDTO, UserSummaryDTO,
    UserListResponseDTO, UserStatisticsDTO, UserAnalyticsDTO, UserLoginResponseDTO
)
from app.config.dependency_container import get_user_controller
from app.auth.auth_dependencies import CurrentUser, get_current_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/users", tags=["Users V2"])

# Health check endpoint
@router.get("/health")
async def health_check(
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, str]:
    """Health check for user service."""
    try:
        # Pass organisation context to controller
        return await controller.health_check(current_user)
    except Exception:
        # Fallback for minimal implementation
        return {
            "service": "user_service",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-complete",
            "organisation": current_user.hostname
        }

# User creation endpoints
@router.post("", response_model=UserResponseDTO)
async def create_user(
    request: CreateUserRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
) -> UserResponseDTO:
    """Create a new user."""
    # Pass organisation context to controller
    return await controller.create_user(request, current_user)

@router.post("/create")
async def create_user_legacy(
    user_data: Dict[str, Any] = Body(..., description="User creation data"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Create a new user (legacy endpoint)."""
    try:
        # Convert legacy format to DTO and include organisation context
        request = CreateUserRequestDTO(**user_data)
        result = await controller.create_user(request, current_user)
        
        return {
            "success": True,
            "message": "User created successfully",
            "employee_id": result.employee_id,
            "name": result.name,
            "email": result.email,
            "department": result.department,
            "designation": result.designation,
            "organisation": current_user.hostname,
            "created_at": datetime.now().isoformat(),
            "created_by": current_user.employee_id
        }
    except Exception as e:
        logger.error(f"Error creating user in organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/with-files", response_model=UserResponseDTO)
async def create_user_with_files(
    user_data: str = Form(..., description="JSON string containing user data"),
    pan_file: Optional[UploadFile] = File(None, description="PAN document file"),
    aadhar_file: Optional[UploadFile] = File(None, description="Aadhar document file"),
    photo: Optional[UploadFile] = File(None, description="User photo file"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """Create a new user with document uploads."""
    return await controller.create_user_with_files(
        user_data=user_data,
        pan_file=pan_file,
        aadhar_file=aadhar_file,
        photo=photo,
        current_user=current_user
    )

# Authentication endpoints (no auth required for login)
@router.post("/auth/login", response_model=UserLoginResponseDTO)
async def authenticate_user(
    request: UserLoginRequestDTO,
    controller: UserController = Depends(get_user_controller)
) -> UserLoginResponseDTO:
    """Authenticate user and return access tokens."""
    return await controller.authenticate_user(request)

# User query endpoints
@router.get("/me")
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Get current user's profile."""
    try:
        user = await controller.get_user_by_id(current_user.employee_id, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "employee_id": user.employee_id,
            "name": user.name,
            "email": user.email,
            "department": user.department,
            "designation": user.designation,
            "role": user.role,
            "organisation": current_user.hostname,
            "last_login": user.last_login_at,
            "permissions": current_user.permissions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user profile for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my/directs")
async def get_my_directs(
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> List[Dict[str, Any]]:
    """Get direct reports for current user."""
    try:
        logger.info(f"Getting direct reports for user {current_user.employee_id} in organisation {current_user.hostname}")
        
        # Get direct reports using controller with organisation context
        directs = await controller.get_users_by_manager(current_user.employee_id, current_user)
        
        return [
            {
                "employee_id": direct.employee_id,
                "name": direct.name,
                "email": direct.email,
                "department": direct.department,
                "designation": direct.designation,
                "date_of_joining": direct.date_of_joining.isoformat() if direct.date_of_joining else None,
                "status": direct.status,
                "organisation": current_user.hostname
            }
            for direct in directs
        ]
        
    except Exception as e:
        logger.error(f"Error getting direct reports for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/manager/directs")
async def get_manager_directs(
    manager_id: str = Query(..., description="Manager ID"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> List[Dict[str, Any]]:
    """Get direct reports for a specific manager."""
    try:
        logger.info(f"Getting direct reports for manager {manager_id} in organisation {current_user.hostname}")
        
        # Get direct reports using controller with organisation context
        directs = await controller.get_users_by_manager(manager_id, current_user)
        
        return [
            {
                "employee_id": direct.employee_id,
                "name": direct.name,
                "email": direct.email,
                "department": direct.department,
                "designation": direct.designation,
                "manager_id": manager_id,
                "date_of_joining": direct.date_of_joining.isoformat() if direct.date_of_joining else None,
                "status": direct.status,
                "organisation": current_user.hostname
            }
            for direct in directs
        ]
        
    except Exception as e:
        logger.error(f"Error getting manager directs for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_user_stats(
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Get user statistics."""
    try:
        stats = await controller.get_user_statistics(current_user)
        return {
            "total_users": stats.total_users,
            "active_users": stats.active_users,
            "inactive_users": stats.inactive_users,
            "departments": stats.department_distribution,
            "roles": stats.role_distribution,
            "recent_joiners": stats.recent_joiners_count,
            "organisation": current_user.hostname,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting user stats for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{employee_id}")
async def get_user_by_id(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Get user by ID with complete details."""
    try:
        user = await controller.get_user_by_id(employee_id, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Retrieved user {employee_id} for organisation {current_user.hostname}")
        
        # Safe attribute access with proper defaults
        def safe_get(obj, attr, default=None):
            try:
                value = getattr(obj, attr, default)
                return value if value is not None else default
            except (AttributeError, TypeError):
                return default
        
        def format_date(date_value):
            if date_value is None:
                return None
            if hasattr(date_value, 'isoformat'):
                return date_value.isoformat()
            return str(date_value)
        
        # Return flattened structure for better frontend compatibility
        user_data = {
            "employee_id": str(safe_get(user, 'employee_id', '')),
            "name": safe_get(user, 'name', ''),
            "email": safe_get(user, 'email', ''),
            "department": safe_get(user, 'department', ''),
            "designation": safe_get(user, 'designation', ''),
            "role": safe_get(user.permissions, 'role', 'user') if hasattr(user, 'permissions') and user.permissions else safe_get(user, 'role', 'user'),
            "date_of_joining": format_date(safe_get(user, 'date_of_joining')),
            "date_of_birth": format_date(safe_get(user.personal_details, 'date_of_birth') if hasattr(user, 'personal_details') and user.personal_details else safe_get(user, 'date_of_birth')),
            "gender": safe_get(user.personal_details, 'gender') if hasattr(user, 'personal_details') and user.personal_details else safe_get(user, 'gender'),
            "mobile": safe_get(user.personal_details, 'mobile') if hasattr(user, 'personal_details') and user.personal_details else safe_get(user, 'mobile'),
            "status": safe_get(user, 'status', 'active'),
            "manager_id": str(safe_get(user, 'manager_id', '')) if safe_get(user, 'manager_id') else '',
            "address": safe_get(user, 'address', ''),
            "emergency_contact": safe_get(user, 'emergency_contact', ''),
            "blood_group": safe_get(user, 'blood_group', ''),
            "location": safe_get(user, 'location', ''),
            "pan_number": safe_get(user.personal_details, 'pan_number') if hasattr(user, 'personal_details') and user.personal_details else safe_get(user, 'pan_number'),
            "aadhar_number": safe_get(user.personal_details, 'aadhar_number') if hasattr(user, 'personal_details') and user.personal_details else safe_get(user, 'aadhar_number'),
            "uan_number": safe_get(user.personal_details, 'uan_number') if hasattr(user, 'personal_details') and user.personal_details else safe_get(user, 'uan_number'),
            "esi_number": safe_get(user.personal_details, 'esi_number') if hasattr(user, 'personal_details') and user.personal_details else safe_get(user, 'esi_number'),
            "pan_document_path": safe_get(user.documents, 'pan_document_path') if hasattr(user, 'documents') and user.documents else safe_get(user, 'pan_document_path'),
            "aadhar_document_path": safe_get(user.documents, 'aadhar_document_path') if hasattr(user, 'documents') and user.documents else safe_get(user, 'aadhar_document_path'),
            "photo_path": safe_get(user.documents, 'photo_path') if hasattr(user, 'documents') and user.documents else safe_get(user, 'photo_path'),
            "organisation": current_user.hostname,
            "created_at": format_date(safe_get(user, 'created_at')),
            "updated_at": format_date(safe_get(user, 'updated_at')),
            "is_active": safe_get(user, 'is_active', True),
            "last_login_at": format_date(safe_get(user, 'last_login_at'))
        }
        
        logger.info(f"Returning user data with fields: {list(user_data.keys())}")
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {employee_id} for organisation {current_user.hostname}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user: {str(e)}"
        )

@router.get("/email/{email}", response_model=UserResponseDTO)
async def get_user_by_email(
    email: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """Get user by email address."""
    return await controller.get_user_by_email(email, current_user)

@router.get("")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    include_inactive: bool = Query(False, description="Include inactive users"),
    include_deleted: bool = Query(False, description="Include deleted users"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Get all users with pagination and filters."""
    try:
        result = await controller.get_all_users(
            skip=skip,
            limit=limit,
            include_inactive=include_inactive,
            include_deleted=include_deleted,
            current_user=current_user
        )
        
        return {
            "users": [
                {
                    "employee_id": user.employee_id,
                    "name": user.name,
                    "email": user.email,
                    "mobile": user.mobile,
                    "role": user.role,
                    "status": user.status,
                    "department": user.department,
                    "designation": user.designation,
                    "is_active": user.is_active,
                    "is_locked": user.is_locked,
                    "profile_completion_percentage": user.profile_completion_percentage,
                    "last_login_at": user.last_login_at,
                    "created_at": user.created_at
                }
                for user in result.users
            ],
            "total": result.total_count,
            "skip": skip,
            "limit": limit,
            "organisation": current_user.hostname
        }
    except Exception as e:
        logger.error(f"Error getting users for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=UserListResponseDTO)
async def search_users(
    filters: UserSearchFiltersDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> UserListResponseDTO:
    """Search users with advanced filters."""
    return await controller.search_users(filters, current_user)

# User update endpoints
@router.put("/{employee_id}")
async def update_user(
    employee_id: str,
    request: UpdateUserRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Update user information."""
    try:
        result = await controller.update_user(employee_id, request, current_user)
        
        logger.info(f"Updated user {employee_id} for organisation {current_user.hostname}")
        
        # Return flattened structure consistent with get_user_by_id
        def safe_get(obj, attr, default=None):
            try:
                value = getattr(obj, attr, default)
                return value if value is not None else default
            except (AttributeError, TypeError):
                return default
        
        def format_date(date_value):
            if date_value is None:
                return None
            if hasattr(date_value, 'isoformat'):
                return date_value.isoformat()
            return str(date_value)
        
        user_data = {
            "employee_id": str(safe_get(result, 'employee_id', '')),
            "name": safe_get(result, 'name', ''),
            "email": safe_get(result, 'email', ''),
            "department": safe_get(result, 'department', ''),
            "designation": safe_get(result, 'designation', ''),
            "role": safe_get(result.permissions, 'role', 'user') if hasattr(result, 'permissions') and result.permissions else safe_get(result, 'role', 'user'),
            "date_of_joining": format_date(safe_get(result, 'date_of_joining')),
            "date_of_birth": format_date(safe_get(result.personal_details, 'date_of_birth') if hasattr(result, 'personal_details') and result.personal_details else safe_get(result, 'date_of_birth')),
            "gender": safe_get(result.personal_details, 'gender') if hasattr(result, 'personal_details') and result.personal_details else safe_get(result, 'gender'),
            "mobile": safe_get(result.personal_details, 'mobile') if hasattr(result, 'personal_details') and result.personal_details else safe_get(result, 'mobile'),
            "status": safe_get(result, 'status', 'active'),
            "manager_id": str(safe_get(result, 'manager_id', '')) if safe_get(result, 'manager_id') else '',
            "address": safe_get(result, 'address', ''),
            "emergency_contact": safe_get(result, 'emergency_contact', ''),
            "blood_group": safe_get(result, 'blood_group', ''),
            "location": safe_get(result, 'location', ''),
            "pan_number": safe_get(result.personal_details, 'pan_number') if hasattr(result, 'personal_details') and result.personal_details else safe_get(result, 'pan_number'),
            "aadhar_number": safe_get(result.personal_details, 'aadhar_number') if hasattr(result, 'personal_details') and result.personal_details else safe_get(result, 'aadhar_number'),
            "uan_number": safe_get(result.personal_details, 'uan_number') if hasattr(result, 'personal_details') and result.personal_details else safe_get(result, 'uan_number'),
            "esi_number": safe_get(result.personal_details, 'esi_number') if hasattr(result, 'personal_details') and result.personal_details else safe_get(result, 'esi_number'),
            "pan_document_path": safe_get(result.documents, 'pan_document_path') if hasattr(result, 'documents') and result.documents else safe_get(result, 'pan_document_path'),
            "aadhar_document_path": safe_get(result.documents, 'aadhar_document_path') if hasattr(result, 'documents') and result.documents else safe_get(result, 'aadhar_document_path'),
            "photo_path": safe_get(result.documents, 'photo_path') if hasattr(result, 'documents') and result.documents else safe_get(result, 'photo_path'),
            "organisation": current_user.hostname,
            "created_at": format_date(safe_get(result, 'created_at')),
            "updated_at": format_date(safe_get(result, 'updated_at')),
            "is_active": safe_get(result, 'is_active', True),
            "last_login_at": format_date(safe_get(result, 'last_login_at'))
        }
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {employee_id} for organisation {current_user.hostname}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update user: {str(e)}"
        )

@router.patch("/{employee_id}/password", response_model=UserResponseDTO)
async def change_user_password(
    employee_id: str,
    request: ChangeUserPasswordRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """Change user password."""
    return await controller.change_user_password(employee_id, request, current_user)

@router.patch("/{employee_id}/role", response_model=UserResponseDTO)
async def change_user_role(
    employee_id: str,
    request: ChangeUserRoleRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """Change user role."""
    return await controller.change_user_role(employee_id, request, current_user)

@router.patch("/{employee_id}/status", response_model=UserResponseDTO)
async def update_user_status(
    employee_id: str,
    request: UserStatusUpdateRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """Update user status (activate, deactivate, suspend, etc.)."""
    return await controller.update_user_status(employee_id, request, current_user)

@router.delete("/{employee_id}")
async def delete_user(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Delete/deactivate a user."""
    try:
        # Use controller to deactivate user with organisation context
        request = UserStatusUpdateRequestDTO(status="inactive", reason="Deleted by admin")
        result = await controller.update_user_status(employee_id, request, current_user)
        
        return {
            "success": True,
            "message": "User deactivated successfully",
            "employee_id": result.employee_id,
            "status": result.status,
            "organisation": current_user.hostname,
            "deactivated_at": datetime.now().isoformat(),
            "deactivated_by": current_user.employee_id
        }
    except Exception as e:
        logger.error(f"Error deleting user {employee_id} in organisation {current_user.hostname}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {str(e)}"
        )

# User existence and validation endpoints
@router.get("/check/exists")
async def check_user_exists(
    email: Optional[str] = Query(None, description="Email to check"),
    mobile: Optional[str] = Query(None, description="Mobile number to check"),
    pan_number: Optional[str] = Query(None, description="PAN number to check"),
    exclude_id: Optional[str] = Query(None, description="User ID to exclude from check"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, bool]:
    """Check if user exists with given email, mobile, or PAN."""
    return await controller.check_user_exists(
        email=email,
        mobile=mobile,
        pan_number=pan_number,
        exclude_id=exclude_id,
        current_user=current_user
    )

@router.get("/analytics/statistics", response_model=UserStatisticsDTO)
async def get_user_statistics(
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> UserStatisticsDTO:
    """Get comprehensive user analytics and statistics."""
    return await controller.get_user_statistics(current_user)

# Legacy compatibility endpoints
@router.get("/legacy/all")
async def get_all_users_legacy(
    hostname: str = Query(..., description="Organisation hostname"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> List[Dict[str, Any]]:
    """Get all users for a specific organisation (legacy endpoint)."""
    # Validate user can access the specified organisation
    if current_user.hostname != hostname and not current_user.has_role("superadmin"):
        raise HTTPException(
            status_code=403,
            detail="Access denied: cannot access different organisation"
        )
    
    try:
        # Create a temporary current user context for the requested hostname
        temp_user_data = current_user.token_payload.copy()
        temp_user_data["hostname"] = hostname
        temp_current_user = CurrentUser(temp_user_data)
        
        result = await controller.get_all_users(
            skip=0,
            limit=1000,  # Large limit for legacy compatibility
            include_inactive=False,
            include_deleted=False,
            current_user=temp_current_user
        )
        
        # Convert to legacy format
        return [
            {
                "employee_id": user.employee_id,
                "name": user.name,
                "email": user.email,
                "department": user.department,
                "designation": user.designation,
                "role": user.role,
                "date_of_joining": user.date_of_joining.isoformat() if user.date_of_joining else None,
                "status": user.status,
                "manager_id": user.manager_id,
                "phone": user.mobile,
                "organisation": hostname
            }
            for user in result.users
        ]
    except Exception as e:
        logger.error(f"Error getting legacy users for organisation {hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @router.get("/legacy/{employee_id}")
# async def get_user_by_employee_id_legacy(
#     employee_id: str,
#     hostname: str = Query(..., description="Organisation hostname"),
#     current_user: CurrentUser = Depends(get_current_user),
#     controller: UserController = Depends(get_user_controller)
# ) -> Dict[str, Any]:
#     """Get user by employee ID for specific organisation (legacy endpoint)."""
#     # Validate user can access the specified organisation
#     if current_user.hostname != hostname and not current_user.has_role("superadmin"):
#         raise HTTPException(
#             status_code=403,
#             detail="Access denied: cannot access different organisation"
#         )
    
#     try:
#         # Create a temporary current user context for the requested hostname
#         temp_user_data = current_user.token_payload.copy()
#         temp_user_data["hostname"] = hostname
#         temp_current_user = CurrentUser(temp_user_data)
        
#         user = await controller.get_user_by_id(employee_id, temp_current_user)
#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"User {employee_id} not found in organisation {hostname}"
#             )
        
#         # Convert to legacy format
#         return {
#             "employee_id": user.employee_id,
#             "name": user.name,
#             "email": user.email,
#             "department": user.department,
#             "designation": user.designation,
#             "role": user.role,
#             "date_of_joining": user.date_of_joining.isoformat() if user.date_of_joining else None,
#             "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
#             "gender": user.gender,
#             "mobile": user.mobile,
#             "status": user.status,
#             "manager_id": user.manager_id,
#             "address": user.address,
#             "emergency_contact": user.emergency_contact,
#             "blood_group": user.blood_group,
#             "location": user.location,
#             "pan_number": user.pan_number,
#             "aadhar_number": user.aadhar_number,
#             "uan_number": user.uan_number,
#             "esi_number": user.esi_number,
#             "pan_document_path": user.pan_document_path,
#             "aadhar_document_path": user.aadhar_document_path,
#             "photo_path": user.photo_path,
#             "organisation": hostname,
#             "created_at": user.created_at.isoformat() if user.created_at else None,
#             "updated_at": user.updated_at.isoformat() if user.updated_at else None,
#             "bank_details": user.bank_details or {},
#             "date_of_joining": user.date_of_joining.isoformat() if user.date_of_joining else None,
#             "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
#             "emergency_contact": user.emergency_contact,
#             "blood_group": user.blood_group
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error getting legacy user {employee_id} for organisation {hostname}: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to get user: {str(e)}"
#         )

# # Error Handlers
# @router.exception_handler(ValueError)
# async def value_error_handler(request, exc):
#     """Handle validation errors."""
#     logger.error(f"Validation error: {exc}")
#     return JSONResponse(
#         status_code=400,
#         content={"detail": str(exc)}
#     )

# @router.exception_handler(HTTPException)
# async def http_exception_handler(request, exc):
#     """Handle HTTP exceptions."""
#     logger.error(f"HTTP error: {exc.detail}")
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )

# @router.exception_handler(Exception)
# async def general_exception_handler(request, exc):
#     """Handle general exceptions."""
#     logger.error(f"Unexpected error: {exc}")
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error"}
#     ) 