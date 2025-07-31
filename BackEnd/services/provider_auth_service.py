"""
Provider authentication service for JWT-based login.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from db.models.provider import Provider
from schemas.provider_auth import ProviderLoginRequest, ProviderLoginData, ProviderData
from core.security import security
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class ProviderAuthService:
    """Service for handling provider authentication operations."""
    
    def authenticate_provider(
        self,
        db: Session,
        login_request: ProviderLoginRequest
    ) -> Tuple[bool, Optional[ProviderLoginData], Optional[str]]:
        """
        Authenticate provider with email and password.
        
        Args:
            db: Database session
            login_request: Login request data
            
        Returns:
            Tuple of (success, login_data, error_message)
        """
        try:
            # Find provider by email
            provider = db.query(Provider).filter(
                Provider.email == login_request.email.lower()
            ).first()
            
            if not provider:
                logger.warning(f"Login attempt with unknown email: {login_request.email}")
                return False, None, "Invalid credentials"
            
            # Check if account is active
            if not provider.is_active:
                logger.warning(f"Login attempt with inactive account: {login_request.email}")
                return False, None, "Account is inactive"
            
            # Verify password
            if not security.verify_password(login_request.password, provider.password_hash):
                logger.warning(f"Invalid password for email: {login_request.email}")
                # Update failed login attempts
                provider.failed_login_attempts += 1
                
                # Lock account if too many failed attempts
                if provider.failed_login_attempts >= 5:
                    provider.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
                    logger.warning(f"Account locked due to failed attempts: {login_request.email}")
                
                db.commit()
                return False, None, "Invalid credentials"
            
            # Check if account is locked
            if provider.locked_until and provider.locked_until > datetime.now(timezone.utc):
                logger.warning(f"Login attempt with locked account: {login_request.email}")
                return False, None, "Account is temporarily locked"
            
            # Reset failed login attempts on successful authentication
            provider.failed_login_attempts = 0
            provider.locked_until = None
            provider.last_login = datetime.now(timezone.utc)
            provider.login_count += 1
            
            db.commit()
            
            # Generate JWT token
            token_data = {
                "provider_id": str(provider.id),
                "email": provider.email,
                "role": "provider",
                "specialization": provider.specialization
            }
            
            # Create access token with 1 hour expiry
            access_token = security.create_access_token(
                data=token_data,
                expires_delta=timedelta(hours=1)
            )
            
            # Prepare provider data
            provider_data = ProviderData(
                id=str(provider.id),
                first_name=provider.first_name,
                last_name=provider.last_name,
                email=provider.email,
                phone_number=provider.phone_number,
                specialization=provider.specialization,
                license_number=provider.license_number,
                years_of_experience=provider.years_of_experience,
                verification_status=provider.verification_status,
                is_active=provider.is_active,
                created_at=provider.created_at,
                last_login=provider.last_login
            )
            
            # Prepare login response data
            login_data = ProviderLoginData(
                access_token=access_token,
                expires_in=3600,  # 1 hour in seconds
                token_type="Bearer",
                provider=provider_data
            )
            
            logger.info(f"Successful login for provider: {login_request.email}")
            return True, login_data, None
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False, None, "Authentication failed"


# Global provider auth service instance
provider_auth_service = ProviderAuthService()
