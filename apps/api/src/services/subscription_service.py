"""Subscription service for business logic and feature access control."""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from src.models.database.subscription import (
    Subscription,
    SubscriptionStatus,
    SubscriptionTier,
)
from src.models.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionUpgradeRequest,
    SubscriptionCancelRequest,
    SubscriptionStatusResponse,
)
from src.repositories.subscription_repository import SubscriptionRepository
from src.services.stripe_service import StripeService
from src.services.analytics_service import (
    SubscriptionAnalyticsService,
    AnalyticsEventType,
)

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for subscription business logic and feature access control."""

    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        stripe_service: StripeService,
        analytics_service: Optional[SubscriptionAnalyticsService] = None,
    ):
        """Initialize subscription service."""
        self.subscription_repo = subscription_repo
        self.stripe_service = stripe_service
        self.analytics_service = analytics_service

    def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user's current subscription."""
        return self.subscription_repo.get_by_user_id(user_id)

    async def get_subscription_status(self, user_id: str) -> SubscriptionStatusResponse:
        """Get comprehensive subscription status for user."""
        subscription = self.get_user_subscription(user_id)

        if subscription and subscription.is_active:
            is_premium = subscription.is_premium
            features = self._get_features_for_tier(subscription.tier)
        else:
            is_premium = False
            features = self._get_features_for_tier(SubscriptionTier.FREE)

        return SubscriptionStatusResponse(
            subscription=subscription, is_premium=is_premium, features=features
        )

    async def create_free_subscription(self, user_id: str) -> Subscription:
        """Create a free subscription for new user."""
        subscription_data = SubscriptionCreate(tier=SubscriptionTier.FREE)
        subscription = self.subscription_repo.create(subscription_data, user_id)
        logger.info(f"Created free subscription for user {user_id}")

        # Track analytics event
        if self.analytics_service:
            await self.analytics_service.track_subscription_event(
                AnalyticsEventType.SUBSCRIPTION_CREATED, user_id, subscription.id
            )

        return subscription

    async def upgrade_to_premium(
        self, user_id: str, upgrade_request: SubscriptionUpgradeRequest
    ) -> Subscription:
        """Upgrade user to premium subscription."""
        # Check if user already has premium subscription
        existing_subscription = self.get_user_subscription(user_id)
        if (
            existing_subscription
            and existing_subscription.is_premium
            and existing_subscription.is_active
        ):
            raise ValueError("User already has an active premium subscription")

        # Create or get Stripe customer
        customer_id = await self._get_or_create_stripe_customer(user_id)

        # Attach payment method
        await self.stripe_service.create_payment_method(
            customer_id, upgrade_request.payment_method_id
        )
        await self.stripe_service.set_default_payment_method(
            customer_id, upgrade_request.payment_method_id
        )

        # Create Stripe subscription
        stripe_subscription = await self.stripe_service.create_subscription(
            customer_id,
            self.stripe_service.premium_price_id,
            upgrade_request.payment_method_id,
        )

        # Create or update local subscription
        if existing_subscription:
            # Update existing subscription
            update_data = SubscriptionUpdate(
                tier=SubscriptionTier.PREMIUM,
                status=SubscriptionStatus.ACTIVE,
                stripe_customer_id=customer_id,
                stripe_subscription_id=stripe_subscription["id"],
                current_period_start=datetime.fromtimestamp(
                    stripe_subscription["current_period_start"]
                ),
                current_period_end=datetime.fromtimestamp(
                    stripe_subscription["current_period_end"]
                ),
                cancelled_at=None,
            )
            subscription = self.subscription_repo.update(
                existing_subscription, update_data
            )
        else:
            # Create new subscription
            subscription_data = SubscriptionCreate(
                tier=SubscriptionTier.PREMIUM,
                stripe_customer_id=customer_id,
                stripe_subscription_id=stripe_subscription["id"],
                current_period_start=datetime.fromtimestamp(
                    stripe_subscription["current_period_start"]
                ),
                current_period_end=datetime.fromtimestamp(
                    stripe_subscription["current_period_end"]
                ),
            )
            subscription = self.subscription_repo.create(subscription_data, user_id)

        logger.info(f"Upgraded user {user_id} to premium subscription")

        # Track analytics event
        if self.analytics_service:
            await self.analytics_service.track_subscription_event(
                AnalyticsEventType.SUBSCRIPTION_UPGRADED, user_id, subscription.id
            )

        return subscription

    async def cancel_subscription(
        self, user_id: str, cancel_request: SubscriptionCancelRequest
    ) -> Subscription:
        """Cancel user's premium subscription."""
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            raise ValueError("No subscription found for user")

        if not subscription.is_premium:
            raise ValueError("User does not have a premium subscription to cancel")

        if subscription.stripe_subscription_id:
            # Cancel Stripe subscription
            await self.stripe_service.cancel_subscription(
                subscription.stripe_subscription_id,
                immediately=False,  # Cancel at period end
            )

        # Update local subscription
        subscription = self.subscription_repo.cancel(subscription)
        logger.info(f"Cancelled subscription for user {user_id}")

        # Track analytics event
        if self.analytics_service:
            await self.analytics_service.track_subscription_event(
                AnalyticsEventType.SUBSCRIPTION_CANCELLED,
                user_id,
                subscription.id,
                {"reason": cancel_request.reason},
            )

        return subscription

    async def handle_stripe_webhook(self, event_data: Dict[str, Any]) -> bool:
        """Handle Stripe webhook events for subscription updates."""
        event_type = event_data.get("type")

        try:
            if event_type == "customer.subscription.created":
                await self._handle_subscription_created(event_data)
            elif event_type == "customer.subscription.updated":
                await self._handle_subscription_updated(event_data)
            elif event_type == "customer.subscription.deleted":
                await self._handle_subscription_deleted(event_data)
            elif event_type == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(event_data)
            elif event_type == "invoice.payment_failed":
                await self._handle_payment_failed(event_data)
            else:
                logger.warning(f"Unhandled webhook event type: {event_type}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error handling webhook event {event_type}: {e}")
            return False

    async def check_feature_access(self, user_id: str, feature: str) -> bool:
        """Check if user has access to a specific feature."""
        subscription = self.get_user_subscription(user_id)
        if not subscription or not subscription.is_active:
            has_access = False
        else:
            features = self._get_features_for_tier(subscription.tier)
            has_access = feature in features

        # Track feature access for analytics
        if self.analytics_service:
            await self.analytics_service.track_feature_access(
                user_id,
                feature,
                has_access,
                subscription.tier if subscription else SubscriptionTier.FREE,
            )

        return has_access

    async def get_available_features(self, user_id: str) -> Dict[str, Any]:
        """Get available features for user's subscription tier."""
        subscription = self.get_user_subscription(user_id)
        if not subscription or not subscription.is_active:
            return self._get_features_for_tier(SubscriptionTier.FREE)

        return self._get_features_for_tier(subscription.tier)

    def _get_features_for_tier(self, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get features available for subscription tier."""
        if tier == SubscriptionTier.PREMIUM:
            return {
                "daily_quotes": True,
                "basic_notifications": True,
                "quote_starring": True,
                "unlimited_starred_quotes": True,
                "quote_search": True,
                "advanced_notifications": True,
                "quote_history": True,
                "priority_support": True,
                "export_quotes": True,
                "custom_quote_categories": True,
            }
        else:  # FREE tier
            return {
                "daily_quotes": True,
                "basic_notifications": True,
                "quote_starring": True,
                "unlimited_starred_quotes": False,
                "quote_search": False,
                "advanced_notifications": False,
                "quote_history": False,
                "priority_support": False,
                "export_quotes": False,
                "custom_quote_categories": False,
            }

    async def _get_or_create_stripe_customer(self, user_id: str) -> str:
        """Get or create Stripe customer for user."""
        # This would typically involve getting user email from user service
        # For now, we'll assume we have access to user data
        # In a real implementation, you'd inject a user service
        user_email = f"user_{user_id}@example.com"  # Placeholder

        # Try to find existing customer
        # In practice, you'd store the customer_id in the user record
        # For now, create a new customer
        customer = await self.stripe_service.create_customer(user_email)
        return customer["id"]

    async def _handle_subscription_created(self, event_data: Dict[str, Any]) -> None:
        """Handle subscription created webhook."""
        subscription_data = event_data["data"]["object"]
        stripe_subscription_id = subscription_data["id"]
        customer_id = subscription_data["customer"]

        # Find local subscription by Stripe subscription ID
        subscription = self.subscription_repo.get_by_stripe_subscription_id(
            stripe_subscription_id
        )
        if subscription:
            # Update subscription status
            self.subscription_repo.update_status(
                subscription, SubscriptionStatus.ACTIVE
            )
            logger.info(f"Activated subscription {subscription.id} from webhook")

    async def _handle_subscription_updated(self, event_data: Dict[str, Any]) -> None:
        """Handle subscription updated webhook."""
        subscription_data = event_data["data"]["object"]
        stripe_subscription_id = subscription_data["id"]

        subscription = self.subscription_repo.get_by_stripe_subscription_id(
            stripe_subscription_id
        )
        if subscription:
            # Update subscription details
            status = self._map_stripe_status_to_local(subscription_data["status"])
            update_data = SubscriptionUpdate(
                status=status,
                current_period_start=datetime.fromtimestamp(
                    subscription_data["current_period_start"]
                ),
                current_period_end=datetime.fromtimestamp(
                    subscription_data["current_period_end"]
                ),
            )
            self.subscription_repo.update(subscription, update_data)
            logger.info(f"Updated subscription {subscription.id} from webhook")

    async def _handle_subscription_deleted(self, event_data: Dict[str, Any]) -> None:
        """Handle subscription deleted webhook."""
        subscription_data = event_data["data"]["object"]
        stripe_subscription_id = subscription_data["id"]

        subscription = self.subscription_repo.get_by_stripe_subscription_id(
            stripe_subscription_id
        )
        if subscription:
            self.subscription_repo.cancel(subscription)
            logger.info(f"Cancelled subscription {subscription.id} from webhook")

    async def _handle_payment_succeeded(self, event_data: Dict[str, Any]) -> None:
        """Handle successful payment webhook."""
        invoice_data = event_data["data"]["object"]
        subscription_id = invoice_data.get("subscription")

        if subscription_id:
            subscription = self.subscription_repo.get_by_stripe_subscription_id(
                subscription_id
            )
            if subscription:
                self.subscription_repo.activate(subscription)
                logger.info(f"Payment succeeded for subscription {subscription.id}")

    async def _handle_payment_failed(self, event_data: Dict[str, Any]) -> None:
        """Handle failed payment webhook."""
        invoice_data = event_data["data"]["object"]
        subscription_id = invoice_data.get("subscription")

        if subscription_id:
            subscription = self.subscription_repo.get_by_stripe_subscription_id(
                subscription_id
            )
            if subscription:
                self.subscription_repo.update_status(
                    subscription, SubscriptionStatus.PAST_DUE
                )
                logger.warning(f"Payment failed for subscription {subscription.id}")

    def _map_stripe_status_to_local(self, stripe_status: str) -> SubscriptionStatus:
        """Map Stripe subscription status to local status."""
        status_mapping = {
            "active": SubscriptionStatus.ACTIVE,
            "canceled": SubscriptionStatus.CANCELLED,
            "past_due": SubscriptionStatus.PAST_DUE,
            "incomplete": SubscriptionStatus.INCOMPLETE,
        }
        return status_mapping.get(stripe_status, SubscriptionStatus.INCOMPLETE)
