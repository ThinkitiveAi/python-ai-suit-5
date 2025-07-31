"""
Unit tests for authentication service.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from services.auth_service import AuthService
from schemas.auth import LoginRequest
from db.models.provider import Provider
from db.models.refresh_token import RefreshToken
from utils.password_utils import hash_password


class TestAuthService:
    """Test cases for AuthService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.auth_service = AuthService()
        self.mock_db = Mock(spec=Session)
        
        # Create test provider
        self.test_provider = Provider(
            id="test-provider-id",
            email="test@example.com",
            phone_number="+1-555-123-4567",
            password_hash=hash_password("TestPassword123!"),
            first_name="Test",
            last_name="Provider",
            specialization="General Practice",
            license_number="TEST123456",
            years_of_experience=5,
            verification_status="verified",
            is_active=True,
            failed_login_attempts=0,
            locked_until=None,
            login_count=0
        )

    def test_authenticate_provider_success(self):
        """Test successful provider authentication."""
        # Arrange
        login_request = LoginRequest(
            identifier="test@example.com",
            password="TestPassword123!",
            remember_me=False
        )
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.test_provider
        
        # Act
        success, login_data, error_message, lock_info = self.auth_service.authenticate_provider(
            self.mock_db, login_request
        )
        
        # Assert
        assert success is True
        assert login_data is not None
        assert error_message is None
        assert lock_info is None
        assert login_data.access_token is not None
        assert login_data.refresh_token is not None
        assert login_data.provider.email == "test@example.com"

    def test_authenticate_provider_invalid_credentials(self):
        """Test authentication with invalid credentials."""
        # Arrange
        login_request = LoginRequest(
            identifier="test@example.com",
            password="WrongPassword123!",
            remember_me=False
        )
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.test_provider
        
        # Act
        success, login_data, error_message, lock_info = self.auth_service.authenticate_provider(
            self.mock_db, login_request
        )
        
        # Assert
        assert success is False
        assert login_data is None
        assert error_message == "Invalid credentials"
        assert lock_info is None

    def test_authenticate_provider_not_found(self):
        """Test authentication with non-existent provider."""
        # Arrange
        login_request = LoginRequest(
            identifier="nonexistent@example.com",
            password="TestPassword123!",
            remember_me=False
        )
        
        # Mock database query to return None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        success, login_data, error_message, lock_info = self.auth_service.authenticate_provider(
            self.mock_db, login_request
        )
        
        # Assert
        assert success is False
        assert login_data is None
        assert error_message == "Invalid credentials"
        assert lock_info is None

    def test_authenticate_provider_inactive_account(self):
        """Test authentication with inactive account."""
        # Arrange
        self.test_provider.is_active = False
        login_request = LoginRequest(
            identifier="test@example.com",
            password="TestPassword123!",
            remember_me=False
        )
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.test_provider
        
        # Act
        success, login_data, error_message, lock_info = self.auth_service.authenticate_provider(
            self.mock_db, login_request
        )
        
        # Assert
        assert success is False
        assert login_data is None
        assert error_message == "Account is inactive"
        assert lock_info is None

    def test_authenticate_provider_locked_account(self):
        """Test authentication with locked account."""
        # Arrange
        self.test_provider.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        login_request = LoginRequest(
            identifier="test@example.com",
            password="TestPassword123!",
            remember_me=False
        )
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.test_provider
        
        # Act
        success, login_data, error_message, lock_info = self.auth_service.authenticate_provider(
            self.mock_db, login_request
        )
        
        # Assert
        assert success is False
        assert login_data is None
        assert error_message == "Account locked"
        assert lock_info is not None
        assert "locked_until" in lock_info

    def test_failed_login_attempts_increment(self):
        """Test that failed login attempts are incremented."""
        # Arrange
        login_request = LoginRequest(
            identifier="test@example.com",
            password="WrongPassword123!",
            remember_me=False
        )
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.test_provider
        
        initial_attempts = self.test_provider.failed_login_attempts
        
        # Act
        self.auth_service.authenticate_provider(self.mock_db, login_request)
        
        # Assert
        assert self.test_provider.failed_login_attempts == initial_attempts + 1

    def test_account_lockout_after_max_attempts(self):
        """Test account lockout after maximum failed attempts."""
        # Arrange
        self.test_provider.failed_login_attempts = 4  # One less than max
        login_request = LoginRequest(
            identifier="test@example.com",
            password="WrongPassword123!",
            remember_me=False
        )
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.test_provider
        
        # Act
        success, login_data, error_message, lock_info = self.auth_service.authenticate_provider(
            self.mock_db, login_request
        )
        
        # Assert
        assert success is False
        assert self.test_provider.failed_login_attempts == 5
        assert self.test_provider.locked_until is not None
        assert lock_info is not None

    def test_successful_login_resets_failed_attempts(self):
        """Test that successful login resets failed attempts."""
        # Arrange
        self.test_provider.failed_login_attempts = 3
        self.test_provider.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)  # Expired lock
        
        login_request = LoginRequest(
            identifier="test@example.com",
            password="TestPassword123!",
            remember_me=False
        )
        
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.test_provider
        
        # Act
        success, login_data, error_message, lock_info = self.auth_service.authenticate_provider(
            self.mock_db, login_request
        )
        
        # Assert
        assert success is True
        assert self.test_provider.failed_login_attempts == 0
        assert self.test_provider.locked_until is None
        assert self.test_provider.login_count == 1

    @patch('services.auth_service.jwt_manager')
    def test_refresh_access_token_success(self, mock_jwt_manager):
        """Test successful token refresh."""
        # Arrange
        refresh_token = "valid_refresh_token"
        mock_payload = Mock()
        mock_payload.sub = "test-provider-id"
        
        mock_jwt_manager.verify_refresh_token.return_value = mock_payload
        mock_jwt_manager.create_access_token.return_value = ("new_access_token", 3600)
        
        # Mock refresh token in database
        mock_refresh_token = Mock(spec=RefreshToken)
        mock_refresh_token.provider_id = "test-provider-id"
        mock_refresh_token.is_valid = True
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_refresh_token
        
        # Mock provider query
        provider_query = Mock()
        provider_query.filter.return_value.first.return_value = self.test_provider
        self.mock_db.query.side_effect = [Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_refresh_token))))), provider_query]
        
        # Act
        success, access_token, expires_in, error_message = self.auth_service.refresh_access_token(
            self.mock_db, refresh_token
        )
        
        # Assert
        assert success is True
        assert access_token == "new_access_token"
        assert expires_in == 3600
        assert error_message is None

    @patch('services.auth_service.jwt_manager')
    def test_refresh_access_token_invalid_token(self, mock_jwt_manager):
        """Test token refresh with invalid token."""
        # Arrange
        refresh_token = "invalid_refresh_token"
        mock_jwt_manager.verify_refresh_token.return_value = None
        
        # Act
        success, access_token, expires_in, error_message = self.auth_service.refresh_access_token(
            self.mock_db, refresh_token
        )
        
        # Assert
        assert success is False
        assert access_token is None
        assert expires_in is None
        assert error_message == "Invalid refresh token"

    def test_logout_provider_success(self):
        """Test successful provider logout."""
        # Arrange
        refresh_token = "valid_refresh_token"
        mock_refresh_token = Mock(spec=RefreshToken)
        mock_refresh_token.provider_id = "test-provider-id"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_refresh_token
        
        # Act
        success, error_message = self.auth_service.logout_provider(self.mock_db, refresh_token)
        
        # Assert
        assert success is True
        assert error_message is None
        mock_refresh_token.revoke.assert_called_once()

    def test_logout_all_sessions_success(self):
        """Test successful logout from all sessions."""
        # Arrange
        provider_id = "test-provider-id"
        mock_query = Mock()
        self.mock_db.query.return_value.filter.return_value.update.return_value = None
        
        # Act
        success, error_message = self.auth_service.logout_all_sessions(self.mock_db, provider_id)
        
        # Assert
        assert success is True
        assert error_message is None

    def test_find_provider_by_email(self):
        """Test finding provider by email."""
        # Arrange
        identifier = "test@example.com"
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.test_provider
        
        # Act
        provider = self.auth_service._find_provider_by_identifier(self.mock_db, identifier)
        
        # Assert
        assert provider == self.test_provider

    def test_find_provider_by_phone(self):
        """Test finding provider by phone number."""
        # Arrange
        identifier = "+1-555-123-4567"
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.test_provider
        
        # Act
        provider = self.auth_service._find_provider_by_identifier(self.mock_db, identifier)
        
        # Assert
        assert provider == self.test_provider

    def test_is_account_locked_true(self):
        """Test account lock check when account is locked."""
        # Arrange
        self.test_provider.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        # Act
        is_locked = self.auth_service._is_account_locked(self.test_provider)
        
        # Assert
        assert is_locked is True

    def test_is_account_locked_false(self):
        """Test account lock check when account is not locked."""
        # Arrange
        self.test_provider.locked_until = None
        
        # Act
        is_locked = self.auth_service._is_account_locked(self.test_provider)
        
        # Assert
        assert is_locked is False

    def test_is_account_locked_expired(self):
        """Test account lock check when lock has expired."""
        # Arrange
        self.test_provider.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)
        
        # Act
        is_locked = self.auth_service._is_account_locked(self.test_provider)
        
        # Assert
        assert is_locked is False
