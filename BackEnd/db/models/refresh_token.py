"""
Database models for refresh tokens.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base


class RefreshToken(Base):
    """
    RefreshToken model for managing JWT refresh tokens.
    """
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False, index=True)
    token_hash = Column(Text, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    provider = relationship("ProviderSQL", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, provider_id={self.provider_id}, is_revoked={self.is_revoked})>"

    @property
    def is_expired(self) -> bool:
        """Check if the refresh token is expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the refresh token is valid (not expired and not revoked)."""
        return not self.is_expired and not self.is_revoked

    def revoke(self):
        """Revoke the refresh token."""
        self.is_revoked = True

    def mark_used(self):
        """Mark the token as used by updating last_used_at."""
        self.last_used_at = datetime.now(timezone.utc)
