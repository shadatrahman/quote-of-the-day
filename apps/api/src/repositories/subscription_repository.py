"""Subscription repository for data access operations."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from src.models.database.subscription import (
    Subscription,
    SubscriptionStatus,
    SubscriptionTier,
)
from src.models.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class SubscriptionRepository:
    """Repository for subscription data access operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(
        self, subscription_data: SubscriptionCreate, user_id: str
    ) -> Subscription:
        """Create a new subscription."""
        subscription = Subscription(
            user_id=user_id,
            tier=subscription_data.tier,
            status=SubscriptionStatus.ACTIVE,
            stripe_customer_id=subscription_data.stripe_customer_id,
            stripe_subscription_id=subscription_data.stripe_subscription_id,
            current_period_start=subscription_data.current_period_start,
            current_period_end=subscription_data.current_period_end,
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def get_by_id(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.db.get(Subscription, subscription_id)

    def get_by_user_id(self, user_id: str) -> Optional[Subscription]:
        """Get subscription by user ID."""
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_stripe_customer_id(
        self, stripe_customer_id: str
    ) -> Optional[Subscription]:
        """Get subscription by Stripe customer ID."""
        stmt = select(Subscription).where(
            Subscription.stripe_customer_id == stripe_customer_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_stripe_subscription_id(
        self, stripe_subscription_id: str
    ) -> Optional[Subscription]:
        """Get subscription by Stripe subscription ID."""
        stmt = select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def update(
        self, subscription: Subscription, update_data: SubscriptionUpdate
    ) -> Subscription:
        """Update subscription with new data."""
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(subscription, field, value)

        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def update_status(
        self, subscription: Subscription, status: SubscriptionStatus
    ) -> Subscription:
        """Update subscription status."""
        subscription.status = status
        if status == SubscriptionStatus.CANCELLED:
            from datetime import datetime

            subscription.cancelled_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def cancel(self, subscription: Subscription) -> Subscription:
        """Cancel subscription."""
        return self.update_status(subscription, SubscriptionStatus.CANCELLED)

    def activate(self, subscription: Subscription) -> Subscription:
        """Activate subscription."""
        return self.update_status(subscription, SubscriptionStatus.ACTIVE)

    def delete(self, subscription: Subscription) -> None:
        """Delete subscription."""
        self.db.delete(subscription)
        self.db.commit()

    def get_active_subscriptions(self) -> List[Subscription]:
        """Get all active subscriptions."""
        stmt = select(Subscription).where(
            Subscription.status == SubscriptionStatus.ACTIVE
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_premium_subscriptions(self) -> List[Subscription]:
        """Get all premium subscriptions."""
        stmt = select(Subscription).where(
            and_(
                Subscription.tier == SubscriptionTier.PREMIUM,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_subscriptions_by_status(
        self, status: SubscriptionStatus
    ) -> List[Subscription]:
        """Get subscriptions by status."""
        stmt = select(Subscription).where(Subscription.status == status)
        return list(self.db.execute(stmt).scalars().all())

    def get_user_subscription_tier(self, user_id: str) -> SubscriptionTier:
        """Get user's subscription tier."""
        subscription = self.get_by_user_id(user_id)
        if subscription and subscription.is_active:
            return subscription.tier
        return SubscriptionTier.FREE

    def has_active_subscription(self, user_id: str) -> bool:
        """Check if user has active subscription."""
        subscription = self.get_by_user_id(user_id)
        return subscription is not None and subscription.is_active

    def is_premium_user(self, user_id: str) -> bool:
        """Check if user has premium subscription."""
        subscription = self.get_by_user_id(user_id)
        return (
            subscription is not None
            and subscription.is_premium
            and subscription.is_active
        )
