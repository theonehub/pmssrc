import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM
from models.user_model import User
from services.user_service import get_login_info_by_username

# Set up a logger for this module.
logger = logging.getLogger(__name__)

# OAuth2 scheme to extract token from requests.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get the current authenticated user from the JWT token.
    Raises HTTP 401 if token is invalid or user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using the secret key and algorithm.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token payload does not contain username.")
            raise credentials_exception
    except JWTError as e:
        logger.error("JWT decode error: %s", e)
        raise credentials_exception

    # Retrieve the user info from the database based on username.
    user = get_login_info_by_username(username)
    if user is None:
        logger.warning("User not found for username: %s", username)
        raise credentials_exception

    logger.info("Current user '%s' retrieved successfully.", username)
    return User(
    id=str(user.get("user_id", "")),
    username=user["username"],
    role=user["role"]
)
