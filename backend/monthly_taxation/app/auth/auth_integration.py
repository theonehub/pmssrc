"""
Authentication Integration Module
Provides authentication utilities for the monthly taxation module
by replicating the auth functions from modules_all to avoid cross-module dependencies.
"""

import os
import logging
from typing import Dict, Any
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# Set up logging
logger = logging.getLogger(__name__)

# Authentication configuration
# These should match the settings from modules_all
# modules_all uses JWT_SECRET (not JWT_SECRET_KEY)
JWT_SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Log configuration for debugging
logger.info(f"JWT Secret Key configured: {'***' if JWT_SECRET_KEY else 'NOT SET'}")
logger.info(f"JWT Algorithm: {JWT_ALGORITHM}")

# OAuth2 scheme to extract token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def extract_employee_id(token: str = Depends(oauth2_scheme)):
    """
    Extracts the employee_id from the JWT token.
    """
    try:
        logger.debug(f"Attempting to decode token for employee_id extraction")
        # Decode the token using the secret key and algorithm.
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        logger.debug(f"Token payload: {list(payload.keys())}")  # Don't log full payload for security
        
        employee_id: str = payload.get("sub")
        if employee_id is None:
            logger.warning("Token payload does not contain 'sub' claim for employee_id")
            raise credentials_exception
        
        logger.debug(f"Successfully extracted employee_id: {employee_id}")
        return employee_id
        
    except JWTError as e:
        logger.error(f"JWT Error extracting employee_id: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error extracting employee_id: {e}")
        raise credentials_exception


def extract_hostname(token: str = Depends(oauth2_scheme)):
    """
    Extracts the hostname from the JWT token.
    """
    try:
        logger.debug(f"Attempting to decode token for hostname extraction")
        # Decode the token using the secret key and algorithm.
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        hostname: str = payload.get("hostname")
        if hostname is None:
            logger.warning("Token payload does not contain 'hostname' claim")
            raise credentials_exception
        
        logger.debug(f"Successfully extracted hostname: {hostname}")
        return hostname
        
    except JWTError as e:
        logger.error(f"JWT Error extracting hostname: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error extracting hostname: {e}")
        raise credentials_exception


def extract_role(token: str = Depends(oauth2_scheme)):
    """
    Extracts the role from the JWT token.
    """
    try:
        logger.debug(f"Attempting to decode token for role extraction")
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        role: str = payload.get("role")
        if role is None:
            logger.warning("Token payload does not contain 'role' claim")
            raise credentials_exception
        
        logger.debug(f"Successfully extracted role: {role}")
        return role
        
    except JWTError as e:
        logger.error(f"JWT Error extracting role: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error extracting role: {e}")
        raise credentials_exception


class CurrentUser(BaseModel):
    """Current user model for monthly taxation module"""
    employee_id: str
    hostname: str
    role: str

    @property
    def user_id(self) -> str:
        """Alias for employee_id for backward compatibility"""
        return self.employee_id


async def get_current_user(
    employee_id: str = Depends(extract_employee_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(extract_role)
) -> CurrentUser:
    """
    Get current authenticated user from JWT token.
    
    This function integrates with the modules_all auth system
    to extract user information from the JWT token and return
    a CurrentUser object.
    
    Returns:
        CurrentUser: Current user information
    """
    logger.debug(f"Creating CurrentUser object for employee_id: {employee_id}")
    return CurrentUser(
        employee_id=employee_id,
        hostname=hostname,
        role=role
    )


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return payload.
    
    Args:
        token: JWT token string
        
    Returns:
        Dict[str, Any]: Token payload if valid
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        logger.debug(f"Verifying token: {token[:20]}...")
        
        # Decode and verify the token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        logger.debug(f"Token verified successfully. Payload keys: {list(payload.keys())}")
        return payload
        
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_dict(token: str) -> Dict[str, Any]:
    """
    Get current user as dictionary from token string.
    
    Args:
        token: JWT token string
        
    Returns:
        Dict[str, Any]: Current user information as dictionary
    """
    try:
        # Verify and decode the token
        payload = verify_token(token)
        
        employee_id = payload.get("sub")
        hostname = payload.get("hostname")
        role = payload.get("role")
        
        if not employee_id or not hostname or not role:
            logger.warning("Token payload missing required claims")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"Creating user dict for employee_id: {employee_id}")
        return {
            "employee_id": employee_id,
            "user_id": employee_id,  # Alias for backward compatibility
            "hostname": hostname,
            "role": role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user from token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def debug_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Debug function to examine token payload without validation.
    Use only for debugging purposes.
    """
    try:
        logger.info(f"Debug token function called with token: {token[:20]}...")
        
        # Decode without verification to see the payload
        # jwt.decode needs a key even when verification is disabled, so provide a dummy one
        unverified_payload = jwt.decode(token, "dummy-key", options={"verify_signature": False})
        logger.info(f"Unverified token payload keys: {list(unverified_payload.keys())}")
        logger.info(f"Token claims: {unverified_payload}")
        return unverified_payload
    except Exception as e:
        logger.error(f"Error decoding token for debugging: {e}")
        return {"error": str(e), "token_preview": token[:50] + "..." if len(token) > 50 else token} 