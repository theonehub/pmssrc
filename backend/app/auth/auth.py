import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM
from models.user_model import User
from typing import List
from services.user_service import get_user_by_emp_id

# Set up a logger for this module.
logger = logging.getLogger(__name__)

# OAuth2 scheme to extract token from requests.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def extract_emp_id(token: str = Depends(oauth2_scheme)):
    """
    Extracts the emp_id from the JWT token.
    """
    try:
        # Decode the token using the secret key and algorithm.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        emp_id: str = payload.get("sub")
        if emp_id is None:
            logger.warning("Token payload does not contain emp_id.")
            raise credentials_exception
    except JWTError as e:
        logger.error("JWT decode error: %s", e)
        raise credentials_exception
    return emp_id


async def extract_hostname(token: str = Depends(oauth2_scheme)):
    """
    Extracts the hostname from the JWT token.
    """
    try:
        # Decode the token using the secret key and algorithm.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        hostname: str = payload.get("hostname")
        if hostname is None:
            logger.warning("Token payload does not contain hostname.")
            raise credentials_exception
    except JWTError as e:
        logger.error("JWT decode error: %s", e)
        raise credentials_exception
    return hostname

async def get_current_user(emp_id: str = Depends(extract_emp_id), hostname: str = Depends(extract_hostname)):
    """
    Dependency to get the current authenticated user from the JWT token.
    Raises HTTP 401 if token is invalid or user is not found.
    """
    # Retrieve the user info from the database based on emp_id.
    user = await get_user_by_emp_id(emp_id, hostname)
    if user is None:
        logger.warning("User not found for emp_id: %s", emp_id)
        raise credentials_exception

    logger.info("Current user '%s' retrieved successfully.", emp_id)
    return User(emp_id=user["emp_id"], role=user["role"])


def role_checker(roles: List[str]):
    async def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise credentials_exception
        return current_user.role
    return checker
