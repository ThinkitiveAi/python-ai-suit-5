"""
Pydantic schemas for provider authentication endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator


class ProviderLoginRequest(BaseModel):
    """Request schema for provider login."""
    email: EmailStr = Field(
        ...,
        description="Provider's email address"
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Provider's password"
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password is not empty."""
        if not v or not v.strip():
            raise ValueError('Password cannot be empty')
        return v


class ProviderData(BaseModel):
    """Provider data included in login response."""
    id: str = Field(..., description="Provider ID")
    first_name: str = Field(..., description="Provider's first name")
    last_name: str = Field(..., description="Provider's last name")
    email: str = Field(..., description="Provider's email address")
    phone_number: str = Field(..., description="Provider's phone number")
    specialization: str = Field(..., description="Provider's specialization")
    license_number: str = Field(..., description="Provider's license number")
    years_of_experience: int = Field(..., description="Years of experience")
    verification_status: str = Field(..., description="Account verification status")
    is_active: bool = Field(..., description="Account active status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


class ProviderLoginData(BaseModel):
    """Login response data."""
    access_token: str = Field(..., description="JWT access token")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    token_type: str = Field(default="Bearer", description="Token type")
    provider: ProviderData = Field(..., description="Provider information")


class ProviderLoginResponse(BaseModel):
    """Response schema for successful provider login."""
    success: bool = True
    message: str = "Login successful"
    data: ProviderLoginData
