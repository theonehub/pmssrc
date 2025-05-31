from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config.settings import SECRET_KEY as JWT_SECRET_KEY, ALGORITHM as JWT_ALGORITHM
from typing import List
from app.utils.logger import get_logger

# Set up a logger for this module.
logger = get_logger(__name__)

# OAuth2 scheme to extract token from requests.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def extract_emp_id(token: str = Depends(oauth2_scheme)):
    """
    Extracts the emp_id from the JWT token.
    """
    try:
        # Decode the token using the secret key and algorithm.
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        emp_id: str = payload.get("sub")
        if emp_id is None:
            logger.warning("Token payload does not contain emp_id.")
            raise credentials_exception
    except JWTError as e:
        logger.error("JWT decode error: %s", e)
        raise credentials_exception
    return emp_id


def extract_hostname(token: str = Depends(oauth2_scheme)):
    """
    Extracts the hostname from the JWT token.
    """
    try:
        # Decode the token using the secret key and algorithm.
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        hostname: str = payload.get("hostname")
        if hostname is None:
            logger.warning("Token payload does not contain hostname.")
            raise credentials_exception
    except JWTError as e:
        logger.error("JWT decode error: %s", e)
        raise credentials_exception
    return hostname

def  extract_role(token: str = Depends(oauth2_scheme)):
    """
    Extracts the role from the JWT token.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    role: str = payload.get("role")
    if role is None:
        logger.warning("Token payload does not contain role.")
        raise credentials_exception
    return role

async def get_current_user(emp_id: str = Depends(extract_emp_id), hostname: str = Depends(extract_hostname)):
    """
    Dependency to get the current authenticated user from the JWT token.
    Raises HTTP 401 if token is invalid or user is not found.
    """
    # Retrieve the user info from the database based on emp_id.
    user = await get_user_by_emp_id(emp_id, hostname)
    if not user:
        user = await get_user_by_emp_id(emp_id, "global_database")
    if user is None:
        logger.warning("User not found for emp_id: %s", emp_id)
        raise credentials_exception

    logger.info("Current user '%s' retrieved successfully.", emp_id)
    return User(emp_id=user["emp_id"], role=user["role"])


def role_checker(roles: List[str]):
    def checker(role: str = Depends(extract_role)):
        logger.info("Checking role for user: %s", role)
        if role not in roles:
            raise credentials_exception
        return role
    return checker

# Simple User class for authentication
class User:
    def __init__(self, emp_id: str, role: str):
        self.emp_id = emp_id
        self.role = role

# Simple stub for user lookup
async def get_user_by_emp_id(emp_id: str, hostname: str = None):
    """Simple stub for user lookup - replace with actual implementation"""
    # For now, return a mock user for testing
    return {
        "emp_id": emp_id,
        "role": "employee"  # Default role
    }
