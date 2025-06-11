"""
Authentication Dependencies
JWT-based authentication with organization context support
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


@dataclass
class CurrentUser:
    """Current authenticated user context with organization information."""
    
    user_id: str
    employee_id: str
    email: str
    username: str
    hostname: str  # Organization hostname for multi-tenancy
    roles: List[str]
    permissions: List[str]
    is_active: bool
    is_superuser: bool = False
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return role in self.roles
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions or self.is_superuser
    
    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return any(role in self.roles for role in roles)
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(self.has_permission(perm) for perm in permissions)


class AuthenticationError(Exception):
    """Custom authentication error."""
    pass


class AuthorizationError(Exception):
    """Custom authorization error."""
    pass


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise AuthenticationError("Invalid token")


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Get current authenticated user with organization context.
    
    Extracts user information from JWT token and adds organization context
    based on request hostname or explicit organization parameter.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify JWT token
        payload = verify_token(credentials.credentials)
        
        # Extract user information from token
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Extract organization context from request
        # This can be from hostname, header, or query parameter
        hostname = extract_organization_context(request)
        if not hostname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization context required"
            )
        
        # Create CurrentUser object with organization context
        current_user = CurrentUser(
            user_id=user_id,
            employee_id=payload.get("employee_id", ""),
            email=payload.get("email", ""),
            username=payload.get("username", ""),
            hostname=hostname,
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", []),
            is_active=payload.get("is_active", True),
            is_superuser=payload.get("is_superuser", False)
        )
        
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        return current_user
        
    except AuthenticationError:
        raise credentials_exception
    except JWTError:
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise credentials_exception


def extract_organization_context(request: Request) -> Optional[str]:
    """
    Extract organization context from request.
    
    Priority order:
    1. X-Organization header
    2. organization query parameter
    3. hostname (for multi-tenant domains)
    """
    # Check for explicit organization header
    org_header = request.headers.get("X-Organization")
    if org_header:
        return org_header
    
    # Check for organization query parameter
    org_param = request.query_params.get("organization")
    if org_param:
        return org_param
    
    # Extract from hostname (for multi-tenant domains)
    host = request.headers.get("host", "")
    if host and "." in host:
        # Extract subdomain as organization identifier
        subdomain = host.split(".")[0]
        if subdomain and subdomain != "www":
            return subdomain
    
    # Default organization for development
    return "default"


def require_role(required_role: str):
    """Dependency to require specific role."""
    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_checker


def require_permission(required_permission: str):
    """Dependency to require specific permission."""
    def permission_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        return current_user
    return permission_checker


def require_any_role(required_roles: List[str]):
    """Dependency to require any of the specified roles."""
    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_any_role(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of roles {required_roles} required"
            )
        return current_user
    return role_checker


def require_any_permission(required_permissions: List[str]):
    """Dependency to require any of the specified permissions."""
    def permission_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_any_permission(required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of permissions {required_permissions} required"
            )
        return current_user
    return permission_checker


def optional_auth(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[CurrentUser]:
    """Optional authentication - returns None if no token provided."""
    if not credentials:
        return None
    
    try:
        return get_current_user(request, credentials)
    except HTTPException:
        return None 