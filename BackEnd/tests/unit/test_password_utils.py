"""
Unit tests for password utility functions.
"""
import pytest
from utils.password_utils import PasswordValidator


class TestPasswordValidator:
    """Test cases for PasswordValidator."""
    
    def test_validate_password_strength_valid(self):
        """Test valid password strength validation."""
        valid_passwords = [
            "Password123!",
            "MySecure@Pass1",
            "Complex#Pass99",
            "Strong$Password2024"
        ]
        
        for password in valid_passwords:
            is_valid, errors = PasswordValidator.validate_password_strength(password)
            assert is_valid is True
            assert len(errors) == 0
    
    def test_validate_password_strength_too_short(self):
        """Test password too short validation."""
        short_passwords = ["Pass1!", "Abc123", "Short1!"]
        
        for password in short_passwords:
            is_valid, errors = PasswordValidator.validate_password_strength(password)
            assert is_valid is False
            assert any("8 characters" in error for error in errors)
    
    def test_validate_password_strength_too_long(self):
        """Test password too long validation."""
        long_password = "A" * 129 + "1!"
        
        is_valid, errors = PasswordValidator.validate_password_strength(long_password)
        assert is_valid is False
        assert any("128 characters" in error for error in errors)
    
    def test_validate_password_strength_no_uppercase(self):
        """Test password without uppercase validation."""
        passwords = ["password123!", "mypass@word1", "lowercase#123"]
        
        for password in passwords:
            is_valid, errors = PasswordValidator.validate_password_strength(password)
            assert is_valid is False
            assert any("uppercase" in error for error in errors)
    
    def test_validate_password_strength_no_lowercase(self):
        """Test password without lowercase validation."""
        passwords = ["PASSWORD123!", "MYPASS@WORD1", "UPPERCASE#123"]
        
        for password in passwords:
            is_valid, errors = PasswordValidator.validate_password_strength(password)
            assert is_valid is False
            assert any("lowercase" in error for error in errors)
    
    def test_validate_password_strength_no_digit(self):
        """Test password without digit validation."""
        passwords = ["Password!", "MyPass@Word", "NoNumbers#"]
        
        for password in passwords:
            is_valid, errors = PasswordValidator.validate_password_strength(password)
            assert is_valid is False
            assert any("digit" in error for error in errors)
    
    def test_validate_password_strength_no_special(self):
        """Test password without special character validation."""
        passwords = ["Password123", "MyPassWord1", "NoSpecialChars1"]
        
        for password in passwords:
            is_valid, errors = PasswordValidator.validate_password_strength(password)
            assert is_valid is False
            assert any("special character" in error for error in errors)
    
    def test_validate_password_strength_repeated_chars(self):
        """Test password with repeated characters validation."""
        passwords = ["Passsword123!", "MyPass@@@Word1", "Password111!"]
        
        for password in passwords:
            is_valid, errors = PasswordValidator.validate_password_strength(password)
            assert is_valid is False
            assert any("repeated" in error for error in errors)
    
    def test_validate_password_strength_common_sequences(self):
        """Test password with common sequences validation."""
        passwords = ["Password123!", "MyPass@abc1", "Test123qwe!"]
        
        for password in passwords:
            is_valid, errors = PasswordValidator.validate_password_strength(password)
            assert is_valid is False
            assert any("common sequences" in error for error in errors)
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = PasswordValidator.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are typically 60 characters
        assert hashed.startswith("$2b$")  # bcrypt identifier
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = PasswordValidator.hash_password(password)
        
        is_valid = PasswordValidator.verify_password(password, hashed)
        assert is_valid is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = PasswordValidator.hash_password(password)
        
        is_valid = PasswordValidator.verify_password(wrong_password, hashed)
        assert is_valid is False
    
    def test_verify_password_invalid_hash(self):
        """Test password verification with invalid hash."""
        password = "TestPassword123!"
        invalid_hash = "invalid_hash"
        
        is_valid = PasswordValidator.verify_password(password, invalid_hash)
        assert is_valid is False
    
    def test_generate_password_requirements(self):
        """Test password requirements generation."""
        requirements = PasswordValidator.generate_password_requirements()
        
        assert isinstance(requirements, dict)
        assert "min_length" in requirements
        assert "max_length" in requirements
        assert "require_uppercase" in requirements
        assert "require_lowercase" in requirements
        assert "require_digit" in requirements
        assert "require_special" in requirements
        assert "special_characters" in requirements
        assert "forbidden_sequences" in requirements
        assert "max_repeated_chars" in requirements
        
        assert requirements["min_length"] == 8
        assert requirements["max_length"] == 128
        assert requirements["require_uppercase"] is True
        assert requirements["require_lowercase"] is True
        assert requirements["require_digit"] is True
        assert requirements["require_special"] is True
    
    def test_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "TestPassword123!"
        hash1 = PasswordValidator.hash_password(password)
        hash2 = PasswordValidator.hash_password(password)
        
        assert hash1 != hash2  # Different salts should produce different hashes
        
        # But both should verify correctly
        assert PasswordValidator.verify_password(password, hash1) is True
        assert PasswordValidator.verify_password(password, hash2) is True
