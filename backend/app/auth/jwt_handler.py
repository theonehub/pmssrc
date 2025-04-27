import logging
from datetime import datetime, timedelta
from jose import jwt
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

logger = logging.getLogger(__name__)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT token with an expiration time.
    The token includes data (typically the user's username and role).
    """
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Access token created for user: %s", data.get("sub"))
    return token

def decode_access_token(token: str):
    """
    Decodes a JWT token and returns the payload.
    Logs errors if token decoding fails.
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug("Token decoded successfully: %s", decoded)
        return decoded
    except Exception as e:
        logger.error("Error decoding token: %s", e)
        raise e
