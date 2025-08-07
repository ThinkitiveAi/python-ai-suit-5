"""
Provider Availability and Appointment Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Time, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import enum

class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"
    TENTATIVE = "tentative"
    BREAK = "break"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class RecurringPattern(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"

class ProviderAvailability(Base):
    __tablename__ = "provider_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=False, default=30)  # in minutes
    status = Column(Enum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE, nullable=False)
    appointment_type = Column(String(100))
    notes = Column(Text)
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(Enum(RecurringPattern), default=RecurringPattern.NONE)
    recurring_end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    provider = relationship("Provider", back_populates="availability_slots")
    appointments = relationship("Appointment", back_populates="availability_slot")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    availability_id = Column(Integer, ForeignKey("provider_availability.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    appointment_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    appointment_type = Column(String(100), nullable=False)
    reason = Column(Text)
    notes = Column(Text)
    patient_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    availability_slot = relationship("ProviderAvailability", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    provider = relationship("Provider", back_populates="appointments")

class AvailabilityTemplate(Base):
    __tablename__ = "availability_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    provider = relationship("Provider", back_populates="availability_templates")
    template_slots = relationship("TemplateTimeSlot", back_populates="template")

class TemplateTimeSlot(Base):
    __tablename__ = "template_time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("availability_templates.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=False, default=30)  # in minutes
    appointment_type = Column(String(100))
    notes = Column(Text)
    
    # Relationships
    template = relationship("AvailabilityTemplate", back_populates="template_slots") 