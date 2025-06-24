"""
Authentication Dependencies
FastAPI dependencies for authentication and authorization
"""

import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.auth_integration import get_current_user_dict, verify_token

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        User dictionary with employee_id, hostname, role, etc.
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        user = await get_current_user_dict(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_role(required_role: str, current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Require a specific role for access.
    
    Args:
        required_role: Required role for access
        current_user: Current user from authentication
        
    Returns:
        User role if authorized
        
    Raises:
        HTTPException: If user doesn't have required role
    """
    user_role = current_user.get("role", "").upper()
    required_role = required_role.upper()
    
    if user_role != required_role:
        logger.warning(f"User {current_user.get('employee_id')} with role {user_role} attempted to access {required_role} endpoint")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: {required_role}"
        )
    
    return user_role


async def require_superadmin(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Require superadmin role for access.
    
    Args:
        current_user: Current user from authentication
        
    Returns:
        User role if authorized
        
    Raises:
        HTTPException: If user is not superadmin
    """
    return await require_role("SUPERADMIN", current_user)


async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Require admin role for access.
    
    Args:
        current_user: Current user from authentication
        
    Returns:
        User role if authorized
        
    Raises:
        HTTPException: If user is not admin
    """
    return await require_role("ADMIN", current_user)


async def require_hr(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Require HR role for access.
    
    Args:
        current_user: Current user from authentication
        
    Returns:
        User role if authorized
        
    Raises:
        HTTPException: If user is not HR
    """
    return await require_role("HR", current_user)


async def require_employee(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Require employee role for access.
    
    Args:
        current_user: Current user from authentication
        
    Returns:
        User role if authorized
        
    Raises:
        HTTPException: If user is not employee
    """
    return await require_role("EMPLOYEE", current_user)


async def require_any_role(
    allowed_roles: list[str], 
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    Require any of the specified roles for access.
    
    Args:
        allowed_roles: List of allowed roles
        current_user: Current user from authentication
        
    Returns:
        User role if authorized
        
    Raises:
        HTTPException: If user doesn't have any of the allowed roles
    """
    user_role = current_user.get("role", "").upper()
    allowed_roles = [role.upper() for role in allowed_roles]
    
    if user_role not in allowed_roles:
        logger.warning(f"User {current_user.get('employee_id')} with role {user_role} attempted to access endpoint requiring roles: {allowed_roles}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
        )
    
    return user_role


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Get current user from JWT token (optional).
    
    Args:
        credentials: HTTP authorization credentials (optional)
        
    Returns:
        User dictionary if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await get_current_user_dict(token)
        return user
        
    except Exception as e:
        logger.debug(f"Optional authentication failed: {e}")
        return None


def verify_token_dependency(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return payload.
    
    Args:
        token: JWT token string
        
    Returns:
        Token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = verify_token(token)
        return payload
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) 