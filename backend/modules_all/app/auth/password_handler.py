import logging
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    """
    hashed = pwd_context.hash(password)
    logger.info("Password hashed successfully. Password: " + password + " Hashed: " + hashed)
    return hashed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that the plain-text password matches the hashed password.
    """
    logger.info("Verifying password: " + plain_password + " with hashed password: " + hashed_password)
    result = pwd_context.verify(plain_password, hashed_password)
    if result:
        logger.info("Password verification succeeded.")
    else:
        logger.warning("Password verification failed.")
    return result
