"""Unit tests for subscription service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from src.services.subscription_service import SubscriptionService
from src.models.database.subscription import (
    Subscription,
    SubscriptionStatus,
    SubscriptionTier,
)
from src.models.schemas.subscription import (
    SubscriptionUpgradeRequest,
    SubscriptionCancelRequest,
    SubscriptionStatusResponse,
)
from src.services.analytics_service import AnalyticsEventType


@pytest.fixture
def mock_subscription_repo():
    """Mock subscription repository."""
    return Mock()


@pytest.fixture
def mock_stripe_service():
    """Mock Stripe service."""
    return Mock()


@pytest.fixture
def mock_analytics_service():
    """Mock analytics service."""
    return Mock()


@pytest.fixture
def subscription_service(
    mock_subscription_repo, mock_stripe_service, mock_analytics_service
):
    """Create subscription service with mocked dependencies."""
    return SubscriptionService(
        mock_subscription_repo, mock_stripe_service, mock_analytics_service
    )


@pytest.fixture
def sample_subscription():
    """Sample subscription for testing."""
    now = datetime.utcnow()
    return Subscription(
        id="test-subscription-id",
        user_id="test-user-id",
        tier=SubscriptionTier.PREMIUM,
        status=SubscriptionStatus.ACTIVE,
        stripe_customer_id="cus_test123",
        stripe_subscription_id="sub_test123",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        created_at=now,
        updated_at=now,
        cancelled_at=None,
    )


class TestSubscriptionService:
    """Test cases for SubscriptionService."""

    def test_get_user_subscription(
        self, subscription_service, mock_subscription_repo, sample_subscription
    ):
        """Test getting user subscription."""
        # Arrange
        user_id = "test-user-id"
        mock_subscription_repo.get_by_user_id.return_value = sample_subscription

        # Act
        result = subscription_service.get_user_subscription(user_id)

        # Assert
        assert result == sample_subscription
        mock_subscription_repo.get_by_user_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_subscription_status_premium(
        self, subscription_service, mock_subscription_repo, sample_subscription
    ):
        """Test getting subscription status for premium user."""
        # Arrange
        user_id = "test-user-id"
        mock_subscription_repo.get_by_user_id.return_value = sample_subscription

        # Act
        result = await subscription_service.get_subscription_status(user_id)

        # Assert
        assert isinstance(result, SubscriptionStatusResponse)
        assert result.subscription is not None
        assert result.subscription.id == sample_subscription.id
        assert result.subscription.user_id == sample_subscription.user_id
        assert result.subscription.tier == sample_subscription.tier
        assert result.subscription.status == sample_subscription.status
        assert result.is_premium is True
        assert result.features["quote_search"] is True
        assert result.features["unlimited_starred_quotes"] is True

    @pytest.mark.asyncio
    async def test_get_subscription_status_free(
        self, subscription_service, mock_subscription_repo
    ):
        """Test getting subscription status for free user."""
        # Arrange
        user_id = "test-user-id"
        mock_subscription_repo.get_by_user_id.return_value = None

        # Act
        result = await subscription_service.get_subscription_status(user_id)

        # Assert
        assert isinstance(result, SubscriptionStatusResponse)
        assert result.subscription is None
        assert result.is_premium is False
        assert result.features["quote_search"] is False
        assert result.features["unlimited_starred_quotes"] is False

    @pytest.mark.asyncio
    async def test_create_free_subscription(
        self, subscription_service, mock_subscription_repo, mock_analytics_service
    ):
        """Test creating free subscription."""
        # Arrange
        user_id = "test-user-id"
        mock_subscription_repo.create.return_value = Mock(id="new-subscription-id")
        mock_analytics_service.track_subscription_event = AsyncMock()

        # Act
        result = await subscription_service.create_free_subscription(user_id)

        # Assert
        assert result is not None
        mock_subscription_repo.create.assert_called_once()
        mock_analytics_service.track_subscription_event.assert_called_once_with(
            AnalyticsEventType.SUBSCRIPTION_CREATED, user_id, "new-subscription-id"
        )

    @pytest.mark.asyncio
    async def test_upgrade_to_premium_success(
        self,
        subscription_service,
        mock_subscription_repo,
        mock_stripe_service,
        mock_analytics_service,
    ):
        """Test successful premium upgrade."""
        # Arrange
        user_id = "test-user-id"
        upgrade_request = SubscriptionUpgradeRequest(payment_method_id="pm_test123")

        mock_subscription_repo.get_by_user_id.return_value = (
            None  # No existing subscription
        )
        mock_stripe_service.create_customer = AsyncMock(
            return_value={"id": "cus_test123"}
        )
        mock_stripe_service.create_payment_method = AsyncMock()
        mock_stripe_service.set_default_payment_method = AsyncMock()
        mock_stripe_service.create_subscription = AsyncMock(
            return_value={
                "id": "sub_test123",
                "current_period_start": 1640995200,
                "current_period_end": 1643673600,
            }
        )
        mock_subscription_repo.create.return_value = Mock(id="new-subscription-id")
        mock_analytics_service.track_subscription_event = AsyncMock()

        # Act
        result = await subscription_service.upgrade_to_premium(user_id, upgrade_request)

        # Assert
        assert result is not None
        mock_stripe_service.create_customer.assert_called_once()
        mock_stripe_service.create_payment_method.assert_called_once()
        mock_stripe_service.set_default_payment_method.assert_called_once()
        mock_stripe_service.create_subscription.assert_called_once()
        mock_subscription_repo.create.assert_called_once()
        mock_analytics_service.track_subscription_event.assert_called_once_with(
            AnalyticsEventType.SUBSCRIPTION_UPGRADED, user_id, "new-subscription-id"
        )

    @pytest.mark.asyncio
    async def test_upgrade_to_premium_already_premium(
        self, subscription_service, mock_subscription_repo, sample_subscription
    ):
        """Test upgrade attempt when user already has premium."""
        # Arrange
        user_id = "test-user-id"
        upgrade_request = SubscriptionUpgradeRequest(payment_method_id="pm_test123")
        mock_subscription_repo.get_by_user_id.return_value = sample_subscription

        # Act & Assert
        with pytest.raises(
            ValueError, match="User already has an active premium subscription"
        ):
            await subscription_service.upgrade_to_premium(user_id, upgrade_request)

    @pytest.mark.asyncio
    async def test_cancel_subscription_success(
        self,
        subscription_service,
        mock_subscription_repo,
        mock_stripe_service,
        mock_analytics_service,
        sample_subscription,
    ):
        """Test successful subscription cancellation."""
        # Arrange
        user_id = "test-user-id"
        cancel_request = SubscriptionCancelRequest(reason="No longer needed")

        mock_subscription_repo.get_by_user_id.return_value = sample_subscription
        mock_stripe_service.cancel_subscription = AsyncMock()
        mock_subscription_repo.cancel.return_value = sample_subscription
        mock_analytics_service.track_subscription_event = AsyncMock()

        # Act
        result = await subscription_service.cancel_subscription(user_id, cancel_request)

        # Assert
        assert result == sample_subscription
        mock_stripe_service.cancel_subscription.assert_called_once_with(
            "sub_test123", immediately=False
        )
        mock_subscription_repo.cancel.assert_called_once_with(sample_subscription)
        mock_analytics_service.track_subscription_event.assert_called_once_with(
            AnalyticsEventType.SUBSCRIPTION_CANCELLED,
            user_id,
            sample_subscription.id,
            {"reason": "No longer needed"},
        )

    @pytest.mark.asyncio
    async def test_cancel_subscription_no_subscription(
        self, subscription_service, mock_subscription_repo
    ):
        """Test cancellation attempt when user has no subscription."""
        # Arrange
        user_id = "test-user-id"
        cancel_request = SubscriptionCancelRequest()
        mock_subscription_repo.get_by_user_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="No subscription found for user"):
            await subscription_service.cancel_subscription(user_id, cancel_request)

    @pytest.mark.asyncio
    async def test_cancel_subscription_not_premium(
        self, subscription_service, mock_subscription_repo
    ):
        """Test cancellation attempt when user doesn't have premium."""
        # Arrange
        user_id = "test-user-id"
        cancel_request = SubscriptionCancelRequest()
        free_subscription = Mock()
        free_subscription.is_premium = False
        mock_subscription_repo.get_by_user_id.return_value = free_subscription

        # Act & Assert
        with pytest.raises(
            ValueError, match="User does not have a premium subscription to cancel"
        ):
            await subscription_service.cancel_subscription(user_id, cancel_request)

    @pytest.mark.asyncio
    async def test_check_feature_access_premium(
        self,
        subscription_service,
        mock_subscription_repo,
        mock_analytics_service,
        sample_subscription,
    ):
        """Test feature access check for premium user."""
        # Arrange
        user_id = "test-user-id"
        feature = "quote_search"
        mock_subscription_repo.get_by_user_id.return_value = sample_subscription
        mock_analytics_service.track_feature_access = AsyncMock()

        # Act
        result = await subscription_service.check_feature_access(user_id, feature)

        # Assert
        assert result is True
        mock_analytics_service.track_feature_access.assert_called_once_with(
            user_id, feature, True, SubscriptionTier.PREMIUM
        )

    @pytest.mark.asyncio
    async def test_check_feature_access_free(
        self, subscription_service, mock_subscription_repo, mock_analytics_service
    ):
        """Test feature access check for free user."""
        # Arrange
        user_id = "test-user-id"
        feature = "quote_search"
        mock_subscription_repo.get_by_user_id.return_value = None
        mock_analytics_service.track_feature_access = AsyncMock()

        # Act
        result = await subscription_service.check_feature_access(user_id, feature)

        # Assert
        assert result is False
        mock_analytics_service.track_feature_access.assert_called_once_with(
            user_id, feature, False, SubscriptionTier.FREE
        )

    @pytest.mark.asyncio
    async def test_get_available_features_premium(
        self, subscription_service, mock_subscription_repo, sample_subscription
    ):
        """Test getting available features for premium user."""
        # Arrange
        user_id = "test-user-id"
        mock_subscription_repo.get_by_user_id.return_value = sample_subscription

        # Act
        result = await subscription_service.get_available_features(user_id)

        # Assert
        assert result["quote_search"] is True
        assert result["unlimited_starred_quotes"] is True
        assert result["priority_support"] is True

    @pytest.mark.asyncio
    async def test_get_available_features_free(
        self, subscription_service, mock_subscription_repo
    ):
        """Test getting available features for free user."""
        # Arrange
        user_id = "test-user-id"
        mock_subscription_repo.get_by_user_id.return_value = None

        # Act
        result = await subscription_service.get_available_features(user_id)

        # Assert
        assert result["quote_search"] is False
        assert result["unlimited_starred_quotes"] is False
        assert result["priority_support"] is False
        assert result["daily_quotes"] is True  # Free feature

    @pytest.mark.asyncio
    async def test_handle_stripe_webhook_subscription_created(
        self, subscription_service, mock_subscription_repo
    ):
        """Test handling Stripe webhook for subscription created."""
        # Arrange
        event_data = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                }
            },
        }
        mock_subscription = Mock()
        mock_subscription_repo.get_by_stripe_subscription_id.return_value = (
            mock_subscription
        )
        mock_subscription_repo.update_status = Mock()

        # Act
        result = await subscription_service.handle_stripe_webhook(event_data)

        # Assert
        assert result is True
        mock_subscription_repo.update_status.assert_called_once_with(
            mock_subscription, SubscriptionStatus.ACTIVE
        )

    @pytest.mark.asyncio
    async def test_handle_stripe_webhook_payment_succeeded(
        self, subscription_service, mock_subscription_repo
    ):
        """Test handling Stripe webhook for payment succeeded."""
        # Arrange
        event_data = {
            "type": "invoice.payment_succeeded",
            "data": {"object": {"subscription": "sub_test123"}},
        }
        mock_subscription = Mock()
        mock_subscription_repo.get_by_stripe_subscription_id.return_value = (
            mock_subscription
        )
        mock_subscription_repo.activate = Mock()

        # Act
        result = await subscription_service.handle_stripe_webhook(event_data)

        # Assert
        assert result is True
        mock_subscription_repo.activate.assert_called_once_with(mock_subscription)

    @pytest.mark.asyncio
    async def test_handle_stripe_webhook_payment_failed(
        self, subscription_service, mock_subscription_repo
    ):
        """Test handling Stripe webhook for payment failed."""
        # Arrange
        event_data = {
            "type": "invoice.payment_failed",
            "data": {"object": {"subscription": "sub_test123"}},
        }
        mock_subscription = Mock()
        mock_subscription_repo.get_by_stripe_subscription_id.return_value = (
            mock_subscription
        )
        mock_subscription_repo.update_status = Mock()

        # Act
        result = await subscription_service.handle_stripe_webhook(event_data)

        # Assert
        assert result is True
        mock_subscription_repo.update_status.assert_called_once_with(
            mock_subscription, SubscriptionStatus.PAST_DUE
        )

    def test_get_features_for_tier_premium(self, subscription_service):
        """Test getting features for premium tier."""
        # Act
        features = subscription_service._get_features_for_tier(SubscriptionTier.PREMIUM)

        # Assert
        assert features["quote_search"] is True
        assert features["unlimited_starred_quotes"] is True
        assert features["priority_support"] is True
        assert features["daily_quotes"] is True

    def test_get_features_for_tier_free(self, subscription_service):
        """Test getting features for free tier."""
        # Act
        features = subscription_service._get_features_for_tier(SubscriptionTier.FREE)

        # Assert
        assert features["quote_search"] is False
        assert features["unlimited_starred_quotes"] is False
        assert features["priority_support"] is False
        assert features["daily_quotes"] is True
