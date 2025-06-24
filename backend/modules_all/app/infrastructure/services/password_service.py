"""
Password Service Implementation
SOLID-compliant service for password operations
"""

import logging
import secrets
import string
from typing import Optional
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class PasswordService:
    """
    Service for password operations following SOLID principles.
    
    - SRP: Only handles password-related operations
    - OCP: Can be extended with new hashing algorithms
    - LSP: Can be substituted with other password services
    - ISP: Focused interface for password operations
    - DIP: Depends on abstractions (CryptContext)
    """
    
    def __init__(self):
        """Initialize password service with bcrypt context."""
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.temp_password_length = 12
        self.temp_password_chars = string.ascii_letters + string.digits + "!@#$%^&*"
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
            
        Raises:
            ValueError: If password is empty or None
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        try:
            hashed = self.pwd_context.hash(password)
            logger.info("Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        if not plain_password or not hashed_password:
            return False
        
        try:
            is_valid = self.pwd_context.verify(plain_password, hashed_password)
            logger.info(f"Password verification result: {is_valid}")
            return is_valid
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def generate_temporary_password(self, length: Optional[int] = None) -> str:
        """
        Generate a secure temporary password.
        
        Args:
            length: Length of password to generate (default: 12)
            
        Returns:
            Generated temporary password
        """
        if length is None:
            length = self.temp_password_length
        
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        try:
            # Ensure password has at least one of each character type
            password_chars = []
            
            # Add at least one uppercase letter
            password_chars.append(secrets.choice(string.ascii_uppercase))
            
            # Add at least one lowercase letter
            password_chars.append(secrets.choice(string.ascii_lowercase))
            
            # Add at least one digit
            password_chars.append(secrets.choice(string.digits))
            
            # Add at least one special character
            password_chars.append(secrets.choice("!@#$%^&*"))
            
            # Fill remaining length with random characters
            for _ in range(length - 4):
                password_chars.append(secrets.choice(self.temp_password_chars))
            
            # Shuffle the password characters
            secrets.SystemRandom().shuffle(password_chars)
            
            password = ''.join(password_chars)
            logger.info(f"Generated temporary password of length {length}")
            return password
            
        except Exception as e:
            logger.error(f"Error generating temporary password: {e}")
            raise
    
    def is_password_strong(self, password: str) -> dict:
        """
        Check password strength and return analysis.
        
        Args:
            password: Password to analyze
            
        Returns:
            Dictionary with strength analysis
        """
        if not password:
            return {
                "is_strong": False,
                "score": 0,
                "issues": ["Password is empty"],
                "suggestions": ["Password must not be empty"]
            }
        
        issues = []
        suggestions = []
        score = 0
        
        # Length check
        if len(password) < 8:
            issues.append("Password is too short")
            suggestions.append("Use at least 8 characters")
        else:
            score += 1
        
        # Uppercase check
        if not any(c.isupper() for c in password):
            issues.append("No uppercase letters")
            suggestions.append("Include at least one uppercase letter")
        else:
            score += 1
        
        # Lowercase check
        if not any(c.islower() for c in password):
            issues.append("No lowercase letters")
            suggestions.append("Include at least one lowercase letter")
        else:
            score += 1
        
        # Digit check
        if not any(c.isdigit() for c in password):
            issues.append("No numbers")
            suggestions.append("Include at least one number")
        else:
            score += 1
        
        # Special character check
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            issues.append("No special characters")
            suggestions.append("Include at least one special character")
        else:
            score += 1
        
        # Length bonus
        if len(password) >= 12:
            score += 1
        
        # Determine strength
        is_strong = score >= 4 and len(password) >= 8
        
        return {
            "is_strong": is_strong,
            "score": score,
            "max_score": 6,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if password hash needs to be updated.
        
        Args:
            hashed_password: Hashed password to check
            
        Returns:
            True if hash needs updating, False otherwise
        """
        try:
            return self.pwd_context.needs_update(hashed_password)
        except Exception as e:
            logger.error(f"Error checking if password needs rehash: {e}")
            return False 