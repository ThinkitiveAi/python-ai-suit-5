"""
Pydantic schemas for Provider Availability and Appointment management.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, time, datetime
from enum import Enum

class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"
    TENTATIVE = "tentative"
    BREAK = "break"

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class RecurringPattern(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"

# Base schemas
class AvailabilityBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    duration: int = Field(30, ge=15, le=480)  # 15 minutes to 8 hours
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    appointment_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    is_recurring: bool = False
    recurring_pattern: RecurringPattern = RecurringPattern.NONE
    recurring_end_date: Optional[date] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

    @validator('recurring_end_date')
    def validate_recurring_end_date(cls, v, values):
        if values.get('is_recurring') and v and 'date' in values:
            if v <= values['date']:
                raise ValueError('Recurring end date must be after start date')
        return v

class AppointmentBase(BaseModel):
    appointment_date: date
    start_time: time
    end_time: time
    appointment_type: str = Field(..., max_length=100)
    reason: Optional[str] = None
    notes: Optional[str] = None
    patient_notes: Optional[str] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

# Create schemas
class AvailabilityCreate(AvailabilityBase):
    provider_id: str

class AppointmentCreate(AppointmentBase):
    availability_id: int
    patient_id: str
    provider_id: str

# Update schemas
class AvailabilityUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration: Optional[int] = Field(None, ge=15, le=480)
    status: Optional[AvailabilityStatus] = None
    appointment_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_pattern: Optional[RecurringPattern] = None
    recurring_end_date: Optional[date] = None

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[AppointmentStatus] = None
    appointment_type: Optional[str] = Field(None, max_length=100)
    reason: Optional[str] = None
    notes: Optional[str] = None
    patient_notes: Optional[str] = None

# Response schemas
class AvailabilityResponse(AvailabilityBase):
    id: int
    provider_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AppointmentResponse(AppointmentBase):
    id: int
    availability_id: int
    patient_id: str
    provider_id: str
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Template schemas
class TemplateTimeSlotBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    duration: int = Field(30, ge=15, le=480)
    appointment_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class AvailabilityTemplateBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_default: bool = False

class AvailabilityTemplateCreate(AvailabilityTemplateBase):
    provider_id: str
    time_slots: List[TemplateTimeSlotBase]

class AvailabilityTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_default: Optional[bool] = None

class TemplateTimeSlotResponse(TemplateTimeSlotBase):
    id: int
    template_id: int

    class Config:
        from_attributes = True

class AvailabilityTemplateResponse(AvailabilityTemplateBase):
    id: int
    provider_id: str
    time_slots: List[TemplateTimeSlotResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Bulk operations
class BulkAvailabilityCreate(BaseModel):
    provider_id: str
    start_date: date
    end_date: date
    time_slots: List[Dict[str, Any]]  # List of time slot configurations
    template_id: Optional[int] = None

class BulkAvailabilityDelete(BaseModel):
    provider_id: str
    start_date: date
    end_date: date
    status_filter: Optional[AvailabilityStatus] = None

# Statistics and reports
class AvailabilityStats(BaseModel):
    total_slots: int
    available_slots: int
    booked_slots: int
    blocked_slots: int
    utilization_rate: float
    average_booking_time: Optional[float] = None

class AppointmentStats(BaseModel):
    total_appointments: int
    scheduled_appointments: int
    confirmed_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_show_appointments: int
    completion_rate: float

# Search and filter schemas
class AvailabilityFilter(BaseModel):
    provider_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[AvailabilityStatus] = None
    appointment_type: Optional[str] = None

class AppointmentFilter(BaseModel):
    provider_id: Optional[str] = None
    patient_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[AppointmentStatus] = None
    appointment_type: Optional[str] = None

# Error responses
class AvailabilityErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

class AppointmentErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None 