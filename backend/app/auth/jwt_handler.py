"""
JWT Handler Module
Handles JWT token generation and validation
"""

from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.auth.jwt_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Import centralized logger
from app.utils.logger import get_logger

logger = get_logger(__name__)

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """
    Create a new JWT access token.
    
    Args:
        data: Data to encode in the token
        
    Returns:
        str: Encoded JWT token
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Created access token for user: {data.get('sub', 'unknown')}")
        return token
        
    except Exception as e:
        logger.error(f"Failed to create access token: {str(e)}", exc_info=True)
        raise

def verify_access_token(token: str) -> dict:
    """
    Verify and decode a JWT access token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict: Decoded token data
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Verified access token for user: {payload.get('sub', 'unknown')}")
        return payload
        
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to verify access token: {str(e)}", exc_info=True)
        raise

def decode_access_token(token: str):
    """
    Decodes a JWT token and returns the payload.
    Validates the token signature and expiration.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        JWTError: If token is invalid, expired, or malformed
        Exception: If decoding fails for other reasons
    """
    try:
        # Decode and validate the token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        logger.info("Token decoded successfully for user: %s", decoded.get("sub", "unknown"))
        
        # Additional validation checks
        if "exp" not in decoded:
            raise JWTError("Token missing expiration claim")
        
        if "sub" not in decoded and "username" not in decoded:
            raise JWTError("Token missing subject or username claim")
        
        return decoded
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise JWTError("Token has expired")
    
    except JWTError as e:
        logger.warning("Invalid token: %s", e)
        raise JWTError(f"Invalid token: {str(e)}")
    
    except Exception as e:
        logger.error("Error decoding token: %s", e)
        raise Exception(f"Failed to decode token: {str(e)}")

def verify_token(token: str) -> bool:
    """
    Verify if a token is valid without returning the payload.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        decode_access_token(token)
        return True
    except Exception:
        return False

def get_token_claims(token: str) -> dict:
    """
    Get specific claims from a token without full validation.
    Useful for extracting user info from expired tokens.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Token claims (may be from expired token)
        
    Raises:
        Exception: If token is malformed
    """
    try:
        # Decode without verification (for extracting claims from expired tokens)
        decoded = jwt.decode(token, options={"verify_signature": False})
        logger.info("Token claims extracted (unverified)")
        return decoded
    except Exception as e:
        logger.error("Error extracting token claims: %s", e)
        raise Exception(f"Failed to extract token claims: {str(e)}")

def refresh_token_if_needed(token: str, refresh_threshold_minutes: int = 60) -> str:
    """
    Check if token needs refresh and return a new one if needed.
    
    Args:
        token: Current JWT token
        refresh_threshold_minutes: Minutes before expiry to trigger refresh
        
    Returns:
        str: New token if refresh needed, original token otherwise
        
    Raises:
        Exception: If token operations fail
    """
    try:
        payload = decode_access_token(token)
        
        # Check if token expires soon
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            time_until_expiry = exp_datetime - datetime.utcnow()
            
            if time_until_expiry.total_seconds() < (refresh_threshold_minutes * 60):
                logger.info("Token needs refresh, creating new token")
                
                # Remove old timestamp claims and create new token
                new_payload = {k: v for k, v in payload.items() if k not in ["exp", "iat"]}
                new_payload["iat"] = datetime.utcnow().timestamp()
                # Create new access token with same user data
                new_expires_delta = timedelta(hours=8)
                return create_access_token(new_payload, new_expires_delta)
        
        return token
        
    except Exception as e:
        logger.error("Error refreshing token: %s", e)
        raise Exception(f"Failed to refresh token: {str(e)}")
