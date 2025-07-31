"""
Provider API endpoints for registration and management.
"""
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Dict, Any
import logging

from schemas.provider import (
    ProviderRegistrationRequest, 
    ProviderRegistrationResponse,
    ErrorResponse,
    ValidationErrorResponse
)
from services.provider_service import provider_service
from middlewares.rate_limiting import rate_limit_dependency, get_client_ip
from core.config import settings

logger = logging.getLogger(__name__)

# Create router for provider endpoints
router = APIRouter(tags=["Provider Registration"])


@router.post(
    "/register",
    response_model=ProviderRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new healthcare provider",
    description="Register a new healthcare provider with comprehensive validation, security measures, and email verification.",
    responses={
        201: {
            "description": "Provider registered successfully",
            "model": ProviderRegistrationResponse
        },
        400: {
            "description": "Bad request - Invalid input data",
            "model": ErrorResponse
        },
        409: {
            "description": "Conflict - Duplicate email, phone, or license number",
            "model": ErrorResponse
        },
        422: {
            "description": "Validation error - Input validation failed",
            "model": ValidationErrorResponse
        },
        429: {
            "description": "Too many requests - Rate limit exceeded",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def register_provider(
    provider_data: ProviderRegistrationRequest,
    request: Request,
    rate_limit_info: Dict[str, Any] = Depends(rate_limit_dependency)
) -> JSONResponse:
    """
    Register a new healthcare provider.
    
    This endpoint handles the complete provider registration process including:
    - Comprehensive input validation
    - Duplicate checking (email, phone, license number)
    - Password strength validation and hashing
    - Email verification token generation
    - Audit logging
    - Rate limiting (5 attempts per hour per IP)
    
    Args:
        provider_data: Provider registration information
        request: FastAPI request object
        rate_limit_info: Rate limiting information from dependency
        
    Returns:
        JSON response with registration result
        
    Raises:
        HTTPException: For various error conditions
    """
    client_ip = rate_limit_info["client_ip"]
    
    try:
        logger.info(f"Provider registration attempt from IP: {client_ip}, Email: {provider_data.email}")
        
        # Process registration through service layer
        success, result = await provider_service.register_provider(
            provider_data=provider_data,
            client_ip=client_ip
        )
        
        if success:
            # Successful registration
            logger.info(f"Provider registered successfully: {provider_data.email}")
            
            response_data = ProviderRegistrationResponse(
                success=True,
                message=result["message"],
                data=result["data"]
            )
            
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=response_data.dict(),
                headers={
                    "X-RateLimit-Remaining": str(rate_limit_info["remaining_requests"] - 1)
                }
            )
        
        else:
            # Registration failed
            error_details = result
            
            # Determine appropriate status code based on error type
            if "field" in error_details:
                # Duplicate field error
                status_code = status.HTTP_409_CONFLICT
                logger.warning(f"Duplicate field error for {provider_data.email}: {error_details['field']}")
            elif "errors" in error_details:
                # Validation errors
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                logger.warning(f"Validation errors for {provider_data.email}: {error_details['errors']}")
            else:
                # General error
                status_code = status.HTTP_400_BAD_REQUEST
                logger.error(f"Registration error for {provider_data.email}: {error_details['message']}")
            
            return JSONResponse(
                status_code=status_code,
                content={
                    "success": False,
                    "message": error_details["message"],
                    "details": error_details.get("errors") or error_details.get("field")
                },
                headers={
                    "X-RateLimit-Remaining": str(rate_limit_info["remaining_requests"] - 1)
                }
            )
    
    except ValidationError as e:
        # Pydantic validation error
        logger.warning(f"Pydantic validation error for {provider_data.email}: {e}")
        
        validation_errors = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            validation_errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation failed",
                "errors": validation_errors
            }
        )
    
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error during provider registration: {e}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "An unexpected error occurred. Please try again later.",
                "details": "Internal server error" if not settings.DEBUG else str(e)
            }
        )


@router.get(
    "/specializations",
    summary="Get list of allowed medical specializations",
    description="Retrieve the list of allowed medical specializations for provider registration.",
    response_model=Dict[str, Any]
)
async def get_specializations() -> Dict[str, Any]:
    """
    Get list of allowed medical specializations.
    
    Returns:
        Dictionary containing list of allowed specializations
    """
    return {
        "success": True,
        "message": "Specializations retrieved successfully",
        "data": {
            "specializations": settings.ALLOWED_SPECIALIZATIONS,
            "count": len(settings.ALLOWED_SPECIALIZATIONS)
        }
    }


@router.get(
    "/password-requirements",
    summary="Get password requirements",
    description="Retrieve password requirements for client-side validation.",
    response_model=Dict[str, Any]
)
async def get_password_requirements() -> Dict[str, Any]:
    """
    Get password requirements for client-side validation.
    
    Returns:
        Dictionary containing password requirements
    """
    from utils.password_utils import PasswordValidator
    
    requirements = PasswordValidator.generate_password_requirements()
    
    return {
        "success": True,
        "message": "Password requirements retrieved successfully",
        "data": requirements
    }


@router.get(
    "/health",
    summary="Health check endpoint",
    description="Check the health status of the provider registration service.",
    response_model=Dict[str, Any]
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring.
    
    Returns:
        Health status information
    """
    import time
    from datetime import datetime
    
    return {
        "success": True,
        "message": "Provider registration service is healthy",
        "data": {
            "service": "Provider Registration API",
            "version": settings.APP_VERSION,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time()
        }
    }
