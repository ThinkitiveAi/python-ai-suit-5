"""
Utility functions for password handling and validation.
"""
import re
from typing import List, Tuple
from core.security import security


class PasswordValidator:
    """Password validation utilities."""
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength and return detailed feedback.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if len(password) > 128:
            errors.append("Password must not exceed 128 characters")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common weak patterns
        if re.search(r'(.)\1{2,}', password):
            errors.append("Password should not contain repeated characters")
        
        # Check for common sequences
        common_sequences = ['123', 'abc', 'qwe', 'asd', 'zxc']
        password_lower = password.lower()
        for seq in common_sequences:
            if seq in password_lower:
                errors.append("Password should not contain common sequences")
                break
        
        return len(errors) == 0, errors
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using the security manager.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return security.hash_password(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        return security.verify_password(plain_password, hashed_password)
    
    @staticmethod
    def generate_password_requirements() -> dict:
        """
        Get password requirements for client-side validation.
        
        Returns:
            Dictionary of password requirements
        """
        return {
            "min_length": 8,
            "max_length": 128,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digit": True,
            "require_special": True,
            "special_characters": "!@#$%^&*(),.?\":{}|<>",
            "forbidden_sequences": ["123", "abc", "qwe", "asd", "zxc"],
            "max_repeated_chars": 2
        }


# Convenience functions for backward compatibility
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return PasswordValidator.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return PasswordValidator.verify_password(plain_password, hashed_password)


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """Validate password strength and return detailed feedback."""
    return PasswordValidator.validate_password_strength(password)


def get_password_requirements() -> dict:
    """Get password requirements for client-side validation."""
    return PasswordValidator.generate_password_requirements()
