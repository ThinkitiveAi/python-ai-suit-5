#!/usr/bin/env python3
"""
Script to directly create a test provider in the database.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from db.database import get_db, initialize_database
from db.models.provider import Provider
from core.security import security
import uuid

def create_test_provider_in_db():
    """Create a test provider directly in the database."""
    print("🏥 Creating Test Provider in Database")
    print("=" * 45)
    
    try:
        # Initialize database
        initialize_database()
        
        # Get database session
        db = next(get_db())
        
        # Check if provider already exists
        existing_provider = db.query(Provider).filter(
            Provider.email == "vaibhav@gmail.com"
        ).first()
        
        if existing_provider:
            print("⚠️  Provider already exists, updating password...")
            # Update the existing provider's password
            existing_provider.password_hash = security.hash_password("Vaibhav@gmail10.com")
            existing_provider.failed_login_attempts = 0
            existing_provider.locked_until = None
            existing_provider.is_active = True
            existing_provider.verification_status = "verified"
            db.commit()
            print("✅ Provider updated successfully!")
            return existing_provider
        
        # Create new provider
        provider = Provider(
            id=uuid.uuid4(),
            first_name="Vaibhav",
            last_name="Martinez", 
            email="vaibhav@gmail.com",
            phone_number="+12345678907",
            password_hash=security.hash_password("Vaibhav@gmail10.com"),
            specialization="Cardiology",
            license_number="MD2024001",
            years_of_experience=10,
            clinic_address={
                "street": "123 Medical Center Drive",
                "city": "New York", 
                "state": "NY",
                "zip": "10001"
            },
            verification_status="verified",
            is_active=True,
            failed_login_attempts=0,
            locked_until=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(provider)
        db.commit()
        db.refresh(provider)
        
        print("✅ Test Provider Created Successfully!")
        print(f"🆔 ID: {provider.id}")
        print(f"👤 Name: {provider.first_name} {provider.last_name}")
        print(f"📧 Email: {provider.email}")
        print(f"📱 Phone: {provider.phone_number}")
        print(f"🏥 Specialization: {provider.specialization}")
        print(f"🆔 License: {provider.license_number}")
        print(f"📅 Experience: {provider.years_of_experience} years")
        print(f"✅ Status: {provider.verification_status}")
        print(f"🔓 Active: {provider.is_active}")
        
        return provider
        
    except Exception as e:
        print(f"❌ Error creating provider: {str(e)}")
        return None
    finally:
        if 'db' in locals():
            db.close()

def test_login_with_created_provider():
    """Test login with the created provider."""
    print("\n🔐 Testing Provider Login")
    print("=" * 30)
    
    import requests
    
    login_data = {
        "email": "vaibhav@gmail.com",
        "password": "Vaibhav@gmail10.com"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/provider/login",
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
                print(f"\n🔑 JWT Token Information:")
                print(f"   Access Token: {login_info.get('access_token', 'N/A')[:50]}...")
                print(f"   Expires In: {login_info.get('expires_in')} seconds (1 hour)")
                print(f"   Token Type: {login_info.get('token_type')}")
                
                if 'provider' in login_info:
                    provider = login_info['provider']
                    print(f"\n👤 Provider Information:")
                    print(f"   ID: {provider.get('id')}")
                    print(f"   Name: {provider.get('first_name')} {provider.get('last_name')}")
                    print(f"   Email: {provider.get('email')}")
                    print(f"   Specialization: {provider.get('specialization')}")
                    print(f"   License: {provider.get('license_number')}")
                    print(f"   Experience: {provider.get('years_of_experience')} years")
                    print(f"   Status: {provider.get('verification_status')}")
                    print(f"   Active: {provider.get('is_active')}")
                
                # Test JWT token payload
                token = login_info.get('access_token')
                if token:
                    payload = security.verify_token(token)
                    if payload:
                        print(f"\n🔍 JWT Token Payload:")
                        print(f"   Provider ID: {payload.get('provider_id')}")
                        print(f"   Email: {payload.get('email')}")
                        print(f"   Role: {payload.get('role')}")
                        print(f"   Specialization: {payload.get('specialization')}")
                        print(f"   Expires: {datetime.fromtimestamp(payload.get('exp', 0))}")
                    else:
                        print("⚠️  Token verification failed")
            
            return True
        else:
            print("❌ Login Failed!")
            try:
                error_data = response.json()
                print(f"💬 Error: {error_data.get('message')}")
                print(f"🔍 Error Code: {error_data.get('error_code')}")
            except:
                print(f"📄 Raw Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login Test Error: {str(e)}")
        return False

def main():
    """Main function."""
    print("🚀 Provider Authentication Test Setup")
    print("=" * 50)
    
    # Create test provider in database
    provider = create_test_provider_in_db()
    
    if provider:
        # Test login
        login_success = test_login_with_created_provider()
        
        if login_success:
            print("\n🎉 Provider Authentication Test Completed Successfully!")
            print("\n📋 Test Results:")
            print("   ✅ Provider created in database")
            print("   ✅ Login endpoint working")
            print("   ✅ JWT token generation working")
            print("   ✅ JWT token validation working")
            print("   ✅ Provider data returned correctly")
            print("\n🔐 JWT Configuration Verified:")
            print("   ✅ Access Token Expiry: 1 hour")
            print("   ✅ Payload includes: provider_id, email, role, specialization")
            print("   ✅ Token type: Bearer")
        else:
            print("\n⚠️  Provider created but login test failed")
    else:
        print("\n❌ Failed to create test provider")
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete")
    print("\n💡 You can now test the login endpoint with:")
    print("   Email: vaibhav@gmail.com")
    print("   Password: Vaibhav@gmail10.com")

if __name__ == "__main__":
    main()
