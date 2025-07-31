"""
Unit tests for provider authentication functionality.
"""
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from main import app
from db.models.provider import Provider
from services.provider_auth_service import provider_auth_service
from schemas.provider_auth import ProviderLoginRequest
from core.security import security


class TestProviderAuthService:
    """Test cases for ProviderAuthService."""
    
    def test_authenticate_provider_success(self, db_session: Session, sample_provider: Provider):
        """Test successful provider authentication."""
        # Arrange
        login_request = ProviderLoginRequest(
            email=sample_provider.email,
            password="TestPassword123!"
        )
        
        # Mock password verification to return True
        with patch.object(security, 'verify_password', return_value=True):
            with patch.object(security, 'create_access_token', return_value="mock_jwt_token"):
                # Act
                success, login_data, error_message = provider_auth_service.authenticate_provider(
                    db_session, login_request
                )
        
        # Assert
        assert success is True
        assert login_data is not None
        assert error_message is None
        assert login_data.access_token == "mock_jwt_token"
        assert login_data.expires_in == 3600
        assert login_data.token_type == "Bearer"
        assert login_data.provider.email == sample_provider.email
    
    def test_authenticate_provider_invalid_email(self, db_session: Session):
        """Test authentication with invalid email."""
        # Arrange
        login_request = ProviderLoginRequest(
            email="nonexistent@example.com",
            password="TestPassword123!"
        )
        
        # Act
        success, login_data, error_message = provider_auth_service.authenticate_provider(
            db_session, login_request
        )
        
        # Assert
        assert success is False
        assert login_data is None
        assert error_message == "Invalid credentials"
    
    def test_authenticate_provider_invalid_password(self, db_session: Session, sample_provider: Provider):
        """Test authentication with invalid password."""
        # Arrange
        login_request = ProviderLoginRequest(
            email=sample_provider.email,
            password="WrongPassword"
        )
        
        # Mock password verification to return False
        with patch.object(security, 'verify_password', return_value=False):
            # Act
            success, login_data, error_message = provider_auth_service.authenticate_provider(
                db_session, login_request
            )
        
        # Assert
        assert success is False
        assert login_data is None
        assert error_message == "Invalid credentials"
        
        # Check that failed attempts were incremented
        db_session.refresh(sample_provider)
        assert sample_provider.failed_login_attempts == 1
    
    def test_authenticate_provider_inactive_account(self, db_session: Session, sample_provider: Provider):
        """Test authentication with inactive account."""
        # Arrange
        sample_provider.is_active = False
        db_session.commit()
        
        login_request = ProviderLoginRequest(
            email=sample_provider.email,
            password="TestPassword123!"
        )
        
        # Act
        success, login_data, error_message = provider_auth_service.authenticate_provider(
            db_session, login_request
        )
        
        # Assert
        assert success is False
        assert login_data is None
        assert error_message == "Account is inactive"
    
    def test_authenticate_provider_locked_account(self, db_session: Session, sample_provider: Provider):
        """Test authentication with locked account."""
        # Arrange
        sample_provider.locked_until = datetime.now(timezone.utc) + timedelta(minutes=10)
        db_session.commit()
        
        login_request = ProviderLoginRequest(
            email=sample_provider.email,
            password="TestPassword123!"
        )
        
        # Act
        success, login_data, error_message = provider_auth_service.authenticate_provider(
            db_session, login_request
        )
        
        # Assert
        assert success is False
        assert login_data is None
        assert error_message == "Account is temporarily locked"
    
    def test_authenticate_provider_account_lockout(self, db_session: Session, sample_provider: Provider):
        """Test account lockout after multiple failed attempts."""
        # Arrange
        sample_provider.failed_login_attempts = 4  # One more attempt will lock the account
        db_session.commit()
        
        login_request = ProviderLoginRequest(
            email=sample_provider.email,
            password="WrongPassword"
        )
        
        # Mock password verification to return False
        with patch.object(security, 'verify_password', return_value=False):
            # Act
            success, login_data, error_message = provider_auth_service.authenticate_provider(
                db_session, login_request
            )
        
        # Assert
        assert success is False
        assert login_data is None
        assert error_message == "Invalid credentials"
        
        # Check that account is now locked
        db_session.refresh(sample_provider)
        assert sample_provider.failed_login_attempts == 5
        assert sample_provider.locked_until is not None
        assert sample_provider.locked_until > datetime.now(timezone.utc)


