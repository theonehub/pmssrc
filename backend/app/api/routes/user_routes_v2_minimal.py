"""
Minimal User API Routes (SOLID Architecture)
FastAPI routes for user operations - minimal working version
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, UploadFile, File
from fastapi import status as http_status
from datetime import datetime

# Create router
router = APIRouter(prefix="/api/v2/users", tags=["Users V2"])

# Mock dependency for current user
async def get_current_user():
    """Mock current user dependency."""
    return {"sub": "admin", "role": "admin", "hostname": "company.com"}

# Health check endpoint
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check for user service."""
    return {
        "service": "user_service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-minimal"
    }

# User management endpoints
@router.get("")
async def get_users(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(10, description="Number of records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get all users with pagination.
    Frontend expects this endpoint for dataService.getUsers()
    """
    # Mock users data
    mock_users = [
        {
            "emp_id": "EMP001",
            "name": "John Doe",
            "email": "john.doe@company.com",
            "department": "Engineering",
            "designation": "Software Engineer",
            "role": "user",
            "doj": "2023-01-15",
            "status": "active",
            "manager_id": "EMP003",
            "phone": "9876543210"
        },
        {
            "emp_id": "EMP002",
            "name": "Jane Smith",
            "email": "jane.smith@company.com",
            "department": "HR",
            "designation": "HR Manager",
            "role": "manager",
            "doj": "2022-03-10",
            "status": "active",
            "manager_id": "EMP004",
            "phone": "9876543211"
        },
        {
            "emp_id": "EMP003",
            "name": "Bob Johnson",
            "email": "bob.johnson@company.com",
            "department": "Engineering",
            "designation": "Senior Software Engineer",
            "role": "manager",
            "doj": "2021-06-01",
            "status": "active",
            "manager_id": "EMP004",
            "phone": "9876543212"
        }
    ]
    
    # Apply pagination
    total = len(mock_users)
    paginated_users = mock_users[skip:skip+limit]
    
    return {
        "total": total,
        "users": paginated_users,
        "skip": skip,
        "limit": limit
    }

@router.get("/stats")
async def get_user_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user statistics.
    Frontend expects this endpoint for dataService.getUserStats()
    """
    return {
        "total_users": 25,
        "active_users": 23,
        "inactive_users": 2,
        "departments": {
            "Engineering": 15,
            "HR": 5,
            "Finance": 5
        },
        "roles": {
            "user": 20,
            "manager": 4,
            "admin": 1
        },
        "recent_joiners": 3,
        "generated_at": datetime.now().isoformat()
    }

@router.get("/my/directs")
async def get_my_directs(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get direct reports for current user.
    Frontend expects this endpoint for dataService.getMyDirects()
    """
    # Mock direct reports
    return [
        {
            "emp_id": "EMP001",
            "name": "John Doe",
            "email": "john.doe@company.com",
            "department": "Engineering",
            "designation": "Software Engineer",
            "doj": "2023-01-15",
            "status": "active"
        },
        {
            "emp_id": "EMP002",
            "name": "Jane Smith",
            "email": "jane.smith@company.com",
            "department": "Engineering",
            "designation": "Junior Developer",
            "doj": "2023-06-01",
            "status": "active"
        }
    ]

@router.get("/manager/directs")
async def get_manager_directs(
    manager_id: str = Query(..., description="Manager ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get direct reports for a specific manager.
    Frontend expects this endpoint for dataService.getManagerDirects()
    """
    # Mock manager's direct reports
    return [
        {
            "emp_id": "EMP001",
            "name": "John Doe",
            "email": "john.doe@company.com",
            "department": "Engineering",
            "designation": "Software Engineer",
            "manager_id": manager_id,
            "doj": "2023-01-15",
            "status": "active"
        },
        {
            "emp_id": "EMP002",
            "name": "Jane Smith",
            "email": "jane.smith@company.com",
            "department": "Engineering",
            "designation": "Junior Developer",
            "manager_id": manager_id,
            "doj": "2023-06-01",
            "status": "active"
        }
    ]

@router.get("/me")
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user's profile.
    Frontend expects this endpoint for dataService.getCurrentUser()
    """
    emp_id = current_user.get("sub", "EMP001")
    
    return {
        "emp_id": emp_id,
        "name": "Current User",
        "email": f"{emp_id.lower()}@company.com",
        "department": "Engineering",
        "designation": "Software Engineer",
        "role": current_user.get("role", "user"),
        "doj": "2023-01-15",
        "status": "active",
        "manager_id": "EMP003",
        "phone": "9876543210",
        "address": "123 Main St, City, State",
        "emergency_contact": "9876543211",
        "blood_group": "O+",
        "profile_picture": None
    }

@router.post("/create")
async def create_user(
    user_data: Dict[str, Any] = Body(..., description="User creation data"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new user.
    Frontend expects this endpoint for dataService.createUser()
    """
    # Mock user creation
    new_emp_id = f"EMP{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "success": True,
        "message": "User created successfully",
        "emp_id": new_emp_id,
        "name": user_data.get("name"),
        "email": user_data.get("email"),
        "department": user_data.get("department"),
        "designation": user_data.get("designation"),
        "created_at": datetime.now().isoformat(),
        "created_by": current_user.get("sub", "system")
    }

@router.post("/import")
async def import_users(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Import users from file.
    Frontend expects this endpoint for dataService.importUsers()
    """
    # Mock import response
    return {
        "success": True,
        "message": "Users imported successfully",
        "imported_count": 10,
        "failed_count": 0,
        "imported_at": datetime.now().isoformat(),
        "imported_by": current_user.get("sub", "system")
    }

@router.put("/{emp_id}")
async def update_user(
    emp_id: str = Path(..., description="Employee ID"),
    user_data: Dict[str, Any] = Body(..., description="Updated user data"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update user information.
    """
    # Mock user update
    return {
        "success": True,
        "message": "User updated successfully",
        "emp_id": emp_id,
        "updated_fields": list(user_data.keys()),
        "updated_at": datetime.now().isoformat(),
        "updated_by": current_user.get("sub", "system")
    }

@router.delete("/{emp_id}")
async def delete_user(
    emp_id: str = Path(..., description="Employee ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete/deactivate a user.
    """
    # Mock user deletion (soft delete)
    return {
        "success": True,
        "message": "User deactivated successfully",
        "emp_id": emp_id,
        "status": "inactive",
        "deactivated_at": datetime.now().isoformat(),
        "deactivated_by": current_user.get("sub", "system")
    }

@router.get("/{emp_id}")
async def get_user_by_id(
    emp_id: str = Path(..., description="Employee ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user by employee ID.
    """
    # Mock user data
    return {
        "emp_id": emp_id,
        "name": "John Doe",
        "email": "john.doe@company.com",
        "department": "Engineering",
        "designation": "Software Engineer",
        "role": "user",
        "doj": "2023-01-15",
        "status": "active",
        "phone": "9876543210",
        "last_updated": datetime.now().isoformat()
    } 