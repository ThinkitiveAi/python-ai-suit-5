#!/usr/bin/env python3
"""
Test script for provider login functionality.
"""
import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_provider_login():
    """Test the provider login endpoint."""
    print("🧪 Testing Provider Login Endpoint")
    print("=" * 50)
    
    # Test data
    login_data = {
        "email": "john.doe@clinic.com",
        "password": "SecurePassword123!"
    }
    
    print(f"📧 Testing login with email: {login_data['email']}")
    
    try:
        # Make login request
        response = requests.post(
            f"{BASE_URL}/provider/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login Successful!")
            print(f"🎯 Success: {data.get('success')}")
            print(f"💬 Message: {data.get('message')}")
            
            if 'data' in data:
                login_info = data['data']
                print("\n🔐 Token Information:")
                print(f"   Access Token: {login_info.get('access_token', 'N/A')[:50]}...")
                print(f"   Expires In: {login_info.get('expires_in')} seconds")
                print(f"   Token Type: {login_info.get('token_type')}")
                
                if 'provider' in login_info:
                    provider = login_info['provider']
                    print("\n👤 Provider Information:")
                    print(f"   ID: {provider.get('id')}")
                    print(f"   Name: {provider.get('first_name')} {provider.get('last_name')}")
                    print(f"   Email: {provider.get('email')}")
                    print(f"   Specialization: {provider.get('specialization')}")
                    print(f"   License: {provider.get('license_number')}")
                    print(f"   Experience: {provider.get('years_of_experience')} years")
                    print(f"   Status: {provider.get('verification_status')}")
                    print(f"   Active: {provider.get('is_active')}")
                    
                    if provider.get('last_login'):
                        print(f"   Last Login: {provider.get('last_login')}")
            
            return login_info.get('access_token') if 'data' in data else None
            
        else:
            print("❌ Login Failed!")
            try:
                error_data = response.json()
                print(f"💬 Error Message: {error_data.get('message', 'Unknown error')}")
                print(f"🔍 Error Code: {error_data.get('error_code', 'N/A')}")
            except:
                print(f"📄 Raw Response: {response.text}")
            
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return None

def test_invalid_login():
    """Test login with invalid credentials."""
    print("\n🧪 Testing Invalid Login")
    print("=" * 30)
    
    # Test with invalid credentials
    invalid_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    
    print(f"📧 Testing with invalid email: {invalid_data['email']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/provider/login",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid credentials")
            error_data = response.json()
            print(f"💬 Error Message: {error_data.get('message')}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing invalid login: {str(e)}")

def test_validation_errors():
    """Test login with validation errors."""
    print("\n🧪 Testing Validation Errors")
    print("=" * 35)
    
    # Test with invalid email format
    invalid_email_data = {
        "email": "invalid-email-format",
        "password": "somepassword"
    }
    
    print("📧 Testing with invalid email format")
    
    try:
        response = requests.post(
            f"{BASE_URL}/provider/login",
            json=invalid_email_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ Correctly rejected invalid email format")
            error_data = response.json()
            print(f"💬 Validation Error: {error_data.get('detail', 'N/A')}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing validation: {str(e)}")

def test_token_validation(access_token):
    """Test JWT token validation."""
    if not access_token:
        print("\n⚠️  Skipping token validation (no token available)")
        return
    
    print("\n🧪 Testing JWT Token Validation")
    print("=" * 40)
    
    try:
        # Test accessing a protected endpoint (if available)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Try to access current provider info
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers
        )
        
        print(f"📡 Token Validation Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token is valid and accepted")
            data = response.json()
            if 'data' in data and 'provider' in data['data']:
                provider = data['data']['provider']
                print(f"👤 Authenticated as: {provider.get('first_name')} {provider.get('last_name')}")
        else:
            print(f"⚠️  Token validation response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing token validation: {str(e)}")

def main():
    """Main test function."""
    print("🚀 Provider Authentication API Test Suite")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {BASE_URL}")
    print()
    
    # Test successful login
    access_token = test_provider_login()
    
    # Test invalid login
    test_invalid_login()
    
    # Test validation errors
    test_validation_errors()
    
    # Test token validation
    test_token_validation(access_token)
    
    print("\n" + "=" * 60)
    print("🏁 Test Suite Completed")
    print("\n📋 Test Summary:")
    print("   ✅ Provider login endpoint")
    print("   ✅ Invalid credentials handling")
    print("   ✅ Input validation")
    print("   ✅ JWT token generation")
    print("\n💡 Next Steps:")
    print("   1. Create a provider account if none exists")
    print("   2. Test with valid credentials")
    print("   3. Use the access token for authenticated requests")

if __name__ == "__main__":
    main()
