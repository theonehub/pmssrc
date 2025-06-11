"""
User DTOs (Data Transfer Objects)
Request and response DTOs for user operations with validation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator, EmailStr

from app.domain.entities.user import User


# Request DTOs
class CreateUserRequestDTO(BaseModel):
    """DTO for creating a new user."""
    
    employee_id: str = Field(..., min_length=1, max_length=50, description="Employee ID")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    roles: Optional[List[str]] = Field(default=[], description="User roles")
    permissions: Optional[List[str]] = Field(default=[], description="User permissions")
    is_active: bool = Field(default=True, description="Whether user is active")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, underscores, and hyphens')
        return v.lower()
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if not v.strip():
            raise ValueError('Employee ID cannot be empty')
        return v.strip()
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip()


class UpdateUserRequestDTO(BaseModel):
    """DTO for updating user information."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    email: Optional[EmailStr] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name")
    roles: Optional[List[str]] = Field(None, description="User roles")
    permissions: Optional[List[str]] = Field(None, description="User permissions")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username must contain only letters, numbers, underscores, and hyphens')
            return v.lower()
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip() if v is not None else v


class ChangePasswordRequestDTO(BaseModel):
    """DTO for changing user password."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def validate_password_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class LoginRequestDTO(BaseModel):
    """DTO for user login."""
    
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(default=False, description="Remember login")


class UserSearchFiltersDTO(BaseModel):
    """DTO for user search filters."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Page size")
    search: Optional[str] = Field(None, description="Search term")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    roles: Optional[List[str]] = Field(None, description="Filter by roles")
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc/desc)")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


# Response DTOs
class UserResponseDTO(BaseModel):
    """DTO for user response."""
    
    id: str
    employee_id: str
    username: str
    email: str
    full_name: str
    roles: List[str]
    permissions: List[str]
    is_active: bool
    is_superuser: bool
    last_login: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    @classmethod
    def from_entity(cls, entity: User) -> 'UserResponseDTO':
        """Create DTO from domain entity."""
        return cls(
            id=str(entity.id.value),
            employee_id=entity.employee_id,
            username=entity.username,
            email=entity.email.value,
            full_name=entity.full_name,
            roles=entity.roles,
            permissions=entity.permissions,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
            last_login=entity.last_login.isoformat() if entity.last_login else None,
            created_at=entity.created_at.isoformat() if entity.created_at else None,
            updated_at=entity.updated_at.isoformat() if entity.updated_at else None,
            created_by=entity.created_by,
            updated_by=entity.updated_by
        )


class UserSummaryDTO(BaseModel):
    """DTO for user summary (for lists)."""
    
    id: str
    employee_id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    roles: List[str]
    created_at: Optional[str] = None
    
    @classmethod
    def from_entity(cls, entity: User) -> 'UserSummaryDTO':
        """Create DTO from domain entity."""
        return cls(
            id=str(entity.id.value),
            employee_id=entity.employee_id,
            username=entity.username,
            email=entity.email.value,
            full_name=entity.full_name,
            is_active=entity.is_active,
            roles=entity.roles,
            created_at=entity.created_at.isoformat() if entity.created_at else None
        )


class UserListResponseDTO(BaseModel):
    """DTO for paginated user list response."""
    
    users: List[UserSummaryDTO]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class LoginResponseDTO(BaseModel):
    """DTO for login response."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponseDTO


class UserProfileDTO(BaseModel):
    """DTO for user profile information."""
    
    id: str
    employee_id: str
    username: str
    email: str
    full_name: str
    roles: List[str]
    permissions: List[str]
    is_active: bool
    last_login: Optional[str] = None
    
    @classmethod
    def from_entity(cls, entity: User) -> 'UserProfileDTO':
        """Create DTO from domain entity."""
        return cls(
            id=str(entity.id.value),
            employee_id=entity.employee_id,
            username=entity.username,
            email=entity.email.value,
            full_name=entity.full_name,
            roles=entity.roles,
            permissions=entity.permissions,
            is_active=entity.is_active,
            last_login=entity.last_login.isoformat() if entity.last_login else None
        )


# Validation DTOs
@dataclass
class UserValidationResultDTO:
    """DTO for user validation results."""
    
    is_valid: bool
    errors: List[str]
    
    @classmethod
    def success(cls) -> 'UserValidationResultDTO':
        """Create successful validation result."""
        return cls(is_valid=True, errors=[])
    
    @classmethod
    def failure(cls, errors: List[str]) -> 'UserValidationResultDTO':
        """Create failed validation result."""
        return cls(is_valid=False, errors=errors) 