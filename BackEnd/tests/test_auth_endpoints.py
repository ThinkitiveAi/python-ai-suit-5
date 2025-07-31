"""
Integration tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from main import app
from db.database import get_db, Base
from db.models.provider import Provider
from db.models.refresh_token import RefreshToken
from utils.password_utils import hash_password


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def setup_database():
    """Set up test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_database):
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_provider():
    """Create test provider in database."""
    db = TestingSessionLocal()
    try:
        provider = Provider(
            email="test@example.com",
            password_hash=hash_password("TestPassword123!"),
            first_name="Test",
            last_name="Provider",
            phone_number="+1-555-123-4567",
            specialization="General Practice",
            license_number="TEST123456",
            years_of_experience=5,
            verification_status="verified",
            is_active=True,
            failed_login_attempts=0,
            login_count=0
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)
        yield provider
    finally:
        db.query(RefreshToken).filter(RefreshToken.provider_id == provider.id).delete()
        db.query(Provider).filter(Provider.id == provider.id).delete()
        db.commit()
        db.close()


class TestAuthEndpoints:
    """Integration tests for authentication endpoints."""

    def test_login_success(self, client, test_provider):
        """Test successful login."""
        # Arrange
        login_data = {
            "identifier": "test@example.com",
            "password": "TestPassword123!",
            "remember_me": False
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert "expires_in" in data["data"]
        assert data["data"]["token_type"] == "Bearer"
        assert data["data"]["provider"]["email"] == "test@example.com"

    def test_login_with_phone_number(self, client, test_provider):
        """Test login with phone number."""
        # Arrange
        login_data = {
            "identifier": "+1-555-123-4567",
            "password": "TestPassword123!",
            "remember_me": False
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_login_remember_me(self, client, test_provider):
        """Test login with remember_me flag."""
        # Arrange
        login_data = {
            "identifier": "test@example.com",
            "password": "TestPassword123!",
            "remember_me": True
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["expires_in"] == 86400  # 24 hours

    def test_login_invalid_credentials(self, client, test_provider):
        """Test login with invalid credentials."""
        # Arrange
        login_data = {
            "identifier": "test@example.com",
            "password": "WrongPassword123!",
            "remember_me": False
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_CREDENTIALS"

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        # Arrange
        login_data = {
            "identifier": "nonexistent@example.com",
            "password": "TestPassword123!",
            "remember_me": False
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

    def test_login_validation_errors(self, client):
        """Test login with validation errors."""
        # Arrange - missing password
        login_data = {
            "identifier": "test@example.com",
            "remember_me": False
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 422

    def test_refresh_token_success(self, client, test_provider):
        """Test successful token refresh."""
        # Arrange - first login to get tokens
        login_data = {
            "identifier": "test@example.com",
            "password": "TestPassword123!",
            "remember_me": False
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # Act
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "expires_in" in data["data"]

    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid token."""
        # Arrange
        refresh_data = {"refresh_token": "invalid_token"}
        
        # Act
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "INVALID_REFRESH_TOKEN"

    def test_get_current_provider(self, client, test_provider):
        """Test getting current provider information."""
        # Arrange - login to get access token
        login_data = {
            "identifier": "test@example.com",
            "password": "TestPassword123!",
            "remember_me": False
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["data"]["access_token"]
        
        # Act
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "test@example.com"
        assert data["data"]["first_name"] == "Test"

    def test_get_current_provider_unauthorized(self, client):
        """Test getting current provider without authentication."""
        # Act
        response = client.get("/api/v1/auth/me")
        
        # Assert
        assert response.status_code == 401

    def test_get_current_provider_invalid_token(self, client):
        """Test getting current provider with invalid token."""
        # Act
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        # Assert
        assert response.status_code == 401

    def test_verify_token_success(self, client, test_provider):
        """Test token verification."""
        # Arrange - login to get access token
        login_data = {
            "identifier": "test@example.com",
            "password": "TestPassword123!",
            "remember_me": False
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["data"]["access_token"]
        
        # Act
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/token/verify", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "test@example.com"
        assert data["data"]["is_active"] is True

    def test_logout_success(self, client, test_provider):
        """Test successful logout."""
        # Arrange - login to get tokens
        login_data = {
            "identifier": "test@example.com",
            "password": "TestPassword123!",
            "remember_me": False
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()["data"]
        
        # Act
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        logout_data = {"refresh_token": tokens["refresh_token"]}
        response = client.post("/api/v1/auth/logout", json=logout_data, headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_logout_unauthorized(self, client):
        """Test logout without authentication."""
        # Act
        logout_data = {"refresh_token": "some_token"}
        response = client.post("/api/v1/auth/logout", json=logout_data)
        
        # Assert
        assert response.status_code == 401

    def test_logout_all_success(self, client, test_provider):
        """Test successful logout from all sessions."""
        # Arrange - login to get access token
        login_data = {
            "identifier": "test@example.com",
            "password": "TestPassword123!",
            "remember_me": False
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["data"]["access_token"]
        
        # Act
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/auth/logout-all", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_logout_all_unauthorized(self, client):
        """Test logout all without authentication."""
        # Act
        response = client.post("/api/v1/auth/logout-all")
        
        # Assert
        assert response.status_code == 401

    @patch('middlewares.rate_limiting.get_client_ip')
    def test_login_rate_limiting(self, mock_get_ip, client, test_provider):
        """Test rate limiting on login endpoint."""
        # Arrange
        mock_get_ip.return_value = "127.0.0.1"
        login_data = {
            "identifier": "test@example.com",
            "password": "WrongPassword123!",
            "remember_me": False
        }
        
        # Act - make multiple requests
        responses = []
        for _ in range(12):  # Exceed rate limit
            response = client.post("/api/v1/auth/login", json=login_data)
            responses.append(response.status_code)
        
        # Assert - should eventually get rate limited
        assert 429 in responses  # Rate limit exceeded

    def test_account_lockout(self, client, test_provider):
        """Test account lockout after failed attempts."""
        # Arrange
        login_data = {
            "identifier": "test@example.com",
            "password": "WrongPassword123!",
            "remember_me": False
        }
        
        # Act - make multiple failed login attempts
        for _ in range(5):  # Max failed attempts
            client.post("/api/v1/auth/login", json=login_data)
        
        # Try one more time - should be locked
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 423  # Locked
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "ACCOUNT_LOCKED"
        assert "details" in data

    def test_successful_login_resets_failed_attempts(self, client, test_provider):
        """Test that successful login resets failed attempts."""
        # Arrange - make some failed attempts
        failed_login_data = {
            "identifier": "test@example.com",
            "password": "WrongPassword123!",
            "remember_me": False
        }
        
        for _ in range(3):
            client.post("/api/v1/auth/login", json=failed_login_data)
        
        # Act - successful login
        success_login_data = {
            "identifier": "test@example.com",
            "password": "TestPassword123!",
            "remember_me": False
        }
        response = client.post("/api/v1/auth/login", json=success_login_data)
        
        # Assert
        assert response.status_code == 200
        
        # Verify failed attempts were reset by checking database
        db = TestingSessionLocal()
        provider = db.query(Provider).filter(Provider.email == "test@example.com").first()
        assert provider.failed_login_attempts == 0
        db.close()
