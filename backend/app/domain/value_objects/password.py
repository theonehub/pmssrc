"""
Password Value Object
Encapsulates password handling with security features following DDD principles
"""

from dataclasses import dataclass
from typing import Optional
import re
import bcrypt


@dataclass(frozen=True)
class Password:
    """
    Value object for password handling.
    
    Follows SOLID principles:
    - SRP: Only handles password-related operations
    - OCP: Can be extended with new password policies
    - LSP: Can be substituted anywhere Password is expected
    - ISP: Focused interface for password operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    hashed_value: str
    
    @classmethod
    def from_plain_text(cls, plain_password: str) -> 'Password':
        """
        Create password from plain text.
        
        Args:
            plain_password: Plain text password
            
        Returns:
            Password instance with hashed value
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        cls._validate_password_strength(plain_password)
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        return cls(hashed_value=hashed.decode('utf-8'))
    
    @classmethod
    def from_hash(cls, hashed_password: str) -> 'Password':
        """
        Create password from existing hash.
        
        Args:
            hashed_password: Already hashed password
            
        Returns:
            Password instance
        """
        return cls(hashed_value=hashed_password)
    
    def verify(self, plain_password: str) -> bool:
        """
        Verify plain text password against hash.
        
        Args:
            plain_password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                self.hashed_value.encode('utf-8')
            )
        except Exception:
            return False
    
    def needs_rehashing(self) -> bool:
        """
        Check if password needs rehashing (e.g., due to updated cost factor).
        
        Returns:
            True if password should be rehashed
        """
        try:
            # Check if the hash uses the current cost factor
            current_cost = bcrypt.gensalt().decode('utf-8')[4:6]
            hash_cost = self.hashed_value[4:6]
            return hash_cost != current_cost
        except Exception:
            return True  # If we can't determine, assume it needs rehashing
    
    @staticmethod
    def _validate_password_strength(password: str) -> None:
        """
        Validate password strength.
        
        Args:
            password: Plain text password to validate
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise ValueError("Password cannot be longer than 128 characters")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '12345678', 'qwerty123', 'admin123',
            'password123', '123456789', 'welcome123'
        ]
        
        if password.lower() in weak_passwords:
            raise ValueError("Password is too common and weak")
    
    @staticmethod
    def get_strength_score(password: str) -> int:
        """
        Calculate password strength score (0-100).
        
        Args:
            password: Plain text password
            
        Returns:
            Strength score from 0 (weakest) to 100 (strongest)
        """
        if not password:
            return 0
        
        score = 0
        
        # Length scoring
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Character variety scoring
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 15
        
        # Complexity scoring
        char_types = 0
        if re.search(r'[a-z]', password):
            char_types += 1
        if re.search(r'[A-Z]', password):
            char_types += 1
        if re.search(r'\d', password):
            char_types += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            char_types += 1
        
        if char_types >= 3:
            score += 10
        if char_types == 4:
            score += 5
        
        # Penalty for common patterns
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            score -= 10
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):  # Sequential numbers
            score -= 5
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):  # Sequential letters
            score -= 5
        
        return max(0, min(100, score))
    
    @staticmethod
    def get_strength_description(password: str) -> str:
        """
        Get password strength description.
        
        Args:
            password: Plain text password
            
        Returns:
            Human-readable strength description
        """
        score = Password.get_strength_score(password)
        
        if score < 30:
            return "Very Weak"
        elif score < 50:
            return "Weak"
        elif score < 70:
            return "Fair"
        elif score < 85:
            return "Good"
        else:
            return "Strong"
    
    @staticmethod
    def generate_temporary_password(length: int = 12) -> str:
        """
        Generate a temporary password.
        
        Args:
            length: Length of password to generate
            
        Returns:
            Generated temporary password
        """
        import secrets
        import string
        
        # Ensure we have at least one character from each required type
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*"
        
        # Start with one character from each type
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill the rest with random characters from all types
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def get_strength_score(self) -> int:
        """
        Get strength score for this password.
        Note: This can't determine the actual strength since we only have the hash.
        Returns a default score indicating it passed validation.
        """
        return 75  # Assume good strength since it passed validation
    
    def __str__(self) -> str:
        """String representation (masked)"""
        return "Password(***)"
    
    def __repr__(self) -> str:
        """Developer representation (masked)"""
        return f"Password(hash_length={len(self.hashed_value)})" 