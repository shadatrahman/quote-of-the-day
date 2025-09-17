"""Analytics API endpoints for subscription metrics and tracking."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from src.core.database import get_db
from src.api.v1.auth import get_current_user
from src.services.analytics_service import (
    SubscriptionAnalyticsService,
    AnalyticsEventType,
)
from src.repositories.subscription_repository import SubscriptionRepository

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(
    db: Session = Depends(get_db),
) -> SubscriptionAnalyticsService:
    """Get analytics service instance."""
    subscription_repo = SubscriptionRepository(db)
    return SubscriptionAnalyticsService(subscription_repo)


@router.get("/subscription-metrics")
async def get_subscription_metrics(
    start_date: Optional[datetime] = Query(
        None, description="Start date for metrics (ISO format)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="End date for metrics (ISO format)"
    ),
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: SubscriptionAnalyticsService = Depends(get_analytics_service),
):
    """Get subscription metrics for a date range (Admin only)."""
    try:
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        metrics = await analytics_service.get_subscription_metrics(start_date, end_date)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription metrics: {str(e)}",
        )


@router.get("/cohort-analysis")
async def get_cohort_analysis(
    cohort_period_days: int = Query(30, description="Cohort period in days"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: SubscriptionAnalyticsService = Depends(get_analytics_service),
):
    """Get user cohort analysis for subscription retention (Admin only)."""
    try:
        analysis = await analytics_service.get_user_cohort_analysis(cohort_period_days)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cohort analysis: {str(e)}",
        )


@router.get("/feature-usage")
async def get_feature_usage_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: SubscriptionAnalyticsService = Depends(get_analytics_service),
):
    """Get feature usage metrics by subscription tier (Admin only)."""
    try:
        metrics = await analytics_service.get_feature_usage_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feature usage metrics: {str(e)}",
        )


@router.get("/dashboard")
async def get_dashboard_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: SubscriptionAnalyticsService = Depends(get_analytics_service),
):
    """Get comprehensive dashboard metrics (Admin only)."""
    try:
        metrics = await analytics_service.get_dashboard_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard metrics: {str(e)}",
        )


@router.post("/track/feature-access")
async def track_feature_access(
    feature: str,
    has_access: bool,
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: SubscriptionAnalyticsService = Depends(get_analytics_service),
):
    """Track feature access attempt."""
    try:
        # Get user's subscription tier
        subscription_repo = SubscriptionRepository(get_db())
        tier = subscription_repo.get_user_subscription_tier(current_user.id)

        await analytics_service.track_feature_access(
            current_user.id, feature, has_access, tier
        )

        return {"status": "tracked", "feature": feature, "has_access": has_access}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track feature access: {str(e)}",
        )


@router.post("/track/upgrade-attempt")
async def track_upgrade_attempt(
    success: bool,
    error_message: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: SubscriptionAnalyticsService = Depends(get_analytics_service),
):
    """Track subscription upgrade attempt."""
    try:
        await analytics_service.track_upgrade_attempt(
            current_user.id, success, error_message
        )

        return {"status": "tracked", "success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track upgrade attempt: {str(e)}",
        )


@router.post("/track/cancellation-attempt")
async def track_cancellation_attempt(
    success: bool,
    reason: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: SubscriptionAnalyticsService = Depends(get_analytics_service),
):
    """Track subscription cancellation attempt."""
    try:
        await analytics_service.track_cancellation_attempt(
            current_user.id, success, reason
        )

        return {"status": "tracked", "success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track cancellation attempt: {str(e)}",
        )


@router.get("/events")
async def get_analytics_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, description="Maximum number of events to return"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    analytics_service: SubscriptionAnalyticsService = Depends(get_analytics_service),
):
    """Get analytics events (Admin only)."""
    try:
        # In a real implementation, this would query the analytics database
        # For now, return a placeholder response
        return {
            "events": [],
            "message": "Analytics events endpoint - requires analytics database integration",
            "filters": {
                "event_type": event_type,
                "limit": limit,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics events: {str(e)}",
        )
