"""
API endpoints for Provider Availability and Appointment management.
"""
from fastapi import APIRouter, HTTPException, Request, Depends, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import logging

from schemas.availability import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AvailabilityTemplateCreate,
    AvailabilityTemplateUpdate,
    AvailabilityTemplateResponse,
    AvailabilityStats,
    AppointmentStats,
    AvailabilityFilter,
    AppointmentFilter,
    AvailabilityStatus,
    AppointmentStatus
)
from services.availability_service import AvailabilityService
from db.database import get_db
from middlewares.auth_middleware import get_current_provider
from middlewares.rate_limiting import rate_limit_dependency, get_client_ip

logger = logging.getLogger(__name__)

# Create router for availability endpoints
router = APIRouter(prefix="/availability", tags=["Provider Availability"])

# Dependency to get database session
def get_availability_service(db=Depends(get_db)) -> AvailabilityService:
    return AvailabilityService(db)

# Provider Availability endpoints
@router.post(
    "/slots",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create availability slot",
    description="Create a new availability slot for a provider."
)
async def create_availability(
    availability_data: AvailabilityCreate,
    request: Request,
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider),
    rate_limit_info: Dict[str, Any] = Depends(rate_limit_dependency)
):
    """Create a new availability slot."""
    try:
        # Ensure provider can only create slots for themselves
        if availability_data.provider_id != str(current_provider["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only create availability slots for your own account"
            )

        result = await service.create_availability(availability_data)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating availability: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create availability slot"
        )

