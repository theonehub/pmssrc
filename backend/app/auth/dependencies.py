import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.auth.jwt_handler import SECRET_KEY, ALGORITHM

# Set up logger for this module.
logger = logging.getLogger(__name__)

# OAuth2 scheme for dependency injection.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency that decodes the JWT token to extract the current user information.
    Raises HTTP 401 if token is invalid or required fields are missing.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        employee_id: str = payload.get("employee_id")
        if username is None or role is None:
            logger.warning("Token payload is missing username or role.")
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {
            "username": username,
            "role": role,
            "employee_id": employee_id
        }
    except JWTError as e:
        logger.error("Failed to decode token: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )

def get_current_user_role(token: str = Depends(oauth2_scheme)):
    """
    Dependency that decodes the JWT token to extract the user's role.
    Raises HTTP 401 if token is invalid or required fields are missing.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            logger.warning("Token payload is missing username or role.")
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return role
    except JWTError as e:
        logger.error("Failed to decode token: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )

def role_checker(allowed_roles):
    """
    Dependency that ensures the current user's role is among the allowed_roles.
    If not, raises HTTP 403 Forbidden.
    """
    def wrapper(role: str = Depends(get_current_user_role)):
        if role not in allowed_roles:
            logger.warning("Role '%s' is not allowed. Allowed roles: %s", role, allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
        logger.info("Role '%s' is authorized.", role)
        return role
    return wrapper
