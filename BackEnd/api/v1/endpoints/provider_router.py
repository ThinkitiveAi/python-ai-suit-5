"""
Provider-specific router that includes provider authentication and management endpoints.
"""
from fastapi import APIRouter
from api.v1.endpoints import provider_auth

router = APIRouter()

# Include provider authentication endpoints
router.include_router(
    provider_auth.router,
    prefix="",
    tags=["provider-auth"]
)
