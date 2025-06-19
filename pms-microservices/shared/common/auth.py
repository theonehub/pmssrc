"""
Shared Authentication Utilities for Microservices
"""

import os
import jwt
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Service URLs
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")

# Security scheme
security = HTTPBearer()


class CurrentUser:
    """Current user context"""
    def __init__(self, user_data: dict):
        self.employee_id = user_data.get("employee_id")
        self.email = user_data.get("email")
        self.name = user_data.get("name")
        self.role = user_data.get("role")
        self.permissions = user_data.get("permissions", {})
        self.hostname = user_data.get("hostname")
        self.organization_id = user_data.get("organization_id")
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return self.permissions.get(permission, False)
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == "admin"
    
    def is_hr(self) -> bool:
        """Check if user is HR"""
        return self.role in ["admin", "hr"]


class JWTManager:
    """JWT token management"""
    
    @staticmethod
    def create_token(user_data: dict) -> str:
        """Create JWT token"""
        payload = {
            "user_data": user_data,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow(),
            "iss": "pms-microservices"
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload.get("user_data")
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def refresh_token(current_token: str) -> str:
        """Refresh JWT token"""
        user_data = JWTManager.decode_token(current_token)
        return JWTManager.create_token(user_data)


async def verify_token_with_user_service(token: str) -> dict:
    """Verify token with User Service"""
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{USER_SERVICE_URL}/api/v2/auth/verify",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token verification failed"
                )
    except httpx.RequestError:
        # Fallback to local JWT verification if User Service is unavailable
        logger.warning("User Service unavailable, falling back to local JWT verification")
        return JWTManager.decode_token(token)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """Get current authenticated user"""
    token = credentials.credentials
    
    try:
        # First try local JWT decoding for performance
        user_data = JWTManager.decode_token(token)
        return CurrentUser(user_data)
    except HTTPException:
        # If local verification fails, try User Service
        user_data = await verify_token_with_user_service(token)
        return CurrentUser(user_data)


async def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Get current user and ensure they are admin"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_current_hr_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Get current user and ensure they are HR or admin"""
    if not current_user.is_hr():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR privileges required"
        )
    return current_user


def require_permission(permission: str):
    """Decorator factory for permission-based access control"""
    async def permission_checker(
        current_user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return permission_checker


class ServiceToServiceAuth:
    """Authentication for service-to-service communication"""
    
    @staticmethod
    def create_service_token(service_name: str) -> str:
        """Create token for service-to-service communication"""
        payload = {
            "service_name": service_name,
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
            "iss": "pms-microservices-internal"
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_service_token(token: str) -> str:
        """Verify service-to-service token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            if payload.get("iss") != "pms-microservices-internal":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid service token"
                )
            return payload.get("service_name")
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service token"
            )


async def get_service_headers(service_name: str) -> dict:
    """Get headers for service-to-service communication"""
    token = ServiceToServiceAuth.create_service_token(service_name)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Service-Name": service_name
    } 