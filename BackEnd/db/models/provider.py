"""
Provider database models for both SQL and NoSQL databases.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import uuid

# RefreshToken relationship uses string reference to avoid circular imports


class ProviderSQL(Base):
    """SQLAlchemy model for Provider table."""
    
    __tablename__ = "providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    specialization = Column(String(100), nullable=False, index=True)
    license_number = Column(String(50), unique=True, nullable=False, index=True)
    years_of_experience = Column(Integer, nullable=False)
    clinic_address = Column(JSON, nullable=False)
    verification_status = Column(String(20), default="pending", nullable=False, index=True)
    verification_token = Column(String(100), nullable=True, index=True)
    license_document_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Login-related fields
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    # refresh_tokens = relationship("RefreshToken", back_populates="provider", cascade="all, delete-orphan")
    availability_slots = relationship("ProviderAvailability", back_populates="provider", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="provider", cascade="all, delete-orphan")
    availability_templates = relationship("AvailabilityTemplate", back_populates="provider", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Provider(id={self.id}, email={self.email}, specialization={self.specialization})>"


class ProviderMongo:
    """MongoDB document structure for Provider collection."""
    
    @staticmethod
    def get_collection_name() -> str:
        return "providers"
    
    @staticmethod
    def get_indexes():
        """Return list of indexes to create for the collection."""
        return [
            {"key": "email", "unique": True},
            {"key": "phone_number", "unique": True},
            {"key": "license_number", "unique": True},
            {"key": "verification_status"},
            {"key": "verification_token"},
            {"key": "specialization"},
            {"key": "is_active"},
            {"key": "created_at"},
        ]
    
    @staticmethod
    def create_document(provider_data: dict) -> dict:
        """Create a MongoDB document from provider data."""
        document = {
            "_id": str(uuid.uuid4()),
            "first_name": provider_data["first_name"],
            "last_name": provider_data["last_name"],
            "email": provider_data["email"].lower(),
            "phone_number": provider_data["phone_number"],
            "password_hash": provider_data["password_hash"],
            "specialization": provider_data["specialization"],
            "license_number": provider_data["license_number"],
            "years_of_experience": provider_data["years_of_experience"],
            "clinic_address": provider_data["clinic_address"],
            "verification_status": "pending",
            "verification_token": provider_data.get("verification_token"),
            "license_document_url": provider_data.get("license_document_url"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        return document
    
    @staticmethod
    def update_document(update_data: dict) -> dict:
        """Update a MongoDB document with new data."""
        update_data["updated_at"] = datetime.utcnow()
        return {"$set": update_data}


class AuditLog:
    """Audit logging for provider registration attempts."""
    
    @staticmethod
    def create_audit_entry(
        ip_address: str,
        email: str,
        action: str,
        status: str,
        details: Optional[str] = None
    ) -> dict:
        """Create an audit log entry."""
        return {
            "timestamp": datetime.utcnow(),
            "ip_address": ip_address,
            "email": email,
            "action": action,
            "status": status,
            "details": details,
        }


class AuditLogSQL(Base):
    """SQLAlchemy model for audit log table."""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 support
    email = Column(String(255), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    details = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AuditLog(email={self.email}, action={self.action}, status={self.status})>"


# Aliases for compatibility
Provider = ProviderSQL
AuditLog = AuditLogSQL
