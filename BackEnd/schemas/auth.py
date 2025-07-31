"""
Pydantic schemas for authentication endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from schemas.provider import ProviderResponse


class LoginRequest(BaseModel):
    """Request schema for provider login."""
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Email address or phone number"
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Provider's password"
    )
    remember_me: bool = Field(
        default=False,
        description="Extend token expiry for longer sessions"
    )

    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v):
        """Validate identifier is not empty."""
        if not v or not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password is not empty."""
        if not v or not v.strip():
            raise ValueError('Password cannot be empty')
        return v


class LoginResponse(BaseModel):
    """Response schema for successful login."""
    success: bool = True
    message: str = "Login successful"
    data: 'LoginData'


class LoginData(BaseModel):
    """Login response data."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    token_type: str = Field(default="Bearer", description="Token type")
    provider: ProviderResponse = Field(..., description="Provider information")


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str = Field(
        ...,
        min_length=1,
        description="Valid refresh token"
    )

    @field_validator('refresh_token')
    @classmethod
    def validate_refresh_token(cls, v):
        """Validate refresh token is not empty."""
        if not v or not v.strip():
            raise ValueError('Refresh token cannot be empty')
        return v.strip()


class RefreshTokenResponse(BaseModel):
    """Response schema for token refresh."""
    success: bool = True
    message: str = "Token refreshed successfully"
    data: 'RefreshTokenData'


class RefreshTokenData(BaseModel):
    """Token refresh response data."""
    access_token: str = Field(..., description="New JWT access token")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    token_type: str = Field(default="Bearer", description="Token type")


class LogoutRequest(BaseModel):
    """Request schema for logout."""
    refresh_token: str = Field(
        ...,
        min_length=1,
        description="Refresh token to invalidate"
    )

    @field_validator('refresh_token')
    @classmethod
    def validate_refresh_token(cls, v):
        """Validate refresh token is not empty."""
        if not v or not v.strip():
            raise ValueError('Refresh token cannot be empty')
        return v.strip()


class LogoutResponse(BaseModel):
    """Response schema for logout."""
    success: bool = True
    message: str = "Logged out successfully"


class LogoutAllResponse(BaseModel):
    """Response schema for logout all sessions."""
    success: bool = True
    message: str = "All sessions logged out successfully"


class AuthErrorResponse(BaseModel):
    """Error response schema for authentication."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


class AccountLockedResponse(BaseModel):
    """Response schema for locked account."""
    success: bool = False
    message: str = "Account locked due to too many failed attempts"
    error_code: str = "ACCOUNT_LOCKED"
    details: dict = Field(..., description="Lock details including unlock time")


# Update forward references
LoginResponse.model_rebuild()
RefreshTokenResponse.model_rebuild()
