#!/usr/bin/env python3
"""
Script to create a test provider for login testing.
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def create_test_provider():
    """Create a test provider account."""
    print("🏥 Creating Test Provider Account")
    print("=" * 40)
    
    # Test provider data
    provider_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@clinic.com",
        "phone_number": "+1234567890",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "specialization": "cardiology",
        "license_number": "LIC123456789",
        "years_of_experience": 5,
        "clinic_address": {
            "street": "123 Medical Center Dr",
            "city": "Healthcare City",
            "state": "CA",
            "zip_code": "90210",
            "country": "USA"
        }
    }
    
    print(f"👤 Creating provider: {provider_data['first_name']} {provider_data['last_name']}")
    print(f"📧 Email: {provider_data['email']}")
    print(f"🏥 Specialization: {provider_data['specialization']}")
    
    try:
        # Make registration request
        response = requests.post(
            f"{BASE_URL}/providers/register",
            json=provider_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Provider Created Successfully!")
            print(f"🎯 Success: {data.get('success')}")
            print(f"💬 Message: {data.get('message')}")
            
            if 'data' in data:
                provider_info = data['data']
                print(f"🆔 Provider ID: {provider_info.get('id')}")
                print(f"📧 Email: {provider_info.get('email')}")
                print(f"🔍 Verification Status: {provider_info.get('verification_status')}")
            
            return True
            
        elif response.status_code == 409:
            print("⚠️  Provider already exists (this is expected)")
            error_data = response.json()
            print(f"💬 Message: {error_data.get('message')}")
            return True  # This is fine for testing
            
        else:
            print("❌ Provider Creation Failed!")
            try:
                error_data = response.json()
                print(f"💬 Error Message: {error_data.get('message', 'Unknown error')}")
                if 'details' in error_data:
                    print(f"🔍 Details: {error_data['details']}")
            except:
                print(f"📄 Raw Response: {response.text}")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False

def test_login_after_creation():
    """Test login with the created provider."""
    print("\n🔐 Testing Login with Created Provider")
    print("=" * 45)
    
    login_data = {
        "email": "john.doe@clinic.com",
        "password": "SecurePassword123!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/provider/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login Successful!")
            print(f"🎯 Success: {data.get('success')}")
            print(f"💬 Message: {data.get('message')}")
            
            if 'data' in data:
                login_info = data['data']
                print(f"🔑 Access Token: {login_info.get('access_token', 'N/A')[:50]}...")
                print(f"⏱️  Expires In: {login_info.get('expires_in')} seconds")
                print(f"🏷️  Token Type: {login_info.get('token_type')}")
                
                if 'provider' in login_info:
                    provider = login_info['provider']
                    print(f"👤 Provider: {provider.get('first_name')} {provider.get('last_name')}")
                    print(f"🏥 Specialization: {provider.get('specialization')}")
            
            return True
        else:
            print("❌ Login Failed!")
            try:
                error_data = response.json()
                print(f"💬 Error: {error_data.get('message')}")
            except:
                print(f"📄 Raw Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login Test Error: {str(e)}")
        return False

def main():
    """Main function."""
    print("🚀 Test Provider Setup & Login Test")
    print("=" * 50)
    
    # Create test provider
    provider_created = create_test_provider()
    
    if provider_created:
        # Test login
        login_success = test_login_after_creation()
        
        if login_success:
            print("\n🎉 All Tests Passed!")
            print("✅ Provider account is ready")
            print("✅ Login endpoint is working")
            print("✅ JWT token generation is working")
        else:
            print("\n⚠️  Provider created but login failed")
    else:
        print("\n❌ Failed to create test provider")
    
    print("\n" + "=" * 50)
    print("🏁 Setup Complete")

if __name__ == "__main__":
    main()
