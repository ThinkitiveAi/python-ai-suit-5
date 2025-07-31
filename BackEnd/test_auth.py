#!/usr/bin/env python3
"""
Test script for authentication endpoints.
Tests login, token refresh, logout, and protected endpoints.
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "auth.test@example.com"
TEST_PHONE = "+1-234-567-8901"
TEST_PASSWORD = "SecurePass987!@#"

def print_separator(title):
    """Print a separator with title."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def print_response(response, title="Response"):
    """Print formatted response."""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Text: {response.text}")

def register_test_provider():
    """Register a test provider for authentication testing."""
    print_separator("REGISTERING TEST PROVIDER")
    
    registration_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "confirm_password": TEST_PASSWORD,
        "first_name": "Auth",
        "last_name": "Test",
        "phone_number": TEST_PHONE,
        "specialization": "Internal Medicine",
        "license_number": "AUTH123456",
        "years_of_experience": 5,
        "clinic_address": {
            "street": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "zip": "12345",
            "country": "USA"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/providers/register",
        json=registration_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response, "Registration")
    return response.status_code == 201

def test_login():
    """Test provider login."""
    print_separator("TESTING LOGIN")
    
    # Test successful login
    login_data = {
        "identifier": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "remember_me": False
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response, "Login")
    
    if response.status_code == 200:
        data = response.json()
        access_token = data["data"]["access_token"]
        refresh_token = data["data"]["refresh_token"]
        print(f"\n✅ Login successful!")
        print(f"Access Token: {access_token[:50]}...")
        print(f"Refresh Token: {refresh_token[:50]}...")
        return access_token, refresh_token
    else:
        print("❌ Login failed!")
        return None, None

def test_login_with_phone():
    """Test provider login with phone number."""
    print_separator("TESTING LOGIN WITH PHONE")
    
    login_data = {
        "identifier": TEST_PHONE,
        "password": TEST_PASSWORD,
        "remember_me": True
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response, "Login with Phone")
    
    if response.status_code == 200:
        print("✅ Phone login successful!")
        return True
    else:
        print("❌ Phone login failed!")
        return False

def test_invalid_login():
    """Test login with invalid credentials."""
    print_separator("TESTING INVALID LOGIN")
    
    # Test with wrong password
    login_data = {
        "identifier": TEST_EMAIL,
        "password": "WrongPassword123!",
        "remember_me": False
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response, "Invalid Login")
    
    if response.status_code == 401:
        print("✅ Invalid login correctly rejected!")
        return True
    else:
        print("❌ Invalid login should have been rejected!")
        return False

def test_protected_endpoint(access_token):
    """Test accessing protected endpoint."""
    print_separator("TESTING PROTECTED ENDPOINT")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response(response, "Get Current Provider")
    
    if response.status_code == 200:
        print("✅ Protected endpoint access successful!")
        return True
    else:
        print("❌ Protected endpoint access failed!")
        return False

def test_token_verification(access_token):
    """Test token verification endpoint."""
    print_separator("TESTING TOKEN VERIFICATION")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/auth/token/verify", headers=headers)
    print_response(response, "Token Verification")
    
    if response.status_code == 200:
        print("✅ Token verification successful!")
        return True
    else:
        print("❌ Token verification failed!")
        return False

def test_token_refresh(refresh_token):
    """Test token refresh."""
    print_separator("TESTING TOKEN REFRESH")
    
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json=refresh_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(response, "Token Refresh")
    
    if response.status_code == 200:
        data = response.json()
        new_access_token = data["data"]["access_token"]
        print(f"✅ Token refresh successful!")
        print(f"New Access Token: {new_access_token[:50]}...")
        return new_access_token
    else:
        print("❌ Token refresh failed!")
        return None

def test_logout(access_token, refresh_token):
    """Test logout."""
    print_separator("TESTING LOGOUT")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    logout_data = {
        "refresh_token": refresh_token
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/logout",
        json=logout_data,
        headers=headers
    )
    
    print_response(response, "Logout")
    
    if response.status_code == 200:
        print("✅ Logout successful!")
        return True
    else:
        print("❌ Logout failed!")
        return False

def test_logout_all(access_token):
    """Test logout all sessions."""
    print_separator("TESTING LOGOUT ALL")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/auth/logout-all", headers=headers)
    print_response(response, "Logout All")
    
    if response.status_code == 200:
        print("✅ Logout all successful!")
        return True
    else:
        print("❌ Logout all failed!")
        return False

def test_rate_limiting():
    """Test rate limiting on login endpoint."""
    print_separator("TESTING RATE LIMITING")
    
    login_data = {
        "identifier": "nonexistent@example.com",
        "password": "WrongPassword123!",
        "remember_me": False
    }
    
    print("Making multiple rapid login attempts...")
    
    for i in range(12):  # Try to exceed rate limit
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Attempt {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print("✅ Rate limiting is working!")
            return True
        
        time.sleep(0.1)  # Small delay between requests
    
    print("⚠️ Rate limiting may not be working as expected")
    return False

def main():
    """Run all authentication tests."""
    print_separator("FASTAPI AUTHENTICATION TESTING")
    print(f"Testing against: {BASE_URL}")
    print(f"Test Provider: {TEST_EMAIL}")
    print(f"Timestamp: {datetime.now()}")
    
    # Register test provider
    if not register_test_provider():
        print("❌ Failed to register test provider. Continuing with existing provider...")
    
    # Test login
    access_token, refresh_token = test_login()
    if not access_token:
        print("❌ Cannot continue without valid tokens")
        return
    
    # Test login with phone
    test_login_with_phone()
    
    # Test invalid login
    test_invalid_login()
    
    # Test protected endpoints
    test_protected_endpoint(access_token)
    test_token_verification(access_token)
    
    # Test token refresh
    new_access_token = test_token_refresh(refresh_token)
    if new_access_token:
        access_token = new_access_token
    
    # Test logout
    test_logout(access_token, refresh_token)
    
    # Login again for logout all test
    access_token, refresh_token = test_login()
    if access_token:
        test_logout_all(access_token)
    
    # Test rate limiting
    test_rate_limiting()
    
    print_separator("TESTING COMPLETE")
    print("✅ Authentication testing finished!")
    print("\nNote: Some tests may fail if the provider already exists or")
    print("if rate limits are active. This is expected behavior.")

if __name__ == "__main__":
    main()
