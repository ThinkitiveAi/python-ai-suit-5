"""
Authentication service for provider login, logout, and session management.
"""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from db.models.provider import Provider
from db.models.refresh_token import RefreshToken
from schemas.auth import LoginRequest, LoginData
from schemas.token import TokenPair
from utils.jwt_utils import jwt_manager
from utils.password_utils import verify_password
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self):
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30

    def authenticate_provider(
        self,
        db: Session,
        login_request: LoginRequest
    ) -> Tuple[bool, Optional[LoginData], Optional[str], Optional[Dict[str, Any]]]:
        """
        Authenticate provider with email/phone and password.
        
        Args:
            db: Database session
            login_request: Login request data
            
        Returns:
            Tuple of (success, login_data, error_message, lock_info)
        """
        try:
            # Find provider by email or phone
            provider = self._find_provider_by_identifier(db, login_request.identifier)
            
            if not provider:
                logger.warning(f"Login attempt with unknown identifier: {login_request.identifier}")
                return False, None, "Invalid credentials", None
            
            # Check if account is locked
            if self._is_account_locked(provider):
                lock_info = self._get_lock_info(provider)
                logger.warning(f"Login attempt on locked account: {provider.email}")
                return False, None, "Account locked", lock_info
            
            # Check if account is active
            if not provider.is_active:
                logger.warning(f"Login attempt on inactive account: {provider.email}")
                return False, None, "Account is inactive", None
            
            # Verify password
            if not verify_password(login_request.password, provider.password_hash):
                self._handle_failed_login(db, provider)
                logger.warning(f"Failed login attempt for: {provider.email}")
                
                # Check if account should be locked after this attempt
                if provider.failed_login_attempts >= self.max_failed_attempts:
                    lock_info = self._get_lock_info(provider)
                    return False, None, "Account locked due to too many failed attempts", lock_info
                
                return False, None, "Invalid credentials", None
            
            # Successful login
            self._handle_successful_login(db, provider)
            
            # Generate tokens
            access_token, expires_in = jwt_manager.create_access_token(
                provider_id=str(provider.id),
                email=provider.email,
                specialization=provider.specialization,
                verification_status=provider.verification_status,
                is_active=provider.is_active,
                remember_me=login_request.remember_me
            )
            
            refresh_token, jti, refresh_expires_at = jwt_manager.create_refresh_token(
                provider_id=str(provider.id),
                email=provider.email,
                specialization=provider.specialization,
                verification_status=provider.verification_status,
                is_active=provider.is_active,
                remember_me=login_request.remember_me
            )
            
            # Store refresh token in database
            refresh_token_hash = self._hash_token(refresh_token)
            db_refresh_token = RefreshToken(
                provider_id=provider.id,
                token_hash=refresh_token_hash,
                expires_at=refresh_expires_at
            )
            db.add(db_refresh_token)
            db.commit()
            
            # Create response data
            from schemas.provider import ProviderResponse
            provider_response = ProviderResponse(
                id=str(provider.id),
                email=provider.email,
                first_name=provider.first_name,
                last_name=provider.last_name,
                phone_number=provider.phone_number,
                specialization=provider.specialization,
                license_number=provider.license_number,
                years_of_experience=provider.years_of_experience,
                verification_status=provider.verification_status,
                is_active=provider.is_active,
                created_at=provider.created_at,
                updated_at=provider.updated_at
            )
            
            login_data = LoginData(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                provider=provider_response
            )
            
            logger.info(f"Successful login for provider: {provider.email}")
            return True, login_data, None, None
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            db.rollback()
            return False, None, "Authentication failed", None

    def refresh_access_token(
        self,
        db: Session,
        refresh_token: str
    ) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
        """
        Refresh access token using refresh token.
        
        Args:
            db: Database session
            refresh_token: Refresh token string
            
        Returns:
            Tuple of (success, new_access_token, expires_in, error_message)
        """
        try:
            # Verify refresh token
            payload = jwt_manager.verify_refresh_token(refresh_token)
            if not payload:
                return False, None, None, "Invalid refresh token"
            
            # Find refresh token in database
            refresh_token_hash = self._hash_token(refresh_token)
            db_refresh_token = db.query(RefreshToken).filter(
                RefreshToken.token_hash == refresh_token_hash,
                RefreshToken.is_revoked == False
            ).first()
            
            if not db_refresh_token or not db_refresh_token.is_valid:
                return False, None, None, "Invalid or expired refresh token"
            
            # Find provider
            provider = db.query(Provider).filter(Provider.id == db_refresh_token.provider_id).first()
            if not provider or not provider.is_active:
                return False, None, None, "Provider not found or inactive"
            
            # Mark refresh token as used
            db_refresh_token.mark_used()
            
            # Generate new access token
            access_token, expires_in = jwt_manager.create_access_token(
                provider_id=str(provider.id),
                email=provider.email,
                specialization=provider.specialization,
                verification_status=provider.verification_status,
                is_active=provider.is_active,
                remember_me=False  # Don't extend on refresh
            )
            
            db.commit()
            
            logger.info(f"Token refreshed for provider: {provider.email}")
            return True, access_token, expires_in, None
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            db.rollback()
            return False, None, None, "Token refresh failed"

    def logout_provider(
        self,
        db: Session,
        refresh_token: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Logout provider by revoking refresh token.
        
        Args:
            db: Database session
            refresh_token: Refresh token to revoke
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Find and revoke refresh token
            refresh_token_hash = self._hash_token(refresh_token)
            db_refresh_token = db.query(RefreshToken).filter(
                RefreshToken.token_hash == refresh_token_hash,
                RefreshToken.is_revoked == False
            ).first()
            
            if db_refresh_token:
                db_refresh_token.revoke()
                db.commit()
                logger.info(f"Provider logged out: {db_refresh_token.provider_id}")
            
            return True, None
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            db.rollback()
            return False, "Logout failed"

    def logout_all_sessions(
        self,
        db: Session,
        provider_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Logout provider from all sessions by revoking all refresh tokens.
        
        Args:
            db: Database session
            provider_id: Provider UUID
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Revoke all active refresh tokens for provider
            db.query(RefreshToken).filter(
                RefreshToken.provider_id == provider_id,
                RefreshToken.is_revoked == False
            ).update({"is_revoked": True})
            
            db.commit()
            
            logger.info(f"All sessions logged out for provider: {provider_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Logout all error: {str(e)}")
            db.rollback()
            return False, "Logout all failed"

    def _find_provider_by_identifier(self, db: Session, identifier: str) -> Optional[Provider]:
        """Find provider by email or phone number."""
        return db.query(Provider).filter(
            or_(
                Provider.email == identifier.lower(),
                Provider.phone_number == identifier
            )
        ).first()

    def _is_account_locked(self, provider: Provider) -> bool:
        """Check if account is currently locked."""
        if not provider.locked_until:
            return False
        
        return datetime.now(timezone.utc) < provider.locked_until

    def _get_lock_info(self, provider: Provider) -> Dict[str, Any]:
        """Get account lock information."""
        if not provider.locked_until:
            return {}
        
        now = datetime.now(timezone.utc)
        time_remaining = max(0, int((provider.locked_until - now).total_seconds()))
        
        return {
            "locked_until": provider.locked_until.isoformat(),
            "time_remaining_seconds": time_remaining,
            "failed_attempts": provider.failed_login_attempts
        }

    def _handle_failed_login(self, db: Session, provider: Provider):
        """Handle failed login attempt."""
        provider.failed_login_attempts += 1
        
        # Lock account if max attempts reached
        if provider.failed_login_attempts >= self.max_failed_attempts:
            provider.locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=self.lockout_duration_minutes
            )
            logger.warning(f"Account locked for provider: {provider.email}")
        
        db.commit()

    def _handle_successful_login(self, db: Session, provider: Provider):
        """Handle successful login."""
        provider.last_login = datetime.now(timezone.utc)
        provider.login_count += 1
        provider.failed_login_attempts = 0
        provider.locked_until = None
        
        db.commit()

    def _hash_token(self, token: str) -> str:
        """Hash token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()


# Global auth service instance
auth_service = AuthService()
