"""
SOLID-Compliant Auth Routes v2
Clean architecture implementation of authentication HTTP endpoints
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime

from app.api.controllers.auth_controller import AuthController
from app.application.dto.auth_dto import (
    LoginRequestDTO, RefreshTokenRequestDTO, LogoutRequestDTO,
    PasswordChangeRequestDTO, PasswordResetRequestDTO, PasswordResetConfirmRequestDTO,
    LoginResponseDTO, TokenResponseDTO, LogoutResponseDTO, PasswordChangeResponseDTO,
    PasswordResetResponseDTO, TokenValidationResponseDTO, UserProfileResponseDTO,
    SessionInfoResponseDTO, AuthHealthResponseDTO
)
# from app.auth.auth import get_current_user
# from app.infrastructure.auth.oauth2_forms import OAuth2PasswordRequestFormWithHost

# Mock dependencies for compilation
async def get_current_user():
    """Mock current user dependency."""
    return {"sub": "admin", "role": "admin", "hostname": "company.com"}

class OAuth2PasswordRequestFormWithHost:
    """Mock OAuth2 form for compilation."""
    def __init__(self, username: str = "admin", password: str = "admin123", hostname: str = "company.com"):
        self.username = username
        self.password = password
        self.hostname = hostname

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/auth", tags=["auth-v2"])

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login")

# Dependency for auth controller
async def get_auth_controller() -> AuthController:
    """Get auth controller instance."""
    return AuthController()

# Health check endpoint
@router.get("/health", response_model=AuthHealthResponseDTO)
async def health_check(
    controller: AuthController = Depends(get_auth_controller)
) -> AuthHealthResponseDTO:
    """Health check for authentication service."""
    return await controller.health_check()

# Authentication endpoints
@router.post("/login", response_model=LoginResponseDTO)
async def login(
    request: LoginRequestDTO,
    controller: AuthController = Depends(get_auth_controller)
) -> LoginResponseDTO:
    """
    User login endpoint.
    
    Args:
        request: Login request with credentials
        controller: Auth controller dependency
        
    Returns:
        Login response with token and user info
    """
    try:
        logger.info(f"Login request for user: {request.username} @ {request.hostname}")
        
        result = await controller.login(request)
        
        return result
        
    except ValueError as e:
        logger.warning(f"Login failed for user {request.username}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Login error for user {request.username}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login/form", response_model=LoginResponseDTO)
async def login_form(
    form_data: OAuth2PasswordRequestFormWithHost = Depends(),
    controller: AuthController = Depends(get_auth_controller)
) -> LoginResponseDTO:
    """
    Legacy form-based login endpoint (OAuth2 compatible).
    
    Args:
        form_data: OAuth2 form data with hostname
        controller: Auth controller dependency
        
    Returns:
        Login response with token and user info
    """
    try:
        logger.info(f"Form login request for user: {form_data.username}")
        
        # Convert form data to DTO
        request = LoginRequestDTO(
            username=form_data.username,
            password=form_data.password,
            hostname=form_data.hostname,
            remember_me=False
        )
        
        result = await controller.login(request)
        
        return result
        
    except ValueError as e:
        logger.warning(f"Form login failed for user {form_data.username}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Form login error for user {form_data.username}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/logout", response_model=LogoutResponseDTO)
async def logout(
    request: LogoutRequestDTO,
    controller: AuthController = Depends(get_auth_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> LogoutResponseDTO:
    """
    User logout endpoint.
    
    Args:
        request: Logout request
        controller: Auth controller dependency
        current_user: Current authenticated user
        
    Returns:
        Logout response
    """
    try:
        logger.info(f"Logout request for user: {current_user.get('sub')}")
        
        result = await controller.logout(request, current_user)
        
        return result
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout/simple", response_model=LogoutResponseDTO)
async def logout_simple(
    controller: AuthController = Depends(get_auth_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> LogoutResponseDTO:
    """
    Simple logout endpoint (no request body required).
    
    Args:
        controller: Auth controller dependency
        current_user: Current authenticated user
        
    Returns:
        Logout response
    """
    # Create simple logout request
    request = LogoutRequestDTO(logout_all_devices=False)
    
    return await controller.logout(request, current_user)

# Token management endpoints
@router.post("/refresh", response_model=TokenResponseDTO)
async def refresh_token(
    request: RefreshTokenRequestDTO,
    controller: AuthController = Depends(get_auth_controller)
) -> TokenResponseDTO:
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        controller: Auth controller dependency
        
    Returns:
        New token response
    """
    try:
        logger.info("Token refresh request")
        
        result = await controller.refresh_token(request)
        
        return result
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=400, detail="Invalid refresh token")

