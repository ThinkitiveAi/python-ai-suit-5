"""
Pydantic schemas for Provider request/response validation and serialization.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, model_validator, Field
from enum import Enum
import re
import phonenumbers
from core.config import settings


class VerificationStatus(str, Enum):
    """Enumeration for provider verification status."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class ClinicAddress(BaseModel):
    """Schema for clinic address information."""
    street: str = Field(..., min_length=5, max_length=200, description="Street address")
    city: str = Field(..., min_length=2, max_length=100, description="City name")
    state: str = Field(..., min_length=2, max_length=50, description="State or province")
    zip: str = Field(..., min_length=3, max_length=20, description="ZIP or postal code")
    
    @validator('street', 'city', 'state')
    def validate_address_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Address field cannot be empty')
        return v.strip()
    
    @validator('zip')
    def validate_zip_code(cls, v):
        # Basic ZIP code validation (US format and international)
        if not re.match(r'^[\d\w\s-]{3,20}$', v):
            raise ValueError('Invalid ZIP/postal code format')
        return v.strip()


class ProviderRegistrationRequest(BaseModel):
    """Schema for provider registration request."""
    first_name: str = Field(..., min_length=2, max_length=50, description="Provider's first name")
    last_name: str = Field(..., min_length=2, max_length=50, description="Provider's last name")
    email: EmailStr = Field(..., description="Provider's email address")
    phone_number: str = Field(..., min_length=10, max_length=20, description="Provider's phone number")
    password: str = Field(..., min_length=8, max_length=128, description="Provider's password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")
    specialization: str = Field(..., min_length=3, max_length=100, description="Medical specialization")
    license_number: str = Field(..., min_length=5, max_length=50, description="Medical license number")
    years_of_experience: int = Field(..., ge=0, le=50, description="Years of medical experience")
    clinic_address: ClinicAddress = Field(..., description="Clinic address information")
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if not re.match(r'^[a-zA-Z\s\'-]+$', v):
            raise ValueError('Name can only contain letters, spaces, hyphens, and apostrophes')
        return v.strip().title()
    
    @validator('email')
    def validate_email_format(cls, v):
        # Additional email validation beyond EmailStr
        if len(v) > 254:
            raise ValueError('Email address is too long')
        return v.lower().strip()
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        try:
            # Parse and validate phone number
            parsed_number = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError('Invalid phone number')
            # Return in international format
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError('Invalid phone number format')
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for required character types
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @validator('specialization')
    def validate_specialization(cls, v):
        if v not in settings.ALLOWED_SPECIALIZATIONS:
            raise ValueError(f'Specialization must be one of: {", ".join(settings.ALLOWED_SPECIALIZATIONS)}')
        return v
    
    @validator('license_number')
    def validate_license_number(cls, v):
        # License number should be alphanumeric
        if not re.match(r'^[A-Za-z0-9]+$', v):
            raise ValueError('License number must be alphanumeric')
        return v.upper().strip()
    
    @model_validator(mode='after')
    def validate_password_match(self):
        if self.password and self.confirm_password and self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self


class ProviderResponse(BaseModel):
    """Schema for provider response data."""
    provider_id: str = Field(..., description="Unique provider identifier")
    email: str = Field(..., description="Provider's email address")
    verification_status: VerificationStatus = Field(..., description="Account verification status")


class ProviderRegistrationResponse(BaseModel):
    """Schema for provider registration response."""
    success: bool = Field(..., description="Registration success status")
    message: str = Field(..., description="Response message")
    data: ProviderResponse = Field(..., description="Provider data")


class ProviderProfile(BaseModel):
    """Schema for complete provider profile."""
    id: str = Field(..., description="Provider ID")
    first_name: str = Field(..., description="Provider's first name")
    last_name: str = Field(..., description="Provider's last name")
    email: str = Field(..., description="Provider's email address")
    phone_number: str = Field(..., description="Provider's phone number")
    specialization: str = Field(..., description="Medical specialization")
    license_number: str = Field(..., description="Medical license number")
    years_of_experience: int = Field(..., description="Years of experience")
    clinic_address: ClinicAddress = Field(..., description="Clinic address")
    verification_status: VerificationStatus = Field(..., description="Verification status")
    license_document_url: Optional[str] = Field(None, description="License document URL")
    is_active: bool = Field(..., description="Account active status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    success: bool = Field(False, description="Success status")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    success: bool = Field(False, description="Success status")
    message: str = Field("Validation failed", description="Error message")
    errors: list = Field(..., description="List of validation errors")
