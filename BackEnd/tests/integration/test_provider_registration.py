"""
Integration tests for provider registration endpoint.
"""
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from core.config import settings
from db.database import Base, engine


class TestProviderRegistration:
    """Integration tests for provider registration."""
    
    @pytest.fixture(scope="class")
    def setup_database(self):
        """Set up test database."""
        # Create tables for testing
        Base.metadata.create_all(bind=engine)
        yield
        # Clean up after tests
        Base.metadata.drop_all(bind=engine)
    
    @pytest.fixture
    def client(self, setup_database):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def valid_provider_data(self):
        """Valid provider registration data."""
        return {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "specialization": "Cardiology",
            "license_number": "MD123456",
            "years_of_experience": 10,
            "clinic_address": {
                "street": "123 Medical Center Drive",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            }
        }
    
    def test_successful_registration(self, client, valid_provider_data):
        """Test successful provider registration."""
        with patch('services.email_service.email_service.send_verification_email', 
                   return_value=AsyncMock(return_value=True)):
            response = client.post("/api/v1/provider/register", json=valid_provider_data)
            
            assert response.status_code == 201
            data = response.json()
            
            assert data["success"] is True
            assert "registered successfully" in data["message"]
            assert "data" in data
            assert "provider_id" in data["data"]
            assert data["data"]["email"] == valid_provider_data["email"]
            assert data["data"]["verification_status"] == "pending"
    
    def test_duplicate_email_registration(self, client, valid_provider_data):
        """Test registration with duplicate email."""
        # First registration
        with patch('services.email_service.email_service.send_verification_email', 
                   return_value=AsyncMock(return_value=True)):
            response1 = client.post("/api/v1/provider/register", json=valid_provider_data)
            assert response1.status_code == 201
        
        # Second registration with same email
        duplicate_data = valid_provider_data.copy()
        duplicate_data["phone_number"] = "+1987654321"  # Different phone
        duplicate_data["license_number"] = "MD654321"   # Different license
        
        response2 = client.post("/api/v1/provider/register", json=duplicate_data)
        
        assert response2.status_code == 409
        data = response2.json()
        
        assert data["success"] is False
        assert "email address already exists" in data["message"]
    
    def test_duplicate_phone_registration(self, client, valid_provider_data):
        """Test registration with duplicate phone number."""
        # First registration
        with patch('services.email_service.email_service.send_verification_email', 
                   return_value=AsyncMock(return_value=True)):
            response1 = client.post("/api/v1/provider/register", json=valid_provider_data)
            assert response1.status_code == 201
        
        # Second registration with same phone
        duplicate_data = valid_provider_data.copy()
        duplicate_data["email"] = "different@example.com"  # Different email
        duplicate_data["license_number"] = "MD654321"      # Different license
        
        response2 = client.post("/api/v1/provider/register", json=duplicate_data)
        
        assert response2.status_code == 409
        data = response2.json()
        
        assert data["success"] is False
        assert "phone number already exists" in data["message"]
    
    def test_duplicate_license_registration(self, client, valid_provider_data):
        """Test registration with duplicate license number."""
        # First registration
        with patch('services.email_service.email_service.send_verification_email', 
                   return_value=AsyncMock(return_value=True)):
            response1 = client.post("/api/v1/provider/register", json=valid_provider_data)
            assert response1.status_code == 201
        
        # Second registration with same license
        duplicate_data = valid_provider_data.copy()
        duplicate_data["email"] = "different@example.com"  # Different email
        duplicate_data["phone_number"] = "+1987654321"     # Different phone
        
        response2 = client.post("/api/v1/provider/register", json=duplicate_data)
        
        assert response2.status_code == 409
        data = response2.json()
        
        assert data["success"] is False
        assert "license number already exists" in data["message"]
    
    def test_password_mismatch(self, client, valid_provider_data):
        """Test registration with password mismatch."""
        invalid_data = valid_provider_data.copy()
        invalid_data["confirm_password"] = "DifferentPassword123!"
        
        response = client.post("/api/v1/provider/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["success"] is False
        assert "Passwords do not match" in str(data["details"])
    
    def test_invalid_email_format(self, client, valid_provider_data):
        """Test registration with invalid email format."""
        invalid_data = valid_provider_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = client.post("/api/v1/provider/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["success"] is False
        assert "errors" in data
    
    def test_weak_password(self, client, valid_provider_data):
        """Test registration with weak password."""
        invalid_data = valid_provider_data.copy()
        invalid_data["password"] = "weak"
        invalid_data["confirm_password"] = "weak"
        
        response = client.post("/api/v1/provider/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["success"] is False
        assert "details" in data
    
    def test_invalid_specialization(self, client, valid_provider_data):
        """Test registration with invalid specialization."""
        invalid_data = valid_provider_data.copy()
        invalid_data["specialization"] = "InvalidSpecialization"
        
        response = client.post("/api/v1/provider/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["success"] is False
        assert "details" in data
    
    def test_invalid_phone_number(self, client, valid_provider_data):
        """Test registration with invalid phone number."""
        invalid_data = valid_provider_data.copy()
        invalid_data["phone_number"] = "invalid-phone"
        
        response = client.post("/api/v1/provider/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["success"] is False
        assert "errors" in data
    
    def test_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_data = {
            "first_name": "John",
            "email": "john@example.com"
            # Missing other required fields
        }
        
        response = client.post("/api/v1/provider/register", json=incomplete_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["success"] is False
        assert "errors" in data
    
    def test_invalid_years_of_experience(self, client, valid_provider_data):
        """Test registration with invalid years of experience."""
        invalid_data = valid_provider_data.copy()
        invalid_data["years_of_experience"] = -1
        
        response = client.post("/api/v1/provider/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["success"] is False
        assert "details" in data
    
    def test_invalid_clinic_address(self, client, valid_provider_data):
        """Test registration with invalid clinic address."""
        invalid_data = valid_provider_data.copy()
        invalid_data["clinic_address"] = {
            "street": "",  # Empty street
            "city": "City",
            "state": "State",
            "zip": "12345"
        }
        
        response = client.post("/api/v1/provider/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["success"] is False
        assert "errors" in data
    
    def test_email_sending_failure(self, client, valid_provider_data):
        """Test registration when email sending fails."""
        with patch('services.email_service.email_service.send_verification_email', 
                   return_value=AsyncMock(return_value=False)):
            response = client.post("/api/v1/provider/register", json=valid_provider_data)
            
            # Registration should still succeed even if email fails
            assert response.status_code == 201
            data = response.json()
            
            assert data["success"] is True
            assert "registered successfully" in data["message"]
    
    def test_rate_limiting(self, client, valid_provider_data):
        """Test rate limiting on registration endpoint."""
        # Make multiple requests to trigger rate limiting
        responses = []
        
        for i in range(settings.RATE_LIMIT_REQUESTS + 2):
            test_data = valid_provider_data.copy()
            test_data["email"] = f"test{i}@example.com"
            test_data["phone_number"] = f"+123456789{i}"
            test_data["license_number"] = f"MD12345{i}"
            
            with patch('services.email_service.email_service.send_verification_email', 
                       return_value=AsyncMock(return_value=True)):
                response = client.post("/api/v1/provider/register", json=test_data)
                responses.append(response)
        
        # First few requests should succeed
        for i in range(settings.RATE_LIMIT_REQUESTS):
            assert responses[i].status_code == 201
        
        # Additional requests should be rate limited
        for i in range(settings.RATE_LIMIT_REQUESTS, len(responses)):
            assert responses[i].status_code == 429
            data = responses[i].json()
            assert data["success"] is False
            assert "Rate limit exceeded" in data["message"]
    
    def test_get_specializations(self, client):
        """Test get specializations endpoint."""
        response = client.get("/api/v1/provider/specializations")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "specializations" in data["data"]
        assert isinstance(data["data"]["specializations"], list)
        assert len(data["data"]["specializations"]) > 0
    
    def test_get_password_requirements(self, client):
        """Test get password requirements endpoint."""
        response = client.get("/api/v1/provider/password-requirements")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "min_length" in data["data"]
        assert "max_length" in data["data"]
        assert "require_uppercase" in data["data"]
        assert "require_lowercase" in data["data"]
        assert "require_digit" in data["data"]
        assert "require_special" in data["data"]
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/provider/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["status"] == "healthy"
        assert "service" in data["data"]
        assert "version" in data["data"]
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "version" in data
        assert "endpoints" in data
    
    def test_application_health_check(self, client):
        """Test application health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["status"] == "healthy"
