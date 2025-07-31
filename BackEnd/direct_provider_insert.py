#!/usr/bin/env python3
"""
Direct database insertion for test provider.
"""
import sys
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import bcrypt

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
from db.database import SessionLocal, initialize_database
from db.models.provider import ProviderSQL

def create_test_provider():
    """Create a test provider directly in the database."""
    print("🚀 Direct Provider Database Insert")
    print("=" * 40)
    
    try:
        # Initialize database
        initialize_database()
        
        # Create database session
        db = SessionLocal()
        
        # Test provider data
        email = "vaibhav@gmail.com"
        password = "Vaibhav@gmail10.com"
        
        print(f"👤 Creating provider: {email}")
        
        # Check if provider already exists
        existing_provider = db.query(ProviderSQL).filter(ProviderSQL.email == email).first()
        if existing_provider:
            print("✅ Provider already exists, updating password...")
            # Update password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            existing_provider.password_hash = password_hash
            existing_provider.failed_login_attempts = 0
            existing_provider.locked_until = None
            db.commit()
            provider_id = existing_provider.id
        else:
            print("🆕 Creating new provider...")
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create provider
            provider = ProviderSQL(
                first_name="Vaibhav",
                last_name="Kumar",
                email=email,
                phone_number="+1-555-123-4567",
                password_hash=password_hash,
                specialization="Internal Medicine",
                license_number="LIC123456",
                years_of_experience=5,
                clinic_address={
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip": "12345",
                    "country": "USA"
                },
                verification_status="verified",
                is_active=True,
                failed_login_attempts=0,
                locked_until=None,
                login_count=0
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            provider_id = provider.id
            
        print(f"✅ Provider created/updated with ID: {provider_id}")
        
        # Verify the provider
        test_provider = db.query(ProviderSQL).filter(ProviderSQL.email == email).first()
        if test_provider:
            print(f"✅ Verification successful:")
            print(f"   📧 Email: {test_provider.email}")
            print(f"   👤 Name: {test_provider.first_name} {test_provider.last_name}")
            print(f"   🏥 Specialization: {test_provider.specialization}")
            print(f"   🔐 Password hash exists: {bool(test_provider.password_hash)}")
            print(f"   ✅ Active: {test_provider.is_active}")
            print(f"   🔓 Failed attempts: {test_provider.failed_login_attempts}")
            
            # Test password verification
            password_valid = bcrypt.checkpw(password.encode('utf-8'), test_provider.password_hash.encode('utf-8'))
            print(f"   🔑 Password verification: {'✅ Valid' if password_valid else '❌ Invalid'}")
            
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_login():
    """Test the login endpoint with the created provider."""
    print(f"\n🧪 Testing Login Endpoint")
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
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LOGIN SUCCESSFUL!")
            print(f"🎫 Token Type: {data.get('token_type', 'N/A')}")
            print(f"🔑 Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"⏰ Expires In: {data.get('expires_in', 'N/A')} seconds")
            
            if 'provider' in data:
                provider = data['provider']
                print(f"👤 Provider: {provider.get('first_name')} {provider.get('last_name')}")
                print(f"📧 Email: {provider.get('email')}")
                print(f"🏥 Specialization: {provider.get('specialization')}")
            
            return True
        else:
            data = response.json()
            print(f"❌ LOGIN FAILED")
            print(f"💬 Message: {data.get('message', 'N/A')}")
            print(f"🔍 Error Code: {data.get('error_code', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {str(e)}")
        return False

def main():
    """Main function."""
    print("🚀 Provider Login Backend Test")
    print("=" * 50)
    
    # Create test provider
    provider_created = create_test_provider()
    
    if provider_created:
        # Test login
        login_success = test_login()
        
        if login_success:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print("=" * 25)
            print("✅ Provider created in database")
            print("✅ Login endpoint working")
            print("✅ JWT token generation working")
            print("✅ Password verification working")
            print("✅ Authentication flow complete")
            
            print(f"\n🔗 Ready for Integration:")
            print("   • Endpoint: POST /api/v1/provider/login")
            print("   • Test Credentials:")
            print("     - Email: vaibhav@gmail.com")
            print("     - Password: Vaibhav@gmail10.com")
            print("   • Returns: JWT token + provider data")
            
        else:
            print(f"\n⚠️ Provider created but login failed")
    else:
        print(f"\n❌ Provider creation failed")
    
    print(f"\n🏁 Test Complete")

if __name__ == "__main__":
    main()
