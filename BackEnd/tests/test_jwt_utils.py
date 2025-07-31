"""
Unit tests for JWT utilities.
"""
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from utils.jwt_utils import JWTManager
from schemas.token import TokenType, VerificationStatus


class TestJWTManager:
    """Test cases for JWTManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.jwt_manager = JWTManager()
        self.test_provider_id = "test-provider-id"
        self.test_email = "test@example.com"
        self.test_specialization = "General Practice"
        self.test_verification_status = "verified"
        self.test_is_active = True

    def test_create_access_token(self):
        """Test access token creation."""
        # Act
        token, expires_in = self.jwt_manager.create_access_token(
            provider_id=self.test_provider_id,
            email=self.test_email,
            specialization=self.test_specialization,
            verification_status=self.test_verification_status,
            is_active=self.test_is_active,
            remember_me=False
        )
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert expires_in == 3600  # 1 hour in seconds
        
        # Decode and verify token
        payload = jwt.decode(token, self.jwt_manager.secret_key, algorithms=[self.jwt_manager.algorithm])
        assert payload["sub"] == self.test_provider_id
        assert payload["email"] == self.test_email
        assert payload["specialization"] == self.test_specialization
        assert payload["verification_status"] == self.test_verification_status
        assert payload["is_active"] == self.test_is_active
        assert payload["token_type"] == TokenType.ACCESS

    def test_create_access_token_remember_me(self):
        """Test access token creation with remember_me flag."""
        # Act
        token, expires_in = self.jwt_manager.create_access_token(
            provider_id=self.test_provider_id,
            email=self.test_email,
            specialization=self.test_specialization,
            verification_status=self.test_verification_status,
            is_active=self.test_is_active,
            remember_me=True
        )
        
        # Assert
        assert expires_in == 86400  # 24 hours in seconds

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        # Act
        token, jti, expires_at = self.jwt_manager.create_refresh_token(
            provider_id=self.test_provider_id,
            email=self.test_email,
            specialization=self.test_specialization,
            verification_status=self.test_verification_status,
            is_active=self.test_is_active,
            remember_me=False
        )
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert jti is not None
        assert isinstance(jti, str)
        assert expires_at is not None
        assert isinstance(expires_at, datetime)
        
        # Decode and verify token
        payload = jwt.decode(token, self.jwt_manager.secret_key, algorithms=[self.jwt_manager.algorithm])
        assert payload["sub"] == self.test_provider_id
        assert payload["email"] == self.test_email
        assert payload["jti"] == jti
        assert payload["token_type"] == TokenType.REFRESH

    def test_create_refresh_token_remember_me(self):
        """Test refresh token creation with remember_me flag."""
        # Act
        token, jti, expires_at = self.jwt_manager.create_refresh_token(
            provider_id=self.test_provider_id,
            email=self.test_email,
            specialization=self.test_specialization,
            verification_status=self.test_verification_status,
            is_active=self.test_is_active,
            remember_me=True
        )
        
        # Assert
        now = datetime.now(timezone.utc)
        expected_expiry = now + timedelta(days=30)
        assert abs((expires_at - expected_expiry).total_seconds()) < 5  # Within 5 seconds

    def test_decode_valid_token(self):
        """Test decoding valid token."""
        # Arrange
        token, _ = self.jwt_manager.create_access_token(
            provider_id=self.test_provider_id,
            email=self.test_email,
            specialization=self.test_specialization,
            verification_status=self.test_verification_status,
            is_active=self.test_is_active
        )
        
        # Act
        decoded = self.jwt_manager.decode_token(token)
        
        # Assert
        assert decoded.is_valid is True
        assert decoded.is_expired is False
        assert decoded.error is None
        assert decoded.payload is not None
        assert decoded.payload.sub == self.test_provider_id
        assert decoded.payload.email == self.test_email

    def test_decode_expired_token(self):
        """Test decoding expired token."""
        # Arrange - create token with past expiry
        now = datetime.now(timezone.utc)
        past_time = now - timedelta(hours=1)
        
        payload = {
            "sub": self.test_provider_id,
            "email": self.test_email,
            "specialization": self.test_specialization,
            "verification_status": self.test_verification_status,
            "is_active": self.test_is_active,
            "token_type": TokenType.ACCESS,
            "iat": int(past_time.timestamp()),
            "exp": int((past_time + timedelta(minutes=1)).timestamp())  # Expired 59 minutes ago
        }
        
        token = jwt.encode(payload, self.jwt_manager.secret_key, algorithm=self.jwt_manager.algorithm)
        
        # Act
        decoded = self.jwt_manager.decode_token(token)
        
        # Assert
        assert decoded.is_valid is False
        assert decoded.is_expired is True
        assert "expired" in decoded.error.lower()
        assert decoded.payload is None

    def test_decode_invalid_token(self):
        """Test decoding invalid token."""
        # Arrange
        invalid_token = "invalid.token.here"
        
        # Act
        decoded = self.jwt_manager.decode_token(invalid_token)
        
        # Assert
        assert decoded.is_valid is False
        assert decoded.is_expired is False
        assert decoded.error is not None
        assert decoded.payload is None

    def test_verify_access_token_valid(self):
        """Test verifying valid access token."""
        # Arrange
        token, _ = self.jwt_manager.create_access_token(
            provider_id=self.test_provider_id,
            email=self.test_email,
            specialization=self.test_specialization,
            verification_status=self.test_verification_status,
            is_active=self.test_is_active
        )
        
        # Act
        payload = self.jwt_manager.verify_access_token(token)
        
        # Assert
        assert payload is not None
        assert payload.sub == self.test_provider_id
        assert payload.token_type == TokenType.ACCESS

    def test_verify_access_token_invalid(self):
        """Test verifying invalid access token."""
        # Arrange
        invalid_token = "invalid.token.here"
        
        # Act
        payload = self.jwt_manager.verify_access_token(invalid_token)
        
        # Assert
        assert payload is None

    def test_verify_refresh_token_with_access_token(self):
        """Test verifying refresh token with access token (should fail)."""
        # Arrange
        access_token, _ = self.jwt_manager.create_access_token(
            provider_id=self.test_provider_id,
            email=self.test_email,
            specialization=self.test_specialization,
            verification_status=self.test_verification_status,
            is_active=self.test_is_active
        )
        
        # Act
        payload = self.jwt_manager.verify_refresh_token(access_token)
        
        # Assert
        assert payload is None

    def test_verify_refresh_token_valid(self):
        """Test verifying valid refresh token."""
        # Arrange
        token, jti, _ = self.jwt_manager.create_refresh_token(
            provider_id=self.test_provider_id,
            email=self.test_email,
            specialization=self.test_specialization,
            verification_status=self.test_verification_status,
            is_active=self.test_is_active
        )
        
        # Act
        payload = self.jwt_manager.verify_refresh_token(token)
        
        # Assert
        assert payload is not None
        assert payload.sub == self.test_provider_id
        assert payload.token_type == TokenType.REFRESH
        assert payload.jti == jti

    def test_extract_token_from_header_valid(self):
        """Test extracting token from valid Authorization header."""
        # Arrange
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
        authorization = f"Bearer {token}"
        
        # Act
        extracted_token = self.jwt_manager.extract_token_from_header(authorization)
        
        # Assert
        assert extracted_token == token

    def test_extract_token_from_header_invalid_scheme(self):
        """Test extracting token from header with invalid scheme."""
        # Arrange
        authorization = "Basic dGVzdDp0ZXN0"
        
        # Act
        extracted_token = self.jwt_manager.extract_token_from_header(authorization)
        
        # Assert
        assert extracted_token is None

    def test_extract_token_from_header_malformed(self):
        """Test extracting token from malformed header."""
        # Arrange
        authorization = "BearerTokenWithoutSpace"
        
        # Act
        extracted_token = self.jwt_manager.extract_token_from_header(authorization)
        
        # Assert
        assert extracted_token is None

    def test_extract_token_from_header_empty(self):
        """Test extracting token from empty header."""
        # Act
        extracted_token = self.jwt_manager.extract_token_from_header("")
        
        # Assert
        assert extracted_token is None

    def test_get_token_expiry_info_valid(self):
        """Test getting expiry info for valid token."""
        # Arrange
        token, _ = self.jwt_manager.create_access_token(
            provider_id=self.test_provider_id,
            email=self.test_email,
            specialization=self.test_specialization,
            verification_status=self.test_verification_status,
            is_active=self.test_is_active
        )
        
        # Act
        expiry_info = self.jwt_manager.get_token_expiry_info(token)
        
        # Assert
        assert "expires_at" in expiry_info
        assert "is_expired" in expiry_info
        assert "time_remaining" in expiry_info
        assert expiry_info["is_expired"] is False
        assert expiry_info["time_remaining"] > 0

    def test_get_token_expiry_info_invalid(self):
        """Test getting expiry info for invalid token."""
        # Arrange
        invalid_token = "invalid.token.here"
        
        # Act
        expiry_info = self.jwt_manager.get_token_expiry_info(invalid_token)
        
        # Assert
        assert "error" in expiry_info
        assert expiry_info["error"] is not None
