#!/usr/bin/env python3
"""
Test script for provider registration with proper phone number format.
"""
import requests
import json
import time

def test_registration():
    """Test provider registration with various phone number formats."""
    
    base_url = "http://localhost:8000"
    
    # Test different phone number formats
    phone_formats = [
        "+12345678901",  # E.164 format
        "+1 234 567 8901",  # With spaces
        "+1-234-567-8901",  # With dashes
        "+1 (234) 567-8901",  # US format with parentheses
    ]
    
    print("🧪 Testing phone number formats...")
    
    for i, phone in enumerate(phone_formats):
        print(f"\n{i+1}. Testing phone format: {phone}")
        
        # Create unique data for each test
        timestamp = int(time.time()) + i
        
        registration_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": f"alice.test.{timestamp}@example.com",
            "phone_number": phone,
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
                f"{base_url}/api/v1/provider/register",
                json=registration_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                print("✅ Registration successful!")
                data = response.json()
                print(f"Provider ID: {data['data']['provider_id']}")
                print(f"Email: {data['data']['email']}")
                break  # Success, no need to test more formats
                
            elif response.status_code == 429:
                print("⚠️  Rate limited - waiting...")
                print("This demonstrates the rate limiting security feature is working!")
                break
                
            elif response.status_code == 422:
                print("❌ Validation failed")
                data = response.json()
                if 'errors' in data:
                    for error in data['errors']:
                        print(f"   Error: {error['field']} - {error['message']}")
                        
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"Response: {response.json()}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test password requirements endpoint
    print("\n📋 Testing password requirements...")
    try:
        response = requests.get(f"{base_url}/api/v1/provider/password-requirements")
        if response.status_code == 200:
            data = response.json()
            print("Password requirements:")
            for key, value in data['data'].items():
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test specializations endpoint
    print("\n🏥 Testing specializations...")
    try:
        response = requests.get(f"{base_url}/api/v1/provider/specializations")
        if response.status_code == 200:
            data = response.json()
            print(f"Available specializations ({data['data']['count']}):")
            for spec in data['data']['specializations']:
                print(f"  - {spec}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_registration()
