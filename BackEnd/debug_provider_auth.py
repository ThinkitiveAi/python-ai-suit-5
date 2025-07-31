#!/usr/bin/env python3
"""
Debug script for provider authentication.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from db.database import get_db
from db.models.provider import Provider
from services.provider_auth_service import provider_auth_service
from schemas.provider_auth import ProviderLoginRequest
from core.security import security

def debug_provider_lookup():
    """Debug provider lookup in database."""
    print("🔍 Debugging Provider Lookup")
    print("=" * 40)
    
    try:
        # Get database session
        db = next(get_db())
        
        # Look for provider
        email = "vaibhav@gmail.com"
        provider = db.query(Provider).filter(Provider.email == email).first()
        
        if provider:
            print("✅ Provider Found!")
            print(f"   ID: {provider.id}")
            print(f"   Name: {provider.first_name} {provider.last_name}")
            print(f"   Email: {provider.email}")
            print(f"   Phone: {provider.phone_number}")
            print(f"   Specialization: {provider.specialization}")
            print(f"   License: {provider.license_number}")
            print(f"   Active: {provider.is_active}")
            print(f"   Verification: {provider.verification_status}")
            print(f"   Failed Attempts: {provider.failed_login_attempts}")
            print(f"   Locked Until: {provider.locked_until}")
            print(f"   Password Hash: {provider.password_hash[:50]}...")
            
            # Test password verification
            test_password = "Vaibhav@gmail10.com"
            is_valid = security.verify_password(test_password, provider.password_hash)
            print(f"   Password Valid: {is_valid}")
            
            return provider
        else:
            print("❌ Provider Not Found!")
            
            # Check all providers
            all_providers = db.query(Provider).all()
            print(f"📊 Total Providers in DB: {len(all_providers)}")
            
            for p in all_providers:
                print(f"   - {p.email} ({p.first_name} {p.last_name})")
            
            return None
            
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")
        return None
    finally:
        if 'db' in locals():
            db.close()

def debug_auth_service():
    """Debug the authentication service."""
    print("\n🔐 Testing Authentication Service")
    print("=" * 45)
    
    try:
        # Create login request
        login_request = ProviderLoginRequest(
            email="vaibhav@gmail.com",
            password="Vaibhav@gmail10.com"
        )
        
        # Get database session
        db = next(get_db())
        
        # Test authentication
        success, login_data, error_message = provider_auth_service.authenticate_provider(
            db, login_request
        )
        
        print(f"🎯 Authentication Result: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            print("✅ Authentication Successful!")
            print(f"   Access Token: {login_data.access_token[:50]}...")
            print(f"   Token Type: {login_data.token_type}")
            print(f"   Expires In: {login_data.expires_in} seconds")
            print(f"   Provider ID: {login_data.provider.id}")
            print(f"   Provider Name: {login_data.provider.first_name} {login_data.provider.last_name}")
        else:
            print(f"❌ Authentication Failed: {error_message}")
        
        return success
        
    except Exception as e:
        print(f"❌ Auth Service Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

def main():
    """Main function."""
    print("🚀 Provider Authentication Debug")
    print("=" * 50)
    
    # Debug provider lookup
    provider = debug_provider_lookup()
    
    if provider:
        # Debug authentication service
        auth_success = debug_auth_service()
        
        if auth_success:
            print("\n🎉 DEBUG SUCCESSFUL!")
            print("✅ Provider exists in database")
            print("✅ Password verification working")
            print("✅ Authentication service working")
            print("✅ JWT token generation working")
        else:
            print("\n⚠️  Provider found but authentication failed")
    else:
        print("\n❌ Provider not found in database")
    
    print("\n" + "=" * 50)
    print("🏁 Debug Complete")

if __name__ == "__main__":
    main()