class TestProviderAuthEndpoint:
    """Test cases for provider authentication endpoint."""
    
    def test_provider_login_success(self, client: TestClient, db_session: Session, sample_provider: Provider):
        """Test successful provider login endpoint."""
        # Arrange
        login_data = {
            "email": sample_provider.email,
            "password": "TestPassword123!"
        }
        
        # Mock the authentication service
        with patch.object(provider_auth_service, 'authenticate_provider') as mock_auth:
            mock_login_data = MagicMock()
            mock_login_data.access_token = "mock_jwt_token"
            mock_login_data.expires_in = 3600
            mock_login_data.token_type = "Bearer"
            mock_login_data.provider.email = sample_provider.email
            
            mock_auth.return_value = (True, mock_login_data, None)
            
            # Act
            response = client.post("/api/v1/provider/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["message"] == "Login successful"
        assert "data" in response_data
        assert "access_token" in response_data["data"]
    
    def test_provider_login_invalid_credentials(self, client: TestClient):
        """Test provider login with invalid credentials."""
        # Arrange
        login_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        # Mock the authentication service to return failure
        with patch.object(provider_auth_service, 'authenticate_provider') as mock_auth:
            mock_auth.return_value = (False, None, "Invalid credentials")
            
            # Act
            response = client.post("/api/v1/provider/login", json=login_data)
        
        # Assert
        assert response.status_code == 401
        response_data = response.json()
        assert response_data["success"] is False
        assert "Invalid credentials" in response_data["message"]
    
    def test_provider_login_validation_error(self, client: TestClient):
        """Test provider login with validation errors."""
        # Arrange
        login_data = {
            "email": "invalid-email",  # Invalid email format
            "password": ""  # Empty password
        }
        
        # Act
        response = client.post("/api/v1/provider/login", json=login_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_provider_login_missing_fields(self, client: TestClient):
        """Test provider login with missing required fields."""
        # Arrange
        login_data = {
            "email": "test@example.com"
            # Missing password field
        }
        
        # Act
        response = client.post("/api/v1/provider/login", json=login_data)
        
        # Assert
        assert response.status_code == 422  # Validation error


class TestJWTTokenGeneration:
    """Test cases for JWT token generation and validation."""
    
    def test_create_access_token(self):
        """Test JWT access token creation."""
        # Arrange
        token_data = {
            "provider_id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "role": "provider",
            "specialization": "cardiology"
        }
        
        # Act
        token = security.create_access_token(
            data=token_data,
            expires_delta=timedelta(hours=1)
        )
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_access_token(self):
        """Test JWT access token verification."""
        # Arrange
        token_data = {
            "provider_id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "role": "provider",
            "specialization": "cardiology"
        }
        
        token = security.create_access_token(
            data=token_data,
            expires_delta=timedelta(hours=1)
        )
        
        # Act
        payload = security.verify_token(token)
        
        # Assert
        assert payload is not None
        assert payload["provider_id"] == token_data["provider_id"]
        assert payload["email"] == token_data["email"]
        assert payload["role"] == token_data["role"]
        assert payload["specialization"] == token_data["specialization"]
        assert "exp" in payload
    
    def test_verify_invalid_token(self):
        """Test verification of invalid JWT token."""
        # Arrange
        invalid_token = "invalid.jwt.token"
        
        # Act
        payload = security.verify_token(invalid_token)
        
        # Assert
        assert payload is None
    
    def test_verify_expired_token(self):
        """Test verification of expired JWT token."""
        # Arrange
        token_data = {
            "provider_id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "role": "provider",
            "specialization": "cardiology"
        }
        
        # Create token with very short expiry
        token = security.create_access_token(
            data=token_data,
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # Act
        payload = security.verify_token(token)
        
        # Assert
        assert payload is None


# Pytest fixtures
@pytest.fixture
def sample_provider(db_session: Session) -> Provider:
    """Create a sample provider for testing."""
    provider = Provider(
        first_name="John",
        last_name="Doe",
        email="john.doe@clinic.com",
        phone_number="+1234567890",
        password_hash=security.hash_password("TestPassword123!"),
        specialization="cardiology",
        license_number="LIC123456",
        years_of_experience=5,
        clinic_address={"street": "123 Main St", "city": "Test City"},
        verification_status="verified",
        is_active=True,
        failed_login_attempts=0,
        locked_until=None
    )
    
    db_session.add(provider)
    db_session.commit()
    db_session.refresh(provider)
    
    return provider


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)
