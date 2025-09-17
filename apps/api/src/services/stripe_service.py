"""Stripe service for payment integration."""

import stripe
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for Stripe payment operations."""

    def __init__(self):
        """Initialize Stripe service."""
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self.premium_price_id = settings.STRIPE_PRICE_ID_PREMIUM

    async def create_customer(
        self, email: str, name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=email, name=name, metadata={"source": "quote_of_the_day"}
            )
            customer_id = (
                customer.get("id") if isinstance(customer, dict) else customer.id
            )
            logger.info(f"Created Stripe customer: {customer_id}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get Stripe customer by ID."""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except stripe.error.InvalidRequestError:
            logger.warning(f"Stripe customer not found: {customer_id}")
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get Stripe customer {customer_id}: {e}")
            raise

    async def update_customer(self, customer_id: str, **kwargs) -> Dict[str, Any]:
        """Update Stripe customer."""
        try:
            customer = stripe.Customer.modify(customer_id, **kwargs)
            logger.info(f"Updated Stripe customer: {customer_id}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update Stripe customer {customer_id}: {e}")
            raise

    async def delete_customer(self, customer_id: str) -> bool:
        """Delete Stripe customer."""
        try:
            stripe.Customer.delete(customer_id)
            logger.info(f"Deleted Stripe customer: {customer_id}")
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to delete Stripe customer {customer_id}: {e}")
            return False

    async def create_payment_method(
        self, customer_id: str, payment_method_id: str
    ) -> Dict[str, Any]:
        """Attach payment method to customer."""
        try:
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id, customer=customer_id
            )
            logger.info(
                f"Attached payment method {payment_method_id} to customer {customer_id}"
            )
            return payment_method
        except stripe.error.StripeError as e:
            logger.error(f"Failed to attach payment method: {e}")
            raise

    async def set_default_payment_method(
        self, customer_id: str, payment_method_id: str
    ) -> Dict[str, Any]:
        """Set default payment method for customer."""
        try:
            customer = stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method_id},
            )
            logger.info(f"Set default payment method for customer {customer_id}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to set default payment method: {e}")
            raise

    async def create_subscription(
        self, customer_id: str, price_id: str, payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a subscription for a customer."""
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"],
            }

            if payment_method_id:
                subscription_data["default_payment_method"] = payment_method_id

            subscription = stripe.Subscription.create(**subscription_data)
            subscription_id = (
                subscription.get("id")
                if isinstance(subscription, dict)
                else subscription.id
            )
            logger.info(f"Created Stripe subscription: {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe subscription: {e}")
            raise

    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get Stripe subscription by ID."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.InvalidRequestError:
            logger.warning(f"Stripe subscription not found: {subscription_id}")
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get Stripe subscription {subscription_id}: {e}")
            raise

    async def update_subscription(
        self, subscription_id: str, **kwargs
    ) -> Dict[str, Any]:
        """Update Stripe subscription."""
        try:
            subscription = stripe.Subscription.modify(subscription_id, **kwargs)
            logger.info(f"Updated Stripe subscription: {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update Stripe subscription {subscription_id}: {e}")
            raise

    async def cancel_subscription(
        self, subscription_id: str, immediately: bool = False
    ) -> Dict[str, Any]:
        """Cancel Stripe subscription."""
        try:
            if immediately:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id, cancel_at_period_end=True
                )
            logger.info(f"Cancelled Stripe subscription: {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel Stripe subscription {subscription_id}: {e}")
            raise

    async def reactivate_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Reactivate a cancelled subscription."""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=False
            )
            logger.info(f"Reactivated Stripe subscription: {subscription_id}")
            return subscription
        except stripe.error.StripeError as e:
            logger.error(
                f"Failed to reactivate Stripe subscription {subscription_id}: {e}"
            )
            raise

    async def get_customer_subscriptions(
        self, customer_id: str
    ) -> list[Dict[str, Any]]:
        """Get all subscriptions for a customer."""
        try:
            subscriptions = stripe.Subscription.list(customer=customer_id)
            return subscriptions.data
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get customer subscriptions {customer_id}: {e}")
            raise

    async def create_billing_portal_session(
        self, customer_id: str, return_url: str
    ) -> Dict[str, Any]:
        """Create billing portal session for customer self-service."""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            logger.info(f"Created billing portal session for customer {customer_id}")
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session: {e}")
            raise

    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a payment intent for one-time payments."""
        try:
            intent_data = {
                "amount": amount,
                "currency": currency,
                "automatic_payment_methods": {"enabled": True},
            }

            if customer_id:
                intent_data["customer"] = customer_id
            if payment_method_id:
                intent_data["payment_method"] = payment_method_id

            intent = stripe.PaymentIntent.create(**intent_data)
            intent_id = intent.get("id") if isinstance(intent, dict) else intent.id
            logger.info(f"Created payment intent: {intent_id}")
            return intent
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature."""
        try:
            stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return True
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            return False
        except Exception as e:
            logger.error(f"Webhook signature verification error: {e}")
            return False

    def parse_webhook_event(
        self, payload: bytes, signature: str
    ) -> Optional[Dict[str, Any]]:
        """Parse and verify Stripe webhook event."""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            logger.info(f"Received Stripe webhook: {event['type']}")
            return event
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            return None
        except Exception as e:
            logger.error(f"Webhook parsing error: {e}")
            return None

    def get_publishable_key(self) -> str:
        """Get Stripe publishable key for client-side integration."""
        return self.publishable_key
