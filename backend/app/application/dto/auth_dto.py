"""
Authentication Application Layer DTOs
Data Transfer Objects for authentication operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import datetime


# ==================== REQUEST DTOs ====================

class LoginRequestDTO(BaseModel):
    """Request DTO for user login"""
    username: str = Field(..., min_length=1, max_length=50, description="Employee ID or username")
    password: str = Field(..., min_length=1, max_length=100, description="User password")
    hostname: str = Field(..., min_length=1, max_length=100, description="Organization hostname")
    remember_me: bool = False
    
    @validator('username')
    def validate_username(cls, v):
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError("Password cannot be empty")
        return v
    
    @validator('hostname')
    def validate_hostname(cls, v):
        if not v.strip():
            raise ValueError("Hostname cannot be empty")
        return v.strip().lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "EMP001",
                "password": "securepassword123",
                "hostname": "company.com",
                "remember_me": False
            }
        }


class RefreshTokenRequestDTO(BaseModel):
    """Request DTO for token refresh"""
    refresh_token: str = Field(..., min_length=1, description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class LogoutRequestDTO(BaseModel):
    """Request DTO for user logout"""
    token: Optional[str] = Field(None, description="Access token to invalidate")
    logout_all_devices: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "logout_all_devices": False
            }
        }


class PasswordChangeRequestDTO(BaseModel):
    """Request DTO for password change"""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    confirm_password: str = Field(..., min_length=8, max_length=100, description="Confirm new password")
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError("Passwords do not match")
        return v
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "NewSecurePass123",
                "confirm_password": "NewSecurePass123"
            }
        }


class PasswordResetRequestDTO(BaseModel):
    """Request DTO for password reset initiation"""
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="User email address")
    hostname: str = Field(..., min_length=1, max_length=100, description="Organization hostname")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@company.com",
                "hostname": "company.com"
            }
        }


class PasswordResetConfirmRequestDTO(BaseModel):
    """Request DTO for password reset confirmation"""
    reset_token: str = Field(..., min_length=1, description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    confirm_password: str = Field(..., min_length=8, max_length=100, description="Confirm new password")
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError("Passwords do not match")
        return v
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "reset_token": "abc123def456ghi789",
                "new_password": "NewSecurePass123",
                "confirm_password": "NewSecurePass123"
            }
        }


# ==================== RESPONSE DTOs ====================

class TokenResponseDTO(BaseModel):
    """Response DTO for token operations"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    issued_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "def456ghi789jkl012...",
                "scope": "read write",
                "issued_at": "2024-01-01T12:00:00"
            }
        }


class LoginResponseDTO(BaseModel):
    """Response DTO for successful login"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    refresh_token: Optional[str] = None
    user_info: Dict[str, Any]
    permissions: List[str]
    last_login: Optional[datetime] = None
    login_time: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_info": {
                    "emp_id": "EMP001",
                    "name": "John Doe",
                    "email": "john.doe@company.com",
                    "role": "user",
                    "department": "Engineering"
                },
                "permissions": ["read_profile", "write_profile"],
                "login_time": "2024-01-01T12:00:00"
            }
        }


class LogoutResponseDTO(BaseModel):
    """Response DTO for logout operation"""
    message: str
    logged_out_at: datetime
    session_duration: Optional[int] = None  # seconds
    devices_logged_out: int = 1
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Successfully logged out",
                "logged_out_at": "2024-01-01T15:30:00",
                "session_duration": 12600,
                "devices_logged_out": 1
            }
        }


class PasswordChangeResponseDTO(BaseModel):
    """Response DTO for password change operation"""
    message: str
    changed_at: datetime
    requires_reauth: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Password changed successfully",
                "changed_at": "2024-01-01T14:00:00",
                "requires_reauth": True
            }
        }


class PasswordResetResponseDTO(BaseModel):
    """Response DTO for password reset initiation"""
    message: str
    reset_token_sent: bool
    expires_in: int  # seconds
    sent_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Password reset email sent",
                "reset_token_sent": True,
                "expires_in": 3600,
                "sent_at": "2024-01-01T12:00:00"
            }
        }


class TokenValidationResponseDTO(BaseModel):
    """Response DTO for token validation"""
    is_valid: bool
    user_info: Optional[Dict[str, Any]] = None
    permissions: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    token_type: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "user_info": {
                    "emp_id": "EMP001",
                    "role": "user",
                    "hostname": "company.com"
                },
                "permissions": ["read_profile"],
                "expires_at": "2024-01-01T16:00:00",
                "token_type": "bearer"
            }
        }


class UserProfileResponseDTO(BaseModel):
    """Response DTO for user profile information"""
    emp_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    department: Optional[str] = None
    position: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    permissions: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "emp_id": "EMP001",
                "username": "john.doe",
                "email": "john.doe@company.com",
                "full_name": "John Doe",
                "role": "user",
                "department": "Engineering",
                "position": "Software Developer",
                "is_active": True,
                "last_login": "2024-01-01T12:00:00",
                "permissions": ["read_profile", "write_profile"]
            }
        }


class SessionInfoResponseDTO(BaseModel):
    """Response DTO for session information"""
    session_id: str
    user_info: Dict[str, Any]
    login_time: datetime
    last_activity: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_123456789",
                "user_info": {
                    "emp_id": "EMP001",
                    "role": "user"
                },
                "login_time": "2024-01-01T12:00:00",
                "last_activity": "2024-01-01T14:30:00",
                "expires_at": "2024-01-01T16:00:00",
                "ip_address": "192.168.1.100",
                "is_active": True
            }
        }


class AuthHealthResponseDTO(BaseModel):
    """Response DTO for authentication health check"""
    service: str
    status: str
    timestamp: datetime
    jwt_service_status: str
    password_service_status: str
    user_service_status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "service": "auth_service",
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00",
                "jwt_service_status": "healthy",
                "password_service_status": "healthy",
                "user_service_status": "healthy"
            }
        }


# ==================== ERROR DTOs ====================

class AuthErrorResponseDTO(BaseModel):
    """Response DTO for authentication errors"""
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    retry_after: Optional[int] = None  # seconds
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "INVALID_CREDENTIALS",
                "error_message": "Invalid username or password",
                "timestamp": "2024-01-01T12:00:00",
                "retry_after": 60
            }
        }
