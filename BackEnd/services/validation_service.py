"""
Validation service for complex business logic validation.
"""
import re
from typing import List, Tuple, Optional
import phonenumbers
from core.config import settings
from utils.email_utils import EmailManager
from utils.password_utils import PasswordValidator


class ValidationService:
    """Service for handling complex validation logic."""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address format and constraints.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or not email.strip():
            return False, "Email address is required"
        
        email = email.strip().lower()
        
        if len(email) > 254:
            return False, "Email address is too long (max 254 characters)"
        
        if not EmailManager.validate_email_format(email):
            return False, "Invalid email address format"
        
        # Check for common disposable email domains (optional)
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email'
        ]
        
        domain = email.split('@')[1] if '@' in email else ''
        if domain in disposable_domains:
            return False, "Disposable email addresses are not allowed"
        
        return True, None
    
    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate and format phone number.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message, formatted_phone)
        """
        if not phone or not phone.strip():
            return False, "Phone number is required", None
        
        try:
            # Parse phone number
            parsed_number = phonenumbers.parse(phone, None)
            
            # Validate phone number
            if not phonenumbers.is_valid_number(parsed_number):
                return False, "Invalid phone number", None
            
            # Check if it's a mobile number (optional business rule)
            number_type = phonenumbers.number_type(parsed_number)
            if number_type not in [
                phonenumbers.PhoneNumberType.MOBILE,
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE,
                phonenumbers.PhoneNumberType.FIXED_LINE
            ]:
                return False, "Please provide a valid mobile or landline number", None
            
            # Format in E164 format
            formatted_phone = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
            
            return True, None, formatted_phone
            
        except phonenumbers.NumberParseException as e:
            error_messages = {
                phonenumbers.NumberParseException.INVALID_COUNTRY_CODE: "Invalid country code",
                phonenumbers.NumberParseException.NOT_A_NUMBER: "Not a valid phone number",
                phonenumbers.NumberParseException.TOO_SHORT_NSN: "Phone number is too short",
                phonenumbers.NumberParseException.TOO_LONG: "Phone number is too long",
            }
            
            error_msg = error_messages.get(e.error_type, "Invalid phone number format")
            return False, error_msg, None
    
    @staticmethod
    def validate_password(password: str, confirm_password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength and confirmation.
        
        Args:
            password: Password to validate
            confirm_password: Password confirmation
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if passwords match
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        # Validate password strength
        is_strong, strength_errors = PasswordValidator.validate_password_strength(password)
        if not is_strong:
            errors.extend(strength_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_license_number(license_number: str) -> Tuple[bool, Optional[str]]:
        """
        Validate medical license number format.
        
        Args:
            license_number: License number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not license_number or not license_number.strip():
            return False, "License number is required"
        
        license_number = license_number.strip().upper()
        
        if len(license_number) < 5:
            return False, "License number must be at least 5 characters long"
        
        if len(license_number) > 50:
            return False, "License number must not exceed 50 characters"
        
        # License number should be alphanumeric
        if not re.match(r'^[A-Z0-9]+$', license_number):
            return False, "License number must contain only letters and numbers"
        
        # Additional format validation can be added here based on specific requirements
        # For example, different states/countries may have different formats
        
        return True, None
    
    @staticmethod
    def validate_specialization(specialization: str) -> Tuple[bool, Optional[str]]:
        """
        Validate medical specialization against allowed list.
        
        Args:
            specialization: Specialization to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not specialization or not specialization.strip():
            return False, "Specialization is required"
        
        specialization = specialization.strip()
        
        if specialization not in settings.ALLOWED_SPECIALIZATIONS:
            allowed_list = ", ".join(settings.ALLOWED_SPECIALIZATIONS)
            return False, f"Specialization must be one of: {allowed_list}"
        
        return True, None
    
    @staticmethod
    def validate_years_of_experience(years: int) -> Tuple[bool, Optional[str]]:
        """
        Validate years of experience.
        
        Args:
            years: Years of experience
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if years < 0:
            return False, "Years of experience cannot be negative"
        
        if years > 50:
            return False, "Years of experience cannot exceed 50 years"
        
        return True, None
    
    @staticmethod
    def validate_name(name: str, field_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate name fields (first name, last name).
        
        Args:
            name: Name to validate
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, f"{field_name} is required"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, f"{field_name} must be at least 2 characters long"
        
        if len(name) > 50:
            return False, f"{field_name} must not exceed 50 characters"
        
        # Name should only contain letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\'-]+$", name):
            return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, None
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """
        Sanitize input string to prevent injection attacks.
        
        Args:
            input_string: Input to sanitize
            
        Returns:
            Sanitized string
        """
        if not input_string:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
        sanitized = input_string
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_clinic_address(address: dict) -> Tuple[bool, List[str]]:
        """
        Validate clinic address information.
        
        Args:
            address: Address dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        required_fields = ['street', 'city', 'state', 'zip']
        
        for field in required_fields:
            if not address.get(field) or not str(address[field]).strip():
                errors.append(f"Address {field} is required")
        
        # Validate ZIP code format
        zip_code = address.get('zip', '').strip()
        if zip_code and not re.match(r'^[\d\w\s-]{3,20}$', zip_code):
            errors.append("Invalid ZIP/postal code format")
        
        # Validate street address length
        street = address.get('street', '').strip()
        if street and len(street) < 5:
            errors.append("Street address must be at least 5 characters long")
        
        return len(errors) == 0, errors
