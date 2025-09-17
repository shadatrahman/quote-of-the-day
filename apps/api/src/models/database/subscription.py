"""Subscription database model and related models."""

from typing import Optional
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum

from src.models.base import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enumeration."""

    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    PAST_DUE = "PAST_DUE"
    INCOMPLETE = "INCOMPLETE"


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enumeration."""

    FREE = "FREE"
    PREMIUM = "PREMIUM"


class Subscription(Base):
    """Subscription model for managing user subscriptions."""

    __tablename__ = "subscriptions"

    # Foreign key to User
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Subscription details
    tier: Mapped[SubscriptionTier] = mapped_column(
        SQLEnum(SubscriptionTier), nullable=False, index=True
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus), nullable=False, index=True
    )

    # Stripe integration fields
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )

    # Billing period tracking
    current_period_start: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Cancellation tracking
    cancelled_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscription")

    def __repr__(self) -> str:
        """String representation of the Subscription model."""
        return (
            f"<Subscription(id={self.id}, user_id={self.user_id}, "
            f"tier={self.tier.value}, status={self.status.value})>"
        )

    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status == SubscriptionStatus.ACTIVE

    @property
    def is_premium(self) -> bool:
        """Check if subscription is premium tier."""
        return self.tier == SubscriptionTier.PREMIUM

    def to_dict(self) -> dict:
        """Convert subscription to dictionary for API responses."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "tier": self.tier.value,
            "status": self.status.value,
            "stripe_customer_id": self.stripe_customer_id,
            "stripe_subscription_id": self.stripe_subscription_id,
            "current_period_start": (
                self.current_period_start.isoformat()
                if self.current_period_start
                else None
            ),
            "current_period_end": (
                self.current_period_end.isoformat() if self.current_period_end else None
            ),
            "cancelled_at": (
                self.cancelled_at.isoformat() if self.cancelled_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Create indexes for better query performance
Index("idx_subscriptions_user_tier", Subscription.user_id, Subscription.tier)
Index("idx_subscriptions_status_tier", Subscription.status, Subscription.tier)
Index("idx_subscriptions_stripe_customer", Subscription.stripe_customer_id)
Index("idx_subscriptions_stripe_subscription", Subscription.stripe_subscription_id)
