"""Analytics service for tracking subscription metrics and events."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from src.core.database import get_db
from src.repositories.subscription_repository import SubscriptionRepository
from src.models.database.subscription import SubscriptionStatus, SubscriptionTier

logger = logging.getLogger(__name__)


class AnalyticsEventType(str, Enum):
    """Analytics event types for subscription tracking."""

    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPGRADED = "subscription_upgraded"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    FEATURE_ACCESSED = "feature_accessed"
    UPGRADE_ATTEMPTED = "upgrade_attempted"
    CANCELLATION_ATTEMPTED = "cancellation_attempted"


class SubscriptionAnalyticsService:
    """Service for subscription analytics and metrics tracking."""

    def __init__(self, subscription_repo: SubscriptionRepository):
        """Initialize analytics service."""
        self.subscription_repo = subscription_repo

    async def track_subscription_event(
        self,
        event_type: AnalyticsEventType,
        user_id: str,
        subscription_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a subscription-related event."""
        try:
            event_data = {
                "event_type": event_type.value,
                "user_id": user_id,
                "subscription_id": subscription_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }

            # In a real implementation, this would send to analytics service
            # For now, we'll just log the event
            logger.info(f"Analytics event: {event_data}")

            # TODO: Integrate with actual analytics service (e.g., Mixpanel, Amplitude, etc.)
            # await self._send_to_analytics_service(event_data)

        except Exception as e:
            logger.error(f"Failed to track analytics event {event_type}: {e}")

    async def get_subscription_metrics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get subscription metrics for a date range."""
        try:
            # Get all subscriptions in date range
            all_subscriptions = self.subscription_repo.get_active_subscriptions()

            # Filter by date range
            filtered_subscriptions = [
                sub
                for sub in all_subscriptions
                if start_date <= sub.created_at <= end_date
            ]

            # Calculate metrics
            total_subscriptions = len(filtered_subscriptions)
            premium_subscriptions = len(
                [
                    sub
                    for sub in filtered_subscriptions
                    if sub.tier == SubscriptionTier.PREMIUM
                ]
            )
            free_subscriptions = total_subscriptions - premium_subscriptions

            # Calculate conversion rate
            conversion_rate = (
                premium_subscriptions / total_subscriptions * 100
                if total_subscriptions > 0
                else 0
            )

            # Calculate churn rate (cancelled subscriptions)
            cancelled_subscriptions = (
                self.subscription_repo.get_subscriptions_by_status(
                    SubscriptionStatus.CANCELLED
                )
            )
            churn_rate = (
                len(cancelled_subscriptions) / total_subscriptions * 100
                if total_subscriptions > 0
                else 0
            )

            # Calculate MRR (Monthly Recurring Revenue)
            mrr = premium_subscriptions * 1.0  # $1 per month per premium subscription

            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "subscriptions": {
                    "total": total_subscriptions,
                    "premium": premium_subscriptions,
                    "free": free_subscriptions,
                },
                "metrics": {
                    "conversion_rate": round(conversion_rate, 2),
                    "churn_rate": round(churn_rate, 2),
                    "mrr": mrr,
                },
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get subscription metrics: {e}")
            return {}

    async def get_user_cohort_analysis(
        self, cohort_period_days: int = 30
    ) -> Dict[str, Any]:
        """Get user cohort analysis for subscription retention."""
        try:
            # Get all subscriptions grouped by creation month
            all_subscriptions = self.subscription_repo.get_active_subscriptions()

            # Group by creation month
            cohorts = {}
            for subscription in all_subscriptions:
                cohort_key = subscription.created_at.strftime("%Y-%m")
                if cohort_key not in cohorts:
                    cohorts[cohort_key] = []
                cohorts[cohort_key].append(subscription)

            # Calculate retention for each cohort
            cohort_analysis = {}
            for cohort_key, subscriptions in cohorts.items():
                total_users = len(subscriptions)
                active_users = len(
                    [
                        sub
                        for sub in subscriptions
                        if sub.status == SubscriptionStatus.ACTIVE
                    ]
                )

                retention_rate = (
                    active_users / total_users * 100 if total_users > 0 else 0
                )

                cohort_analysis[cohort_key] = {
                    "total_users": total_users,
                    "active_users": active_users,
                    "retention_rate": round(retention_rate, 2),
                }

            return {
                "cohort_analysis": cohort_analysis,
                "cohort_period_days": cohort_period_days,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get cohort analysis: {e}")
            return {}

    async def get_feature_usage_metrics(self) -> Dict[str, Any]:
        """Get feature usage metrics for subscription tiers."""
        try:
            # This would typically come from feature usage tracking
            # For now, we'll return mock data
            return {
                "feature_usage": {
                    "daily_quotes": {
                        "free_users": 85.2,
                        "premium_users": 92.1,
                    },
                    "quote_search": {
                        "free_users": 0.0,  # Not available for free users
                        "premium_users": 67.8,
                    },
                    "quote_starring": {
                        "free_users": 45.3,
                        "premium_users": 78.9,
                    },
                    "advanced_notifications": {
                        "free_users": 0.0,  # Not available for free users
                        "premium_users": 34.2,
                    },
                },
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get feature usage metrics: {e}")
            return {}

    async def track_feature_access(
        self,
        user_id: str,
        feature: str,
        has_access: bool,
        subscription_tier: SubscriptionTier,
    ) -> None:
        """Track feature access attempts."""
        await self.track_subscription_event(
            AnalyticsEventType.FEATURE_ACCESSED,
            user_id,
            metadata={
                "feature": feature,
                "has_access": has_access,
                "subscription_tier": subscription_tier.value,
            },
        )

    async def track_upgrade_attempt(
        self, user_id: str, success: bool, error_message: Optional[str] = None
    ) -> None:
        """Track subscription upgrade attempts."""
        await self.track_subscription_event(
            AnalyticsEventType.UPGRADE_ATTEMPTED,
            user_id,
            metadata={
                "success": success,
                "error_message": error_message,
            },
        )

    async def track_cancellation_attempt(
        self, user_id: str, success: bool, reason: Optional[str] = None
    ) -> None:
        """Track subscription cancellation attempts."""
        await self.track_subscription_event(
            AnalyticsEventType.CANCELLATION_ATTEMPTED,
            user_id,
            metadata={
                "success": success,
                "reason": reason,
            },
        )

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get key metrics for analytics dashboard."""
        try:
            # Get metrics for last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)

            metrics = await self.get_subscription_metrics(start_date, end_date)
            cohort_analysis = await self.get_user_cohort_analysis()
            feature_usage = await self.get_feature_usage_metrics()

            return {
                "subscription_metrics": metrics,
                "cohort_analysis": cohort_analysis,
                "feature_usage": feature_usage,
                "dashboard_generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {e}")
            return {}
