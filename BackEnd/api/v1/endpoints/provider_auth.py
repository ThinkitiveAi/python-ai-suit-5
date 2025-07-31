"""
Provider authentication endpoints for JWT-based login.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from db.database import get_db
from schemas.provider_auth import (
    ProviderLoginRequest, ProviderLoginResponse
)
from services.provider_auth_service import provider_auth_service
import logging

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/login", response_model=ProviderLoginResponse)
@limiter.limit("5/hour")  # 5 login attempts per hour per IP
async def provider_login(
    request: Request,
    login_request: ProviderLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate provider and return JWT access token.
    
    - **email**: Provider's email address
    - **password**: Provider's password
    
    Returns access token with 1 hour expiry and provider information.
    
    **JWT Token Configuration:**
    - Access Token Expiry: 1 hour
    - Payload: provider_id, email, role, specialization
    
    **Authentication Logic:**
    - Accept login with email + password
    - Verify password using bcrypt comparison
    - Generate JWT access token
    
    **Validation Rules:**
    - Email must be valid format
    - Password must be provided and non-empty
    """
    try:
        success, login_data, error_message = provider_auth_service.authenticate_provider(
            db, login_request
        )
        
        if not success:
            # Log failed authentication attempt
            logger.warning(
                f"Failed login attempt from IP {request.client.host} "
                f"for email: {login_request.email}"
            )
            
            # Return 401 Unauthorized for any authentication failure
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "message": error_message or "Authentication failed",
                    "error_code": "INVALID_CREDENTIALS"
                }
            )
        
        # Log successful authentication
        logger.info(
            f"Successful login from IP {request.client.host} "
            f"for email: {login_request.email}"
        )
        
        return ProviderLoginResponse(data=login_data)
        
    except Exception as e:
        logger.error(f"Provider login endpoint error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "SERVER_ERROR"
            }
        )
