"""User database model and related models."""

from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum

from src.models.base import Base


class SubscriptionTier(str, enum.Enum):
    """User subscription tier enumeration."""

    FREE = "FREE"
    PREMIUM = "PREMIUM"


class User(Base):
    """User model for authentication and profile management."""

    __tablename__ = "users"

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Profile fields
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False
    )
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)

    # Notification settings (stored as JSON)
    notification_settings: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=lambda: {
            "enabled": True,
            "delivery_time": "09:00",
            "weekdays_only": False,
            "pause_until": None,
        },
        nullable=False,
    )

    # Timestamps
    last_login_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_quote_delivered: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    email_verification_token: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    email_verification_expires_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    password_reset_token: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    password_reset_expires_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription", back_populates="user", uselist=False
    )

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"

    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription."""
        return self.subscription_tier == SubscriptionTier.PREMIUM

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for API responses."""
        return {
            "id": str(self.id),
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "subscription_tier": self.subscription_tier.value,
            "timezone": self.timezone,
            "notification_settings": self.notification_settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": (
                self.last_login_at.isoformat() if self.last_login_at else None
            ),
            "last_quote_delivered": (
                self.last_quote_delivered.isoformat()
                if self.last_quote_delivered
                else None
            ),
        }