@router.get(
    "/slots/{availability_id}",
    response_model=AvailabilityResponse,
    summary="Get availability slot",
    description="Get a specific availability slot by ID."
)
async def get_availability(
    availability_id: int,
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Get a specific availability slot."""
    try:
        result = await service.get_availability(availability_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability slot not found"
            )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving availability {availability_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve availability slot"
        )

@router.get(
    "/slots",
    response_model=List[AvailabilityResponse],
    summary="Get provider availability",
    description="Get availability slots for a provider with optional filtering."
)
async def get_provider_availability(
    provider_id: Optional[str] = Query(None, description="Provider ID (defaults to current provider)"),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    status_filter: Optional[AvailabilityStatus] = Query(None, description="Status filter"),
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Get availability slots for a provider."""
    try:
        # Use current provider if no provider_id specified
        if not provider_id:
            provider_id = str(current_provider["id"])
        elif provider_id != str(current_provider["id"]):
            # For now, only allow providers to see their own availability
            # In the future, this could be expanded for admin access
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view your own availability slots"
            )

        result = await service.get_provider_availability(
            provider_id=provider_id,
            start_date=start_date,
            end_date=end_date,
            status_filter=status_filter
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving availability for provider {provider_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve availability slots"
        )

@router.put(
    "/slots/{availability_id}",
    response_model=AvailabilityResponse,
    summary="Update availability slot",
    description="Update an existing availability slot."
)
async def update_availability(
    availability_id: int,
    update_data: AvailabilityUpdate,
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Update an availability slot."""
    try:
        # Verify ownership
        existing = await service.get_availability(availability_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability slot not found"
            )
        
        if existing.provider_id != str(current_provider["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update your own availability slots"
            )

        result = await service.update_availability(availability_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability slot not found"
            )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating availability {availability_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update availability slot"
        )

@router.delete(
    "/slots/{availability_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete availability slot",
    description="Delete an availability slot."
)
async def delete_availability(
    availability_id: int,
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Delete an availability slot."""
    try:
        # Verify ownership
        existing = await service.get_availability(availability_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability slot not found"
            )
        
        if existing.provider_id != str(current_provider["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only delete your own availability slots"
            )

        success = await service.delete_availability(availability_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Availability slot not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting availability {availability_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete availability slot"
        )

# Appointment endpoints
@router.post(
    "/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create appointment",
    description="Create a new appointment."
)
async def create_appointment(
    appointment_data: AppointmentCreate,
    request: Request,
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider),
    rate_limit_info: Dict[str, Any] = Depends(rate_limit_dependency)
):
    """Create a new appointment."""
    try:
        # Ensure provider can only create appointments for themselves
        if appointment_data.provider_id != str(current_provider["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only create appointments for your own account"
            )

        result = await service.create_appointment(appointment_data)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create appointment"
        )

@router.get(
    "/appointments/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Get appointment",
    description="Get a specific appointment by ID."
)
async def get_appointment(
    appointment_id: int,
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Get a specific appointment."""
    try:
        result = await service.get_appointment(appointment_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Verify ownership
        if result.provider_id != str(current_provider["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view your own appointments"
            )
        
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving appointment {appointment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve appointment"
        )

@router.get(
    "/appointments",
    response_model=List[AppointmentResponse],
    summary="Get provider appointments",
    description="Get appointments for a provider with optional filtering."
)
async def get_provider_appointments(
    provider_id: Optional[str] = Query(None, description="Provider ID (defaults to current provider)"),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    status_filter: Optional[AppointmentStatus] = Query(None, description="Status filter"),
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Get appointments for a provider."""
    try:
        # Use current provider if no provider_id specified
        if not provider_id:
            provider_id = str(current_provider["id"])
        elif provider_id != str(current_provider["id"]):
            # For now, only allow providers to see their own appointments
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view your own appointments"
            )

        result = await service.get_provider_appointments(
            provider_id=provider_id,
            start_date=start_date,
            end_date=end_date,
            status_filter=status_filter
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving appointments for provider {provider_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve appointments"
        )

@router.put(
    "/appointments/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Update appointment",
    description="Update an existing appointment."
)
async def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Update an appointment."""
    try:
        # Verify ownership
        existing = await service.get_appointment(appointment_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        if existing.provider_id != str(current_provider["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update your own appointments"
            )

        result = await service.update_appointment(appointment_id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment {appointment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update appointment"
        )

@router.delete(
    "/appointments/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete appointment",
    description="Delete an appointment."
)
async def delete_appointment(
    appointment_id: int,
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Delete an appointment."""
    try:
        # Verify ownership
        existing = await service.get_appointment(appointment_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        if existing.provider_id != str(current_provider["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only delete your own appointments"
            )

        success = await service.delete_appointment(appointment_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting appointment {appointment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete appointment"
        )

# Statistics endpoints
@router.get(
    "/stats/availability",
    response_model=AvailabilityStats,
    summary="Get availability statistics",
    description="Get availability statistics for a provider."
)
async def get_availability_stats(
    provider_id: Optional[str] = Query(None, description="Provider ID (defaults to current provider)"),
    start_date: date = Query(..., description="Start date for statistics"),
    end_date: date = Query(..., description="End date for statistics"),
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Get availability statistics for a provider."""
    try:
        # Use current provider if no provider_id specified
        if not provider_id:
            provider_id = str(current_provider["id"])
        elif provider_id != str(current_provider["id"]):
            # For now, only allow providers to see their own statistics
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view your own statistics"
            )

        result = await service.get_availability_stats(provider_id, start_date, end_date)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating availability stats for provider {provider_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate availability statistics"
        )

@router.get(
    "/stats/appointments",
    response_model=AppointmentStats,
    summary="Get appointment statistics",
    description="Get appointment statistics for a provider."
)
async def get_appointment_stats(
    provider_id: Optional[str] = Query(None, description="Provider ID (defaults to current provider)"),
    start_date: date = Query(..., description="Start date for statistics"),
    end_date: date = Query(..., description="End date for statistics"),
    service: AvailabilityService = Depends(get_availability_service),
    current_provider: Dict = Depends(get_current_provider)
):
    """Get appointment statistics for a provider."""
    try:
        # Use current provider if no provider_id specified
        if not provider_id:
            provider_id = str(current_provider["id"])
        elif provider_id != str(current_provider["id"]):
            # For now, only allow providers to see their own statistics
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view your own statistics"
            )

        result = await service.get_appointment_stats(provider_id, start_date, end_date)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating appointment stats for provider {provider_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate appointment statistics"
        ) 