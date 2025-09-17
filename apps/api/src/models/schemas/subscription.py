"""Subscription Pydantic schemas for API validation and serialization."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from src.models.database.subscription import SubscriptionStatus, SubscriptionTier


class SubscriptionTierEnum(str, Enum):
    """Subscription tier enumeration for API."""

    FREE = "FREE"
    PREMIUM = "PREMIUM"


class SubscriptionStatusEnum(str, Enum):
    """Subscription status enumeration for API."""

    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    PAST_DUE = "PAST_DUE"
    INCOMPLETE = "INCOMPLETE"


class SubscriptionBase(BaseModel):
    """Base subscription schema with common fields."""

    tier: SubscriptionTierEnum = Field(..., description="Subscription tier")
    status: SubscriptionStatusEnum = Field(..., description="Subscription status")


class SubscriptionCreate(BaseModel):
    """Schema for subscription creation."""

    tier: SubscriptionTierEnum = Field(
        default=SubscriptionTierEnum.FREE, description="Subscription tier"
    )
    stripe_customer_id: Optional[str] = Field(
        None, description="Stripe customer ID for payment integration"
    )
    stripe_subscription_id: Optional[str] = Field(
        None, description="Stripe subscription ID for payment integration"
    )
    current_period_start: Optional[datetime] = Field(
        None, description="Billing period start date"
    )
    current_period_end: Optional[datetime] = Field(
        None, description="Billing period end date"
    )


class SubscriptionUpdate(BaseModel):
    """Schema for subscription updates."""

    status: Optional[SubscriptionStatusEnum] = Field(
        None, description="Subscription status"
    )
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")
    stripe_subscription_id: Optional[str] = Field(
        None, description="Stripe subscription ID"
    )
    current_period_start: Optional[datetime] = Field(
        None, description="Billing period start date"
    )
    current_period_end: Optional[datetime] = Field(
        None, description="Billing period end date"
    )
    cancelled_at: Optional[datetime] = Field(None, description="Cancellation timestamp")


class SubscriptionResponse(SubscriptionBase):
    """Schema for subscription API responses."""

    id: str = Field(..., description="Subscription unique identifier")
    user_id: str = Field(..., description="User unique identifier")
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")
    stripe_subscription_id: Optional[str] = Field(
        None, description="Stripe subscription ID"
    )
    current_period_start: Optional[datetime] = Field(
        None, description="Billing period start date"
    )
    current_period_end: Optional[datetime] = Field(
        None, description="Billing period end date"
    )
    cancelled_at: Optional[datetime] = Field(None, description="Cancellation timestamp")
    created_at: datetime = Field(..., description="Subscription creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class SubscriptionUpgradeRequest(BaseModel):
    """Schema for subscription upgrade request."""

    payment_method_id: str = Field(
        ..., min_length=1, description="Stripe payment method ID"
    )

    @field_validator("payment_method_id")
    @classmethod
    def validate_payment_method_id(cls, v):
        """Validate payment method ID format."""
        if not v or not v.strip():
            raise ValueError("payment_method_id cannot be empty")
        return v.strip()


class SubscriptionCancelRequest(BaseModel):
    """Schema for subscription cancellation request."""

    reason: Optional[str] = Field(
        None, max_length=500, description="Cancellation reason (optional)"
    )


class SubscriptionStatusResponse(BaseModel):
    """Schema for subscription status response."""

    subscription: Optional[SubscriptionResponse] = Field(
        None, description="Current subscription details"
    )
    is_premium: bool = Field(..., description="Whether user has premium access")
    features: dict = Field(..., description="Available features for current tier")

    model_config = {"from_attributes": True}


class StripeWebhookEvent(BaseModel):
    """Schema for Stripe webhook event processing."""

    id: str = Field(..., description="Stripe event ID")
    type: str = Field(..., description="Event type")
    data: dict = Field(..., description="Event data object")
    created: int = Field(..., description="Event creation timestamp")

    @field_validator("type")
    @classmethod
    def validate_event_type(cls, v):
        """Validate that we handle this event type."""
        supported_types = [
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "invoice.payment_succeeded",
            "invoice.payment_failed",
        ]
        if v not in supported_types:
            raise ValueError(f"Unsupported event type: {v}")
        return v
