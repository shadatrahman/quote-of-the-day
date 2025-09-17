"""Stripe configuration and webhook handling."""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from src.core.config import settings
from src.services.stripe_service import StripeService
from src.services.subscription_service import SubscriptionService
from src.repositories.subscription_repository import SubscriptionRepository
from src.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def get_stripe_service() -> StripeService:
    """Get Stripe service instance."""
    return StripeService()


def get_subscription_service(db=Depends(get_db)) -> SubscriptionService:
    """Get subscription service instance."""
    subscription_repo = SubscriptionRepository(db)
    stripe_service = StripeService()
    return SubscriptionService(subscription_repo, stripe_service)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        logger.warning("Missing Stripe signature header")
        raise HTTPException(status_code=400, detail="Missing signature header")

    # Verify webhook signature
    stripe_service = StripeService()
    event = stripe_service.parse_webhook_event(payload, signature)

    if not event:
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    success = await subscription_service.handle_stripe_webhook(event)

    if success:
        return JSONResponse(content={"status": "success"})
    else:
        logger.error(f"Failed to handle webhook event: {event['type']}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


@router.get("/stripe/config")
async def get_stripe_config(
    stripe_service: StripeService = Depends(get_stripe_service),
):
    """Get Stripe configuration for client-side integration."""
    return {
        "publishable_key": stripe_service.get_publishable_key(),
        "premium_price_id": settings.STRIPE_PRICE_ID_PREMIUM,
    }
