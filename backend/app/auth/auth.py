import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM
from models.user_model import User
from services.user_service import get_user_by_empId

# Set up a logger for this module.
logger = logging.getLogger(__name__)

# OAuth2 scheme to extract token from requests.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def extract_empId(token: str = Depends(oauth2_scheme)):
    """
    Extracts the empId from the JWT token.
    """
    try:
        # Decode the token using the secret key and algorithm.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        empId: str = payload.get("sub")
        if empId is None:
            logger.warning("Token payload does not contain empId.")
            raise credentials_exception
    except JWTError as e:
        logger.error("JWT decode error: %s", e)
        raise credentials_exception

def get_current_user(empId: str = Depends(extract_empId)):
    """
    Dependency to get the current authenticated user from the JWT token.
    Raises HTTP 401 if token is invalid or user is not found.
    """
    # Retrieve the user info from the database based on empId.
    user = get_user_by_empId(empId)
    if user is None:
        logger.warning("User not found for empId: %s", empId)
        raise credentials_exception

    logger.info("Current user '%s' retrieved successfully.", empId)
    return User(
    id=str(user.get("empId", "")),
    empId=user["empId"],
    role=user["role"]
)
