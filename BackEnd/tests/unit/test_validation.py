"""
Unit tests for validation service functions.
"""
import pytest
from services.validation_service import ValidationService


class TestValidationService:
    """Test cases for ValidationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validation_service = ValidationService()
    
    def test_validate_email_valid(self):
        """Test valid email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "provider123@medical.org"
        ]
        
        for email in valid_emails:
            is_valid, error = self.validation_service.validate_email(email)
            assert is_valid is True
            assert error is None
    
    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        invalid_emails = [
            "",
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "a" * 250 + "@domain.com",  # Too long
        ]
        
        for email in invalid_emails:
            is_valid, error = self.validation_service.validate_email(email)
            assert is_valid is False
            assert error is not None
    
    def test_validate_email_disposable(self):
        """Test disposable email rejection."""
        disposable_emails = [
            "test@10minutemail.com",
            "user@tempmail.org",
            "provider@guerrillamail.com"
        ]
        
        for email in disposable_emails:
            is_valid, error = self.validation_service.validate_email(email)
            assert is_valid is False
            assert "disposable" in error.lower()
    
    def test_validate_phone_number_valid(self):
        """Test valid phone number validation."""
        valid_phones = [
            "+1234567890",
            "+44 20 7946 0958",
            "+91 98765 43210"
        ]
        
        for phone in valid_phones:
            is_valid, error, formatted = self.validation_service.validate_phone_number(phone)
            assert is_valid is True
            assert error is None
            assert formatted is not None
            assert formatted.startswith("+")
    
    def test_validate_phone_number_invalid(self):
        """Test invalid phone number validation."""
        invalid_phones = [
            "",
            "123",
            "invalid-phone",
            "123-456-7890",  # Without country code
        ]
        
        for phone in invalid_phones:
            is_valid, error, formatted = self.validation_service.validate_phone_number(phone)
            assert is_valid is False
            assert error is not None
            assert formatted is None
    
    def test_validate_password_valid(self):
        """Test valid password validation."""
        valid_passwords = [
            ("Password123!", "Password123!"),
            ("MySecure@Pass1", "MySecure@Pass1"),
            ("Complex#Pass99", "Complex#Pass99")
        ]
        
        for password, confirm in valid_passwords:
            is_valid, errors = self.validation_service.validate_password(password, confirm)
            assert is_valid is True
            assert len(errors) == 0
    
    def test_validate_password_invalid(self):
        """Test invalid password validation."""
        invalid_passwords = [
            ("short", "short"),  # Too short
            ("nouppercase123!", "nouppercase123!"),  # No uppercase
            ("NOLOWERCASE123!", "NOLOWERCASE123!"),  # No lowercase
            ("NoNumbers!", "NoNumbers!"),  # No numbers
            ("NoSpecialChars123", "NoSpecialChars123"),  # No special chars
            ("Password123!", "DifferentPass123!"),  # Passwords don't match
        ]
        
        for password, confirm in invalid_passwords:
            is_valid, errors = self.validation_service.validate_password(password, confirm)
            assert is_valid is False
            assert len(errors) > 0
    
    def test_validate_license_number_valid(self):
        """Test valid license number validation."""
        valid_licenses = [
            "ABC123456",
            "MD12345",
            "LICENSE789"
        ]
        
        for license_num in valid_licenses:
            is_valid, error = self.validation_service.validate_license_number(license_num)
            assert is_valid is True
            assert error is None
    
    def test_validate_license_number_invalid(self):
        """Test invalid license number validation."""
        invalid_licenses = [
            "",
            "123",  # Too short
            "ABC-123",  # Contains hyphen
            "LICENSE@123",  # Contains special char
            "a" * 60,  # Too long
        ]
        
        for license_num in invalid_licenses:
            is_valid, error = self.validation_service.validate_license_number(license_num)
            assert is_valid is False
            assert error is not None
    
    def test_validate_specialization_valid(self):
        """Test valid specialization validation."""
        # These should match the allowed specializations in config
        valid_specializations = [
            "Cardiology",
            "Neurology",
            "Pediatrics"
        ]
        
        for spec in valid_specializations:
            is_valid, error = self.validation_service.validate_specialization(spec)
            assert is_valid is True
            assert error is None
    
    def test_validate_specialization_invalid(self):
        """Test invalid specialization validation."""
        invalid_specializations = [
            "",
            "InvalidSpecialization",
            "cardiology",  # Wrong case
            "Fake Medicine"
        ]
        
        for spec in invalid_specializations:
            is_valid, error = self.validation_service.validate_specialization(spec)
            assert is_valid is False
            assert error is not None
    
    def test_validate_years_of_experience_valid(self):
        """Test valid years of experience validation."""
        valid_years = [0, 1, 10, 25, 50]
        
        for years in valid_years:
            is_valid, error = self.validation_service.validate_years_of_experience(years)
            assert is_valid is True
            assert error is None
    
    def test_validate_years_of_experience_invalid(self):
        """Test invalid years of experience validation."""
        invalid_years = [-1, 51, 100]
        
        for years in invalid_years:
            is_valid, error = self.validation_service.validate_years_of_experience(years)
            assert is_valid is False
            assert error is not None
    
    def test_validate_name_valid(self):
        """Test valid name validation."""
        valid_names = [
            "John",
            "Mary-Jane",
            "O'Connor",
            "Jean Pierre"
        ]
        
        for name in valid_names:
            is_valid, error = self.validation_service.validate_name(name, "First name")
            assert is_valid is True
            assert error is None
    
    def test_validate_name_invalid(self):
        """Test invalid name validation."""
        invalid_names = [
            "",
            "A",  # Too short
            "John123",  # Contains numbers
            "Name@Test",  # Contains special chars
            "a" * 60,  # Too long
        ]
        
        for name in invalid_names:
            is_valid, error = self.validation_service.validate_name(name, "First name")
            assert is_valid is False
            assert error is not None
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        test_cases = [
            ("normal text", "normal text"),
            ("text<script>", "textscript"),
            ("text&amp;", "textamp"),
            ("text'quote\"", "textquotequote"),
            ("", ""),
        ]
        
        for input_text, expected in test_cases:
            result = self.validation_service.sanitize_input(input_text)
            assert result == expected
    
    def test_validate_clinic_address_valid(self):
        """Test valid clinic address validation."""
        valid_address = {
            "street": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "zip": "10001"
        }
        
        is_valid, errors = self.validation_service.validate_clinic_address(valid_address)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_clinic_address_invalid(self):
        """Test invalid clinic address validation."""
        invalid_addresses = [
            {},  # Empty
            {"street": "", "city": "City", "state": "State", "zip": "12345"},  # Empty street
            {"street": "123", "city": "City", "state": "State", "zip": "12345"},  # Short street
            {"street": "123 Main St", "city": "", "state": "State", "zip": "12345"},  # Empty city
            {"street": "123 Main St", "city": "City", "state": "", "zip": "12345"},  # Empty state
            {"street": "123 Main St", "city": "City", "state": "State", "zip": ""},  # Empty zip
            {"street": "123 Main St", "city": "City", "state": "State", "zip": "invalid@zip"},  # Invalid zip
        ]
        
        for address in invalid_addresses:
            is_valid, errors = self.validation_service.validate_clinic_address(address)
            assert is_valid is False
            assert len(errors) > 0
