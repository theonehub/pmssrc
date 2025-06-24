"""
Authentication Dependencies
Provides authentication and authorization dependencies with hostname-based organisation segregation
"""

import logging
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.jwt_handler import decode_access_token
from app.utils.logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer scheme for token extraction
security = HTTPBearer()


class CurrentUser:
    """
    Current user information with organisation context.
    """
    def __init__(self, token_payload: Dict[str, Any]):
        self.employee_id = token_payload.get("employee_id") or token_payload.get("sub")
        self.username = token_payload.get("username")
        self.role = token_payload.get("role", "user")
        self.hostname = token_payload.get("hostname")
        self.permissions = token_payload.get("permissions", [])
        self.token_payload = token_payload
    
    @property
    def organisation_id(self) -> str:
        """Get organisation ID based on hostname."""
        return self.hostname
    
    @property
    def database_name(self) -> str:
        """Get database name for organisation."""
        if self.hostname:
            return f"pms_{self.hostname}"
        return "pms_global_database"
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return self.role.lower() == role.lower()
    
    def can_access_organisation(self, hostname: Optional[str] = None) -> bool:
        """Check if user can access specific organisation."""
        if hostname is None:
            return True
        return self.hostname == hostname


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Extract current user from JWT token with organisation context.
    
    Args:
        credentials: HTTP Authorization credentials containing JWT token
        
    Returns:
        CurrentUser: Current user with organisation context
        
    Raises:
        HTTPException: If token is invalid or missing required claims
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Decode JWT token
        payload = decode_access_token(token)
        
        # Validate required claims
        if not payload.get("hostname"):
            logger.warning("Token missing hostname claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing organisation context",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not (payload.get("employee_id") or payload.get("sub")):
            logger.warning("Token missing user identifier")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identifier",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create current user object
        current_user = CurrentUser(payload)
        
        logger.info(f"Authenticated user: {current_user.employee_id} from organisation: {current_user.hostname}")
        
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[CurrentUser]:
    """
    Extract current user from JWT token (optional).
    
    Args:
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        Optional[CurrentUser]: Current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function
    """
    async def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_role(required_role):
            logger.warning(f"Access denied: user {current_user.employee_id} lacks required role {required_role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {required_role} role required"
            )
        return current_user
    
    return role_checker


def require_permission(required_permission: str):
    """
    Dependency factory for permission-based access control.
    
    Args:
        required_permission: Required permission
        
    Returns:
        Dependency function
    """
    async def permission_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_permission(required_permission):
            logger.warning(f"Access denied: user {current_user.employee_id} lacks permission {required_permission}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {required_permission} permission required"
            )
        return current_user
    
    return permission_checker


def require_organisation_access(hostname: Optional[str] = None):
    """
    Dependency factory for organisation-based access control.
    
    Args:
        hostname: Required organisation hostname (None for any organisation)
        
    Returns:
        Dependency function
    """
    async def organisation_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.can_access_organisation(hostname):
            logger.warning(f"Access denied: user {current_user.employee_id} cannot access organisation {hostname}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient organisation permissions"
            )
        return current_user
    
    return organisation_checker


# Common role dependencies
require_admin = require_role("admin")
require_manager = require_role("manager")
require_hr = require_role("hr")
require_superadmin = require_role("superadmin")

# Common permission dependencies
require_read_all = require_permission("read_all")
require_write_all = require_permission("write_all")
require_manage_users = require_permission("manage_users")
require_manage_payroll = require_permission("manage_payroll") 