"""
Pydantic schemas for JWT token payload structure.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class TokenType(str, Enum):
    """Token type enumeration."""
    ACCESS = "access"
    REFRESH = "refresh"


class VerificationStatus(str, Enum):
    """Provider verification status."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class JWTPayload(BaseModel):
    """JWT token payload schema."""
    sub: str = Field(..., description="Subject (provider_id)")
    email: str = Field(..., description="Provider email")
    role: str = Field(default="provider", description="User role")
    specialization: str = Field(..., description="Medical specialization")
    verification_status: VerificationStatus = Field(..., description="Account verification status")
    is_active: bool = Field(..., description="Account active status")
    token_type: TokenType = Field(..., description="Token type (access/refresh)")
    iat: int = Field(..., description="Issued at timestamp")
    exp: int = Field(..., description="Expiration timestamp")
    jti: Optional[str] = Field(None, description="JWT ID for refresh tokens")


class AccessTokenPayload(JWTPayload):
    """Access token specific payload."""
    token_type: TokenType = Field(default=TokenType.ACCESS, description="Access token type")


class RefreshTokenPayload(JWTPayload):
    """Refresh token specific payload."""
    token_type: TokenType = Field(default=TokenType.REFRESH, description="Refresh token type")
    jti: str = Field(..., description="JWT ID for token tracking")


class TokenPair(BaseModel):
    """Token pair response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    token_type: str = Field(default="Bearer", description="Token type")


class DecodedToken(BaseModel):
    """Decoded JWT token information."""
    payload: JWTPayload = Field(..., description="Token payload")
    is_valid: bool = Field(..., description="Token validity status")
    is_expired: bool = Field(..., description="Token expiration status")
    error: Optional[str] = Field(None, description="Error message if invalid")