@router.post("/validate", response_model=TokenValidationResponseDTO)
async def validate_token(
    authorization: Optional[str] = Header(None),
    controller: AuthController = Depends(get_auth_controller)
) -> TokenValidationResponseDTO:
    """
    Validate access token.
    
    Args:
        authorization: Authorization header with Bearer token
        controller: Auth controller dependency
        
    Returns:
        Token validation response
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return TokenValidationResponseDTO(is_valid=False)
        
        token = authorization.split(" ")[1]
        result = await controller.validate_token(token)
        
        return result
        
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return TokenValidationResponseDTO(is_valid=False)

# Password management endpoints
@router.post("/change-password", response_model=PasswordChangeResponseDTO)
async def change_password(
    request: PasswordChangeRequestDTO,
    controller: AuthController = Depends(get_auth_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> PasswordChangeResponseDTO:
    """
    Change user password.
    
    Args:
        request: Password change request
        controller: Auth controller dependency
        current_user: Current authenticated user
        
    Returns:
        Password change response
    """
    try:
        logger.info(f"Password change request for user: {current_user.get('sub')}")
        
        result = await controller.change_password(request, current_user)
        
        return result
        
    except ValueError as e:
        logger.warning(f"Password change failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-password", response_model=PasswordResetResponseDTO)
async def request_password_reset(
    request: PasswordResetRequestDTO,
    controller: AuthController = Depends(get_auth_controller)
) -> PasswordResetResponseDTO:
    """
    Initiate password reset process.
    
    Args:
        request: Password reset request
        controller: Auth controller dependency
        
    Returns:
        Password reset response
    """
    try:
        logger.info(f"Password reset request for email: {request.email}")
        
        result = await controller.request_password_reset(request)
        
        return result
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-password/confirm", response_model=PasswordChangeResponseDTO)
async def confirm_password_reset(
    request: PasswordResetConfirmRequestDTO,
    controller: AuthController = Depends(get_auth_controller)
) -> PasswordChangeResponseDTO:
    """
    Confirm password reset with token.
    
    Args:
        request: Password reset confirmation request
        controller: Auth controller dependency
        
    Returns:
        Password change response
    """
    try:
        logger.info("Password reset confirmation request")
        
        result = await controller.confirm_password_reset(request)
        
        return result
        
    except ValueError as e:
        logger.warning(f"Password reset confirmation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Password reset confirmation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User profile endpoints
@router.get("/me", response_model=UserProfileResponseDTO)
async def get_current_user_profile(
    controller: AuthController = Depends(get_auth_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserProfileResponseDTO:
    """
    Get current user profile information.
    
    Args:
        controller: Auth controller dependency
        current_user: Current authenticated user
        
    Returns:
        User profile response
    """
    try:
        logger.info(f"Profile request for user: {current_user.get('sub')}")
        
        result = await controller.get_current_user_profile(current_user)
        
        return result
        
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session", response_model=SessionInfoResponseDTO)
async def get_session_info(
    controller: AuthController = Depends(get_auth_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    authorization: str = Header(...)
) -> SessionInfoResponseDTO:
    """
    Get current session information.
    
    Args:
        controller: Auth controller dependency
        current_user: Current authenticated user
        authorization: Authorization header with Bearer token
        
    Returns:
        Session info response
    """
    try:
        logger.info(f"Session info request for user: {current_user.get('sub')}")
        
        # Extract token from authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=400, detail="Invalid authorization header")
        
        token = authorization.split(" ")[1]
        result = await controller.get_session_info(current_user, token)
        
        return result
        
    except Exception as e:
        logger.error(f"Get session info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility endpoints
@router.get("/permissions")
async def get_current_user_permissions(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user permissions.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User permissions
    """
    try:
        controller = AuthController()
        permissions = controller._get_user_permissions(current_user.get("role", ""))
        
        return {
            "user_id": current_user.get("sub"),
            "role": current_user.get("role"),
            "permissions": permissions,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get permissions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/whoami")
async def whoami(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Quick endpoint to check current authenticated user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Basic user info
    """
    return {
        "emp_id": current_user.get("sub"),
        "role": current_user.get("role"),
        "hostname": current_user.get("hostname"),
        "authenticated": True,
        "timestamp": datetime.now().isoformat()
    }

# Note: Exception handlers would be registered at the app level, not router level
# These are commented out for now as they require app-level registration

# async def value_error_handler(request, exc):
#     """Handle validation errors."""
#     logger.error(f"Validation error: {exc}")
#     raise HTTPException(status_code=400, detail=str(exc))

# async def http_exception_handler(request, exc):
#     """Handle HTTP exceptions."""
#     logger.error(f"HTTP error: {exc.detail}")
#     raise exc

# async def general_exception_handler(request, exc):
#     """Handle general exceptions."""
#     logger.error(f"Unexpected error: {exc}", exc_info=True)
#     raise HTTPException(status_code=500, detail="Internal server error")
