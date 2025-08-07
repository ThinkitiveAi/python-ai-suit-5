"""
Service layer for Provider Availability and Appointment management.
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, time, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
import logging

from db.models.availability import (
    ProviderAvailability, 
    Appointment, 
    AvailabilityTemplate, 
    TemplateTimeSlot,
    AvailabilityStatus,
    AppointmentStatus,
    RecurringPattern
)
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
    AppointmentFilter
)

logger = logging.getLogger(__name__)

class AvailabilityService:
    def __init__(self, db: Session):
        self.db = db

    # Provider Availability CRUD operations
    async def create_availability(self, availability_data: AvailabilityCreate) -> AvailabilityResponse:
        """Create a new availability slot."""
        try:
            # Check for conflicts
            conflict = self.db.query(ProviderAvailability).filter(
                and_(
                    ProviderAvailability.provider_id == availability_data.provider_id,
                    ProviderAvailability.date == availability_data.date,
                    or_(
                        and_(
                            ProviderAvailability.start_time <= availability_data.start_time,
                            ProviderAvailability.end_time > availability_data.start_time
                        ),
                        and_(
                            ProviderAvailability.start_time < availability_data.end_time,
                            ProviderAvailability.end_time >= availability_data.end_time
                        ),
                        and_(
                            ProviderAvailability.start_time >= availability_data.start_time,
                            ProviderAvailability.end_time <= availability_data.end_time
                        )
                    )
                )
            ).first()

            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Time slot conflicts with existing availability"
                )

            # Create availability slot
            db_availability = ProviderAvailability(
                provider_id=availability_data.provider_id,
                date=availability_data.date,
                start_time=availability_data.start_time,
                end_time=availability_data.end_time,
                duration=availability_data.duration,
                status=availability_data.status,
                appointment_type=availability_data.appointment_type,
                notes=availability_data.notes,
                is_recurring=availability_data.is_recurring,
                recurring_pattern=availability_data.recurring_pattern,
                recurring_end_date=availability_data.recurring_end_date
            )

            self.db.add(db_availability)
            self.db.commit()
            self.db.refresh(db_availability)

            logger.info(f"Created availability slot {db_availability.id} for provider {availability_data.provider_id}")
            return AvailabilityResponse.from_orm(db_availability)

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating availability: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create availability slot"
            )

    async def get_availability(self, availability_id: int) -> Optional[AvailabilityResponse]:
        """Get a specific availability slot by ID."""
        try:
            availability = self.db.query(ProviderAvailability).filter(
                ProviderAvailability.id == availability_id
            ).first()

            if not availability:
                return None

            return AvailabilityResponse.from_orm(availability)

        except Exception as e:
            logger.error(f"Error retrieving availability {availability_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve availability slot"
            )

    async def get_provider_availability(
        self, 
        provider_id: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status_filter: Optional[AvailabilityStatus] = None
    ) -> List[AvailabilityResponse]:
        """Get availability slots for a provider with optional filtering."""
        try:
            query = self.db.query(ProviderAvailability).filter(
                ProviderAvailability.provider_id == provider_id
            )

            if start_date:
                query = query.filter(ProviderAvailability.date >= start_date)
            if end_date:
                query = query.filter(ProviderAvailability.date <= end_date)
            if status_filter:
                query = query.filter(ProviderAvailability.status == status_filter)

            query = query.order_by(ProviderAvailability.date, ProviderAvailability.start_time)
            availabilities = query.all()

            return [AvailabilityResponse.from_orm(avail) for avail in availabilities]

        except Exception as e:
            logger.error(f"Error retrieving availability for provider {provider_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve availability slots"
            )

    async def update_availability(
        self, 
        availability_id: int, 
        update_data: AvailabilityUpdate
    ) -> Optional[AvailabilityResponse]:
        """Update an availability slot."""
        try:
            availability = self.db.query(ProviderAvailability).filter(
                ProviderAvailability.id == availability_id
            ).first()

            if not availability:
                return None

            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(availability, field, value)

            availability.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(availability)

            logger.info(f"Updated availability slot {availability_id}")
            return AvailabilityResponse.from_orm(availability)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating availability {availability_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update availability slot"
            )

    async def delete_availability(self, availability_id: int) -> bool:
        """Delete an availability slot."""
        try:
            availability = self.db.query(ProviderAvailability).filter(
                ProviderAvailability.id == availability_id
            ).first()

            if not availability:
                return False

            # Check if slot has appointments
            appointments = self.db.query(Appointment).filter(
                Appointment.availability_id == availability_id
            ).count()

            if appointments > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete availability slot with existing appointments"
                )

            self.db.delete(availability)
            self.db.commit()

            logger.info(f"Deleted availability slot {availability_id}")
            return True

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting availability {availability_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete availability slot"
            )

    # Appointment CRUD operations
    async def create_appointment(self, appointment_data: AppointmentCreate) -> AppointmentResponse:
        """Create a new appointment."""
        try:
            # Verify availability slot exists and is available
            availability = self.db.query(ProviderAvailability).filter(
                ProviderAvailability.id == appointment_data.availability_id
            ).first()

            if not availability:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Availability slot not found"
                )

            if availability.status != AvailabilityStatus.AVAILABLE:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Availability slot is not available for booking"
                )

            # Create appointment
            db_appointment = Appointment(
                availability_id=appointment_data.availability_id,
                patient_id=appointment_data.patient_id,
                provider_id=appointment_data.provider_id,
                appointment_date=appointment_data.appointment_date,
                start_time=appointment_data.start_time,
                end_time=appointment_data.end_time,
                appointment_type=appointment_data.appointment_type,
                reason=appointment_data.reason,
                notes=appointment_data.notes,
                patient_notes=appointment_data.patient_notes
            )

            # Update availability status
            availability.status = AvailabilityStatus.BOOKED

            self.db.add(db_appointment)
            self.db.commit()
            self.db.refresh(db_appointment)

            logger.info(f"Created appointment {db_appointment.id} for patient {appointment_data.patient_id}")
            return AppointmentResponse.from_orm(db_appointment)

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating appointment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create appointment"
            )

    async def get_appointment(self, appointment_id: int) -> Optional[AppointmentResponse]:
        """Get a specific appointment by ID."""
        try:
            appointment = self.db.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()

            if not appointment:
                return None

            return AppointmentResponse.from_orm(appointment)

        except Exception as e:
            logger.error(f"Error retrieving appointment {appointment_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve appointment"
            )

    async def get_provider_appointments(
        self, 
        provider_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status_filter: Optional[AppointmentStatus] = None
    ) -> List[AppointmentResponse]:
        """Get appointments for a provider with optional filtering."""
        try:
            query = self.db.query(Appointment).filter(
                Appointment.provider_id == provider_id
            )

            if start_date:
                query = query.filter(Appointment.appointment_date >= start_date)
            if end_date:
                query = query.filter(Appointment.appointment_date <= end_date)
            if status_filter:
                query = query.filter(Appointment.status == status_filter)

            query = query.order_by(Appointment.appointment_date, Appointment.start_time)
            appointments = query.all()

            return [AppointmentResponse.from_orm(apt) for apt in appointments]

        except Exception as e:
            logger.error(f"Error retrieving appointments for provider {provider_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve appointments"
            )

    async def update_appointment(
        self, 
        appointment_id: int, 
        update_data: AppointmentUpdate
    ) -> Optional[AppointmentResponse]:
        """Update an appointment."""
        try:
            appointment = self.db.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()

            if not appointment:
                return None

            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(appointment, field, value)

            appointment.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(appointment)

            logger.info(f"Updated appointment {appointment_id}")
            return AppointmentResponse.from_orm(appointment)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating appointment {appointment_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update appointment"
            )

    async def delete_appointment(self, appointment_id: int) -> bool:
        """Delete an appointment."""
        try:
            appointment = self.db.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()

            if not appointment:
                return False

            # Reset availability slot status
            availability = self.db.query(ProviderAvailability).filter(
                ProviderAvailability.id == appointment.availability_id
            ).first()

            if availability:
                availability.status = AvailabilityStatus.AVAILABLE

            self.db.delete(appointment)
            self.db.commit()

            logger.info(f"Deleted appointment {appointment_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting appointment {appointment_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete appointment"
            )

    # Statistics and reporting
    async def get_availability_stats(self, provider_id: str, start_date: date, end_date: date) -> AvailabilityStats:
        """Get availability statistics for a provider."""
        try:
            query = self.db.query(ProviderAvailability).filter(
                and_(
                    ProviderAvailability.provider_id == provider_id,
                    ProviderAvailability.date >= start_date,
                    ProviderAvailability.date <= end_date
                )
            )

            total_slots = query.count()
            available_slots = query.filter(ProviderAvailability.status == AvailabilityStatus.AVAILABLE).count()
            booked_slots = query.filter(ProviderAvailability.status == AvailabilityStatus.BOOKED).count()
            blocked_slots = query.filter(ProviderAvailability.status == AvailabilityStatus.BLOCKED).count()

            utilization_rate = (booked_slots / total_slots * 100) if total_slots > 0 else 0

            return AvailabilityStats(
                total_slots=total_slots,
                available_slots=available_slots,
                booked_slots=booked_slots,
                blocked_slots=blocked_slots,
                utilization_rate=utilization_rate
            )

        except Exception as e:
            logger.error(f"Error calculating availability stats for provider {provider_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate availability statistics"
            )

    async def get_appointment_stats(self, provider_id: str, start_date: date, end_date: date) -> AppointmentStats:
        """Get appointment statistics for a provider."""
        try:
            query = self.db.query(Appointment).filter(
                and_(
                    Appointment.provider_id == provider_id,
                    Appointment.appointment_date >= start_date,
                    Appointment.appointment_date <= end_date
                )
            )

            total_appointments = query.count()
            scheduled_appointments = query.filter(Appointment.status == AppointmentStatus.SCHEDULED).count()
            confirmed_appointments = query.filter(Appointment.status == AppointmentStatus.CONFIRMED).count()
            completed_appointments = query.filter(Appointment.status == AppointmentStatus.COMPLETED).count()
            cancelled_appointments = query.filter(Appointment.status == AppointmentStatus.CANCELLED).count()
            no_show_appointments = query.filter(Appointment.status == AppointmentStatus.NO_SHOW).count()

            completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0

            return AppointmentStats(
                total_appointments=total_appointments,
                scheduled_appointments=scheduled_appointments,
                confirmed_appointments=confirmed_appointments,
                completed_appointments=completed_appointments,
                cancelled_appointments=cancelled_appointments,
                no_show_appointments=no_show_appointments,
                completion_rate=completion_rate
            )

        except Exception as e:
            logger.error(f"Error calculating appointment stats for provider {provider_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate appointment statistics"
            )

# Service instance
availability_service = AvailabilityService 