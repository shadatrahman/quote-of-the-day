"""Subscription API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.core.database import get_db
from src.api.v1.auth import get_current_user
from src.models.schemas.subscription import (
    SubscriptionResponse,
    SubscriptionUpgradeRequest,
    SubscriptionCancelRequest,
    SubscriptionStatusResponse,
)
from src.services.subscription_service import SubscriptionService
from src.repositories.subscription_repository import SubscriptionRepository
from src.services.stripe_service import StripeService

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/subscription", tags=["subscription"])


def get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    """Get subscription service instance."""
    subscription_repo = SubscriptionRepository(db)
    stripe_service = StripeService()
    return SubscriptionService(subscription_repo, stripe_service)


@router.get("/", response_model=SubscriptionStatusResponse)
@limiter.limit("30/minute")
async def get_subscription_status(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """Get current user's subscription status and available features."""
    try:
        status_response = await subscription_service.get_subscription_status(
            current_user["user_id"]
        )
        return status_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription status: {str(e)}",
        )


@router.post("/upgrade", response_model=SubscriptionResponse)
@limiter.limit("5/minute")
async def upgrade_subscription(
    request: Request,
    upgrade_request: SubscriptionUpgradeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """Upgrade user to premium subscription."""
    try:
        # Check if user already has premium
        current_subscription = subscription_service.get_user_subscription(
            current_user["user_id"]
        )
        if (
            current_subscription
            and current_subscription.is_premium
            and current_subscription.is_active
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active premium subscription",
            )

        subscription = await subscription_service.upgrade_to_premium(
            current_user["user_id"], upgrade_request
        )
        return subscription
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade subscription: {str(e)}",
        )


@router.post("/cancel", response_model=Dict[str, str])
@limiter.limit("3/minute")
async def cancel_subscription(
    request: Request,
    cancel_request: SubscriptionCancelRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """Cancel user's premium subscription."""
    try:
        subscription = await subscription_service.cancel_subscription(
            current_user["user_id"], cancel_request
        )
        return {
            "message": "Subscription cancelled successfully",
            "cancelled_at": (
                subscription.cancelled_at.isoformat()
                if subscription.cancelled_at
                else None
            ),
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}",
        )


@router.get("/features", response_model=Dict[str, Any])
@limiter.limit("60/minute")
async def get_available_features(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """Get available features for current user's subscription tier."""
    try:
        features = await subscription_service.get_available_features(
            current_user["user_id"]
        )
        return features
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available features: {str(e)}",
        )


@router.get("/check/{feature}")
@limiter.limit("100/minute")
async def check_feature_access(
    request: Request,
    feature: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """Check if user has access to a specific feature."""
    try:
        has_access = await subscription_service.check_feature_access(
            current_user["user_id"], feature
        )
        return {
            "feature": feature,
            "has_access": has_access,
            "user_id": current_user["user_id"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check feature access: {str(e)}",
        )
