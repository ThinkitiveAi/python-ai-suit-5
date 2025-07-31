"""
Authentication endpoints for provider login, logout, and token management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from db.database import get_db
from db.models.provider import Provider
from schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    LogoutRequest, LogoutResponse, LogoutAllResponse, AuthErrorResponse,
    AccountLockedResponse
)
from services.auth_service import auth_service
from middlewares.auth_middleware import get_current_provider
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/hour")  # 10 login attempts per hour per IP
async def login_provider(
    request: Request,
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate provider and return JWT tokens.
    
    - **identifier**: Email address or phone number
    - **password**: Provider's password
    - **remember_me**: Extend token expiry for longer sessions
    
    Returns access token, refresh token, and provider information.
    """
    try:
        success, login_data, error_message, lock_info = auth_service.authenticate_provider(
            db, login_request
        )
        
        if not success:
            # Handle account locked scenario
            if lock_info:
                return JSONResponse(
                    status_code=status.HTTP_423_LOCKED,
                    content=AccountLockedResponse(
                        details=lock_info
                    ).model_dump()
                )
            
            # Handle other authentication failures
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=AuthErrorResponse(
                    message=error_message or "Authentication failed",
                    error_code="INVALID_CREDENTIALS"
                ).model_dump()
            )
        
        return LoginResponse(data=login_data)
        
    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=AuthErrorResponse(
                message="Internal server error",
                error_code="SERVER_ERROR"
            ).model_dump()
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
@limiter.limit("20/hour")  # 20 refresh attempts per hour per IP
async def refresh_access_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token with updated expiry.
    """
    try:
        success, access_token, expires_in, error_message = auth_service.refresh_access_token(
            db, refresh_request.refresh_token
        )
        
        if not success:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=AuthErrorResponse(
                    message=error_message or "Token refresh failed",
                    error_code="INVALID_REFRESH_TOKEN"
                ).model_dump()
            )
        
        from schemas.auth import RefreshTokenData
        return RefreshTokenResponse(
            data=RefreshTokenData(
                access_token=access_token,
                expires_in=expires_in
            )
        )
        
    except Exception as e:
        logger.error(f"Refresh endpoint error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=AuthErrorResponse(
                message="Internal server error",
                error_code="SERVER_ERROR"
            ).model_dump()
        )


@router.post("/logout", response_model=LogoutResponse)
@limiter.limit("30/hour")  # 30 logout attempts per hour per IP
async def logout_provider(
    request: Request,
    logout_request: LogoutRequest,
    db: Session = Depends(get_db),
    current_provider: Provider = Depends(get_current_provider)
):
    """
    Logout provider by revoking refresh token.
    
    - **refresh_token**: Refresh token to revoke
    
    Requires valid access token in Authorization header.
    """
    try:
        success, error_message = auth_service.logout_provider(
            db, logout_request.refresh_token
        )
        
        if not success:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=AuthErrorResponse(
                    message=error_message or "Logout failed",
                    error_code="LOGOUT_FAILED"
                ).model_dump()
            )
        
        return LogoutResponse()
        
    except Exception as e:
        logger.error(f"Logout endpoint error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=AuthErrorResponse(
                message="Internal server error",
                error_code="SERVER_ERROR"
            ).model_dump()
        )


@router.post("/logout-all", response_model=LogoutAllResponse)
@limiter.limit("10/hour")  # 10 logout-all attempts per hour per IP
async def logout_all_sessions(
    request: Request,
    db: Session = Depends(get_db),
    current_provider: Provider = Depends(get_current_provider)
):
    """
    Logout provider from all sessions by revoking all refresh tokens.
    
    Requires valid access token in Authorization header.
    """
    try:
        success, error_message = auth_service.logout_all_sessions(
            db, str(current_provider.id)
        )
        
        if not success:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=AuthErrorResponse(
                    message=error_message or "Logout all failed",
                    error_code="LOGOUT_ALL_FAILED"
                ).model_dump()
            )
        
        return LogoutAllResponse()
        
    except Exception as e:
        logger.error(f"Logout all endpoint error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=AuthErrorResponse(
                message="Internal server error",
                error_code="SERVER_ERROR"
            ).model_dump()
        )


@router.get("/me")
@limiter.limit("60/hour")  # 60 profile requests per hour per IP
async def get_current_provider_info(
    request: Request,
    current_provider: Provider = Depends(get_current_provider)
):
    """
    Get current authenticated provider information.
    
    Requires valid access token in Authorization header.
    """
    try:
        from schemas.provider import ProviderResponse
        
        provider_response = ProviderResponse(
            id=str(current_provider.id),
            email=current_provider.email,
            first_name=current_provider.first_name,
            last_name=current_provider.last_name,
            phone_number=current_provider.phone_number,
            specialization=current_provider.specialization,
            license_number=current_provider.license_number,
            years_of_experience=current_provider.years_of_experience,
            verification_status=current_provider.verification_status,
            is_active=current_provider.is_active,
            created_at=current_provider.created_at,
            updated_at=current_provider.updated_at
        )
        
        return {
            "success": True,
            "message": "Provider information retrieved successfully",
            "data": provider_response
        }
        
    except Exception as e:
        logger.error(f"Get provider info error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=AuthErrorResponse(
                message="Internal server error",
                error_code="SERVER_ERROR"
            ).model_dump()
        )


@router.get("/token/verify")
@limiter.limit("100/hour")  # 100 token verification requests per hour per IP
async def verify_token(
    request: Request,
    current_provider: Provider = Depends(get_current_provider)
):
    """
    Verify if the current access token is valid.
    
    Requires valid access token in Authorization header.
    """
    try:
        return {
            "success": True,
            "message": "Token is valid",
            "data": {
                "provider_id": str(current_provider.id),
                "email": current_provider.email,
                "is_active": current_provider.is_active,
                "verification_status": current_provider.verification_status
            }
        }
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=AuthErrorResponse(
                message="Internal server error",
                error_code="SERVER_ERROR"
            ).model_dump()
        )
