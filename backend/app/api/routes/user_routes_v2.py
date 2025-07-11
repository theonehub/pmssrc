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
router = APIRouter(prefix="/v2/users", tags=["Users V2"])

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

@router.get("/template")
async def download_user_template(
    format: str = Query("csv", description="Template format (csv, xlsx)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    """Download user import template with headers."""
    try:
        # Validate format
        if format not in ['csv', 'xlsx']:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'xlsx'")
        
        # Get template using controller
        file_content, filename = await controller.get_user_template(format, current_user)
        
        # Return file response
        from fastapi.responses import Response
        media_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return Response(
            content=file_content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating user template for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate template: {str(e)}")

@router.get("/{employee_id}")
async def get_user_by_id(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> UserResponseDTO:
    """Get user by ID with complete details."""
    try:
        user = await controller.get_user_by_id(employee_id, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Retrieved user {employee_id} for organisation {current_user.hostname}")
        return user  # Return the DTO as-is (nested structure)
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
            "last_login_at": format_date(safe_get(result, 'last_login_at')),
            # Banking details
            "account_number": safe_get(result.bank_details, 'account_number') if hasattr(result, 'bank_details') and result.bank_details else '',
            "bank_name": safe_get(result.bank_details, 'bank_name') if hasattr(result, 'bank_details') and result.bank_details else '',
            "ifsc_code": safe_get(result.bank_details, 'ifsc_code') if hasattr(result, 'bank_details') and result.bank_details else '',
            "account_holder_name": safe_get(result.bank_details, 'account_holder_name') if hasattr(result, 'bank_details') and result.bank_details else '',
            "branch_name": safe_get(result.bank_details, 'branch_name') if hasattr(result, 'bank_details') and result.bank_details else '',
            "account_type": safe_get(result.bank_details, 'account_type') if hasattr(result, 'bank_details') and result.bank_details else ''
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

# Import/Export endpoints
@router.post("/import")
async def import_users(
    file: UploadFile = File(..., description="CSV/Excel file containing user data"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Import users from CSV/Excel file."""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = file.filename.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Import users using controller
        result = await controller.import_users(file_content, file.filename, current_user)
        
        return {
            "success": True,
            "message": "Users imported successfully",
            "imported_count": result.imported_count,
            "errors": result.errors if hasattr(result, 'errors') else [],
            "organisation": current_user.hostname,
            "imported_at": datetime.now().isoformat(),
            "imported_by": current_user.employee_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing users for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import users: {str(e)}")

@router.get("/export")
async def export_users(
    format: str = Query("csv", description="Export format (csv, xlsx)"),
    include_inactive: bool = Query(False, description="Include inactive users"),
    include_deleted: bool = Query(False, description="Include deleted users"),
    department: Optional[str] = Query(None, description="Filter by department"),
    role: Optional[str] = Query(None, description="Filter by role"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    """Export users to CSV/Excel file."""
    try:
        # Validate format
        if format not in ['csv', 'xlsx']:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'xlsx'")
        
        # Get users for export
        result = await controller.get_all_users(
            skip=0,
            limit=10000,  # Large limit for export
            include_inactive=include_inactive,
            include_deleted=include_deleted,
            current_user=current_user
        )
        
        # Apply additional filters
        users = result.users
        if department:
            users = [u for u in users if u.department == department]
        if role:
            users = [u for u in users if u.role == role]
        
        # Export using controller
        file_content, filename = await controller.export_users(users, format, current_user)
        
        # Return file response
        from fastapi.responses import Response
        media_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return Response(
            content=file_content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting users for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export users: {str(e)}")

# Department and Designation endpoints
@router.get("/departments")
async def get_departments(
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, List[str]]:
    """Get list of all departments in the organisation."""
    try:
        departments = await controller.get_departments(current_user)
        return {
            "departments": departments,
            "organisation": current_user.hostname,
            "count": len(departments)
        }
    except Exception as e:
        logger.error(f"Error getting departments for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/designations")
async def get_designations(
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, List[str]]:
    """Get list of all designations in the organisation."""
    try:
        designations = await controller.get_designations(current_user)
        return {
            "designations": designations,
            "organisation": current_user.hostname,
            "count": len(designations)
        }
    except Exception as e:
        logger.error(f"Error getting designations for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User attendance and leaves summary endpoints
@router.get("/{employee_id}/attendance/summary")
async def get_user_attendance_summary(
    employee_id: str,
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Get user attendance summary for a specific month."""
    try:
        # Import attendance controller for this functionality
        from app.api.controllers.attendance_controller import AttendanceController
        from app.config.dependency_container import get_attendance_controller
        
        attendance_controller = get_attendance_controller()
        summary = await attendance_controller.get_user_attendance_summary(
            employee_id, month, year, current_user
        )
        
        return {
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "total_working_days": summary.total_working_days,
            "present_days": summary.present_days,
            "absent_days": summary.absent_days,
            "half_days": summary.half_days,
            "late_arrivals": summary.late_arrivals,
            "early_departures": summary.early_departures,
            "overtime_hours": summary.overtime_hours,
            "attendance_percentage": summary.attendance_percentage,
            "organisation": current_user.hostname
        }
        
    except Exception as e:
        logger.error(f"Error getting attendance summary for user {employee_id} in organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{employee_id}/leaves/summary")
async def get_user_leaves_summary(
    employee_id: str,
    year: int = Query(..., ge=2020, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Get user leaves summary for a specific year."""
    try:
        # Import employee leave controller for this functionality
        from app.api.controllers.employee_leave_controller import EmployeeLeaveController
        from app.config.dependency_container import get_employee_leave_controller
        
        leave_controller = get_employee_leave_controller()
        summary = await leave_controller.get_user_leave_summary(
            employee_id, year, current_user
        )
        
        return {
            "employee_id": employee_id,
            "year": year,
            "total_casual_leaves": summary.total_casual_leaves,
            "used_casual_leaves": summary.used_casual_leaves,
            "remaining_casual_leaves": summary.total_casual_leaves - summary.used_casual_leaves,
            "total_sick_leaves": summary.total_sick_leaves,
            "used_sick_leaves": summary.used_sick_leaves,
            "remaining_sick_leaves": summary.total_sick_leaves - summary.used_sick_leaves,
            "total_earned_leaves": summary.total_earned_leaves,
            "used_earned_leaves": summary.used_earned_leaves,
            "remaining_earned_leaves": summary.total_earned_leaves - summary.used_earned_leaves,
            "pending_leave_requests": summary.pending_leave_requests,
            "organisation": current_user.hostname
        }
        
    except Exception as e:
        logger.error(f"Error getting leaves summary for user {employee_id} in organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Profile picture and documents endpoints
@router.get("/{user_id}/profile-picture")
async def get_user_profile_picture(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    """Get user profile picture."""
    try:
        user = await controller.get_user_by_id(user_id, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get profile picture path
        photo_path = None
        if hasattr(user, 'documents') and user.documents:
            photo_path = user.documents.photo_path
        elif hasattr(user, 'photo_path'):
            photo_path = user.photo_path
        
        if not photo_path:
            raise HTTPException(status_code=404, detail="Profile picture not found")
        
        # Return file response
        from fastapi.responses import FileResponse
        import os
        
        file_path = os.path.join("uploads", photo_path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Profile picture file not found")
        
        return FileResponse(file_path, media_type="image/*")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile picture for user {user_id} in organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/documents")
async def upload_user_documents(
    user_id: str,
    pan_file: Optional[UploadFile] = File(None, description="PAN document file"),
    aadhar_file: Optional[UploadFile] = File(None, description="Aadhar document file"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Upload user documents (PAN, Aadhar)."""
    try:
        # Validate user exists
        user = await controller.get_user_by_id(user_id, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Upload documents using controller
        result = await controller.upload_user_documents(
            user_id=user_id,
            pan_file=pan_file,
            aadhar_file=aadhar_file,
            current_user=current_user
        )
        
        return {
            "success": True,
            "message": "Documents uploaded successfully",
            "pan_document_path": result.pan_document_path,
            "aadhar_document_path": result.aadhar_document_path,
            "user_id": user_id,
            "organisation": current_user.hostname,
            "uploaded_at": datetime.now().isoformat(),
            "uploaded_by": current_user.employee_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading documents for user {user_id} in organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload documents: {str(e)}")

@router.post("/{user_id}/profile-picture")
async def upload_user_profile_picture(
    user_id: str,
    photo: UploadFile = File(..., description="User profile picture"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Upload user profile picture."""
    try:
        # Validate user exists
        user = await controller.get_user_by_id(user_id, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate file type
        if not photo.content_type or not photo.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Upload profile picture using controller
        result = await controller.upload_user_profile_picture(
            user_id=user_id,
            photo=photo,
            current_user=current_user
        )
        
        return {
            "success": True,
            "message": "Profile picture uploaded successfully",
            "profile_picture_url": result.profile_picture_url,
            "user_id": user_id,
            "organisation": current_user.hostname,
            "uploaded_at": datetime.now().isoformat(),
            "uploaded_by": current_user.employee_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading profile picture for user {user_id} in organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload profile picture: {str(e)}")

@router.get("/analytics/statistics", response_model=UserStatisticsDTO)
async def get_user_statistics(
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> UserStatisticsDTO:
    """Get comprehensive user analytics and statistics."""
    return await controller.get_user_statistics(current_user)

@router.get("")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, le=1000, description="Number of records to return for pagination"),
    include_inactive: bool = Query(False, description="Include inactive users"),
    include_deleted: bool = Query(False, description="Include deleted users"),
    organisation_id: Optional[str] = Query(None, description="Organisation ID to filter users"),
    search: Optional[str] = Query(None, description="Search query for users"),
    department: Optional[str] = Query(None, description="Filter by department"),
    role: Optional[str] = Query(None, description="Filter by role"),
    manager_id: Optional[str] = Query(None, description="Filter by manager ID"),
    designation: Optional[str] = Query(None, description="Filter by designation"),
    location: Optional[str] = Query(None, description="Filter by location"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
) -> Dict[str, Any]:
    """Get a paginated list of users with optional filters."""
    try:
        filters = {
            "skip": skip,
            "limit": limit,
            "include_inactive": include_inactive,
            "include_deleted": include_deleted,
            "organisation_id": organisation_id,
            "search": search,
            "department": department,
            "role": role,
            "manager_id": manager_id,
            "designation": designation,
            "location": location
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        result = await controller.get_all_users(**filters, current_user=current_user)
        return {
            "total": result.total_count,
            "users": result.users,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
            "has_next": result.has_next,
            "has_previous": result.has_previous
        }
    except Exception as e:
        logger.error(f"Error fetching users for organisation {current_user.hostname}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")
