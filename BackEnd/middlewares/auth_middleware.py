"""
Authentication middleware for JWT token validation and provider authentication.
"""
from typing import Optional, Tuple
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.database import get_db
from db.models.provider import Provider
from schemas.token import AccessTokenPayload
from utils.jwt_utils import jwt_manager
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Authentication middleware for JWT token validation."""
    
    def __init__(self):
        self.jwt_manager = jwt_manager

    async def get_current_provider(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
    ) -> Provider:
        """
        Get current authenticated provider from JWT token.
        
        Args:
            request: FastAPI request object
            credentials: HTTP Bearer credentials
            db: Database session
            
        Returns:
            Provider object if authenticated
            
        Raises:
            HTTPException: If authentication fails
        """
        # Check for credentials
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verify access token
        payload = self.jwt_manager.verify_access_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Find provider in database
        provider = db.query(Provider).filter(Provider.id == payload.sub).first()
        if not provider:
            logger.warning(f"Token valid but provider not found: {payload.sub}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Provider not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check if provider is active
        if not provider.is_active:
            logger.warning(f"Inactive provider attempted access: {provider.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Check if account is locked
        if self._is_account_locked(provider):
            logger.warning(f"Locked provider attempted access: {provider.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked"
            )
        
        return provider

    async def get_optional_current_provider(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
    ) -> Optional[Provider]:
        """
        Get current provider if authenticated, None otherwise.
        
        Args:
            request: FastAPI request object
            credentials: HTTP Bearer credentials
            db: Database session
            
        Returns:
            Provider object if authenticated, None otherwise
        """
        try:
            return await self.get_current_provider(request, credentials, db)
        except HTTPException:
            return None

    def verify_provider_permissions(
        self,
        current_provider: Provider,
        required_verification: bool = False,
        required_specializations: Optional[list] = None
    ) -> bool:
        """
        Verify provider has required permissions.
        
        Args:
            current_provider: Current authenticated provider
            required_verification: Whether verification is required
            required_specializations: List of allowed specializations
            
        Returns:
            True if provider has permissions
            
        Raises:
            HTTPException: If permissions are insufficient
        """
        # Check verification status
        if required_verification and current_provider.verification_status != "verified":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account verification required"
            )
        
        # Check specialization
        if required_specializations and current_provider.specialization not in required_specializations:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this specialization"
            )
        
        return True

    def _is_account_locked(self, provider: Provider) -> bool:
        """Check if provider account is currently locked."""
        if not provider.locked_until:
            return False
        
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) < provider.locked_until


# Global auth middleware instance
auth_middleware = AuthMiddleware()


# Dependency functions for FastAPI
async def get_current_provider(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Provider:
    """Dependency to get current authenticated provider."""
    return await auth_middleware.get_current_provider(request, credentials, db)


async def get_optional_current_provider(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Provider]:
    """Dependency to get current provider if authenticated."""
    return await auth_middleware.get_optional_current_provider(request, credentials, db)


def require_verification(current_provider: Provider = Depends(get_current_provider)) -> Provider:
    """Dependency that requires verified provider."""
    auth_middleware.verify_provider_permissions(current_provider, required_verification=True)
    return current_provider


def require_specialization(specializations: list):
    """Dependency factory that requires specific specializations."""
    def _require_specialization(current_provider: Provider = Depends(get_current_provider)) -> Provider:
        auth_middleware.verify_provider_permissions(
            current_provider,
            required_specializations=specializations
        )
        return current_provider
    
    return _require_specialization
