import logging
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    """
    hashed = pwd_context.hash(password)
    logger.debug("Password hashed successfully.")
    return hashed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that the plain-text password matches the hashed password.
    """
    result = pwd_context.verify(plain_password, hashed_password)
    if result:
        logger.debug("Password verification succeeded.")
    else:
        logger.warning("Password verification failed.")
    return result
