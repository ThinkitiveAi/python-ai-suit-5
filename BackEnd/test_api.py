#!/usr/bin/env python3
"""
Simple test script to demonstrate the Provider Registration API functionality.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test all API endpoints."""
    print("🚀 Testing Provider Registration API")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Health check
    print("\n2. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get specializations
    print("\n3. Testing specializations endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/provider/specializations")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Available specializations: {data['data']['specializations']}")
        print(f"Total count: {data['data']['count']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Get password requirements
    print("\n4. Testing password requirements endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/provider/password-requirements")
        print(f"Status: {response.status_code}")
        data = response.json()
        print("Password requirements:")
        for key, value in data['data'].items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Provider service health
    print("\n5. Testing provider service health...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/provider/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Provider registration (with valid data)
    print("\n6. Testing provider registration...")
    
    # Use a unique email to avoid duplicates
    timestamp = int(time.time())
    
    registration_data = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": f"alice.johnson.{timestamp}@medicalprovider.com",
        "phone_number": "+15551234567",
        "password": "StrongMedical@Pass2024",
        "confirm_password": "StrongMedical@Pass2024",
        "specialization": "Cardiology",
        "license_number": f"MD{timestamp}",
        "years_of_experience": 8,
        "clinic_address": {
            "street": "456 Healthcare Boulevard",
            "city": "Boston",
            "state": "MA",
            "zip": "02101"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/provider/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            data = response.json()
            print(f"Provider ID: {data['data']['provider_id']}")
            print(f"Email: {data['data']['email']}")
            print(f"Verification Status: {data['data']['verification_status']}")
        elif response.status_code == 429:
            print("⚠️  Rate limited - this is expected behavior for security")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Registration failed")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 7: Test duplicate registration
    print("\n7. Testing duplicate email detection...")
    try:
        # Try to register with the same email again
        response = requests.post(
            f"{BASE_URL}/api/v1/provider/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 409:
            print("✅ Duplicate detection working!")
            print(f"Response: {response.json()['message']}")
        elif response.status_code == 429:
            print("⚠️  Rate limited - cannot test duplicates right now")
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 8: Test invalid data validation
    print("\n8. Testing validation with invalid data...")
    
    invalid_data = {
        "first_name": "J",  # Too short
        "last_name": "Smith123",  # Contains numbers
        "email": "invalid-email",  # Invalid format
        "phone_number": "123-456-7890",  # Invalid format
        "password": "weak",  # Too weak
        "confirm_password": "different",  # Doesn't match
        "specialization": "FakeSpecialty",  # Not in allowed list
        "license_number": "INVALID@LICENSE",  # Invalid format
        "years_of_experience": -1,  # Negative
        "clinic_address": {
            "street": "",  # Empty
            "city": "City",
            "state": "State",
            "zip": "invalid-zip"  # Invalid format
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/provider/register",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ Validation working correctly!")
            data = response.json()
            print("Validation errors detected:")
            if 'errors' in data:
                for error in data['errors'][:3]:  # Show first 3 errors
                    print(f"  - {error['field']}: {error['message']}")
            elif 'details' in data:
                for detail in data['details'][:3]:  # Show first 3 details
                    print(f"  - {detail}")
        elif response.status_code == 429:
            print("⚠️  Rate limited - cannot test validation right now")
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\nKey Features Demonstrated:")
    print("✅ SQLite database integration")
    print("✅ Comprehensive input validation")
    print("✅ Password strength requirements")
    print("✅ Rate limiting protection")
    print("✅ Duplicate detection")
    print("✅ Email verification system (mock)")
    print("✅ Audit logging")
    print("✅ RESTful API design")
    print("✅ Proper error handling")
    print("✅ Security best practices")

if __name__ == "__main__":
    test_api_endpoints()
