"""End-to-end tests for subscription flow."""

import pytest
import asyncio
import sys
import os
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import Mock, AsyncMock, patch

# Set environment variables before importing the app
os.environ["ENVIRONMENT"] = "test"
os.environ["ALLOWED_HOSTS"] = "testserver,localhost,test"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_12345"
os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://quote_user:quote_password@localhost:5432/quote_of_the_day_dev"
)
os.environ["REDIS_URL"] = "redis://localhost:6379/1"

# Add the API source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from src.main import app
from src.models.database.subscription import (
    Subscription,
    SubscriptionStatus,
    SubscriptionTier,
)
from src.models.database.user import User, SubscriptionTier as UserSubscriptionTier


@pytest.fixture
def test_app():
    """Test FastAPI application."""
    # Override dependencies for E2E tests
    from src.api.v1.auth import get_current_user
    from src.core.database import get_db
    from src.api.v1.subscription import get_subscription_service
    from src.services.subscription_service import SubscriptionService
    from unittest.mock import Mock, AsyncMock

    def mock_get_current_user():
        """Mock authentication dependency for testing."""
        return {
            "user_id": "test-user-id",
            "email": "test@example.com",
            "is_active": True,
            "is_verified": True,
        }

    def mock_get_db():
        """Mock database dependency for testing."""
        return None

    def mock_get_subscription_service():
        """Mock subscription service dependency for testing."""
        service = SubscriptionService(Mock(), Mock())
        return service

    # Override dependencies
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_subscription_service] = mock_get_subscription_service

    return app


@pytest.fixture
def client(test_app):
    """Async test client."""
    return AsyncClient(app=test_app, base_url="http://test")


@pytest.fixture
def mock_user():
    """Mock user for testing."""
    return User(
        id="test-user-id",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
        is_verified=True,
        subscription_tier=UserSubscriptionTier.FREE,
        timezone="UTC",
        notification_settings={},
    )


@pytest.fixture
def mock_premium_user():
    """Mock premium user for testing."""
    return User(
        id="test-premium-user-id",
        email="premium@example.com",
        password_hash="hashed_password",
        is_active=True,
        is_verified=True,
        subscription_tier=UserSubscriptionTier.PREMIUM,
        timezone="UTC",
        notification_settings={},
    )


@pytest.fixture
def mock_subscription():
    """Mock subscription for testing."""
    return Subscription(
        id="test-subscription-id",
        user_id="test-user-id",
        tier=SubscriptionTier.PREMIUM,
        status=SubscriptionStatus.ACTIVE,
        stripe_customer_id="cus_test123",
        stripe_subscription_id="sub_test123",
        current_period_start="2025-01-01T00:00:00Z",
        current_period_end="2025-01-31T00:00:00Z",
        cancelled_at=None,
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z",
    )


class TestSubscriptionE2EFlow:
    """End-to-end tests for subscription flow."""

    @pytest.mark.asyncio
    async def test_complete_subscription_upgrade_flow(
        self, client, mock_user, mock_subscription, test_app
    ):
        """Test complete subscription upgrade flow."""
        # Arrange - Override the service for this test
        from src.api.v1.subscription import get_subscription_service
        from src.services.subscription_service import SubscriptionService
        from src.models.schemas.subscription import SubscriptionStatusResponse
        from unittest.mock import Mock, AsyncMock
        from datetime import datetime

        def mock_upgrade_flow_service():
            service = SubscriptionService(Mock(), Mock())

            # Initial status - free user
            service.get_subscription_status = AsyncMock(
                return_value=SubscriptionStatusResponse(
                    subscription=None,
                    is_premium=False,
                    features={
                        "daily_quotes": True,
                        "quote_search": False,
                        "unlimited_starred_quotes": False,
                    },
                )
            )

            # Upgrade method
            service.upgrade_to_premium = AsyncMock(return_value=mock_subscription)
            return service

        test_app.dependency_overrides[get_subscription_service] = (
            mock_upgrade_flow_service
        )

        # Step 1: Check initial subscription status
        response = await client.get("/api/v1/subscription/")
        assert response.status_code == 200
        data = response.json()
        assert data["is_premium"] is False
        assert data["subscription"] is None
        assert data["features"]["quote_search"] is False

        # Step 2: Upgrade to premium
        upgrade_data = {"payment_method_id": "pm_test123"}
        response = await client.post("/api/v1/subscription/upgrade", json=upgrade_data)
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "PREMIUM"
        assert data["status"] == "ACTIVE"

        # Step 3: Check updated subscription status
        def mock_upgraded_service():
            service = SubscriptionService(Mock(), Mock())
            service.get_subscription_status = AsyncMock(
                return_value=SubscriptionStatusResponse(
                    subscription=mock_subscription,
                    is_premium=True,
                    features={
                        "daily_quotes": True,
                        "quote_search": True,
                        "unlimited_starred_quotes": True,
                    },
                )
            )
            service.check_feature_access = AsyncMock(return_value=True)
            return service

        test_app.dependency_overrides[get_subscription_service] = mock_upgraded_service

        response = await client.get("/api/v1/subscription/")
        assert response.status_code == 200
        data = response.json()
        assert data["is_premium"] is True
        assert data["subscription"] is not None
        assert data["features"]["quote_search"] is True

        # Step 4: Check feature access
        response = await client.get("/api/v1/subscription/check/quote_search")
        assert response.status_code == 200
        data = response.json()
        assert data["has_access"] is True

    @patch("src.api.v1.subscription.get_current_user")
    @patch("src.api.v1.subscription.get_subscription_service")
    @pytest.mark.asyncio
    async def test_subscription_cancellation_flow(
        self,
        mock_get_service,
        mock_get_user,
        client,
        mock_premium_user,
        mock_subscription,
    ):
        """Test subscription cancellation flow."""
        # Arrange
        mock_get_user.return_value = mock_premium_user
        mock_service = Mock()

        # Mock service responses
        mock_service.get_subscription_status = AsyncMock(
            return_value={
                "subscription": mock_subscription,
                "is_premium": True,
                "features": {
                    "daily_quotes": True,
                    "quote_search": True,
                    "unlimited_starred_quotes": True,
                },
            }
        )
        mock_service.cancel_subscription = AsyncMock(
            return_value={
                "message": "Subscription cancelled successfully",
                "cancelled_at": "2025-01-15T00:00:00Z",
            }
        )
        mock_get_service.return_value = mock_service

        # Step 1: Check initial premium status
        response = await client.get("/api/v1/subscription/")
        assert response.status_code == 200
        data = response.json()
        assert data["is_premium"] is True
        assert data["features"]["quote_search"] is True

        # Step 2: Cancel subscription
        cancel_data = {"reason": "No longer needed"}
        response = await client.post("/api/v1/subscription/cancel", json=cancel_data)
        assert response.status_code == 200
        data = response.json()
        assert "cancelled successfully" in data["message"]

        # Step 3: Check updated status (would be cancelled in real scenario)
        mock_service.get_subscription_status = AsyncMock(
            return_value={
                "subscription": mock_subscription,
                "is_premium": False,  # Cancelled
                "features": {
                    "daily_quotes": True,
                    "quote_search": False,
                    "unlimited_starred_quotes": False,
                },
            }
        )

        response = await client.get("/api/v1/subscription/")
        assert response.status_code == 200
        data = response.json()
        assert data["is_premium"] is False
        assert data["features"]["quote_search"] is False

    @patch("src.api.v1.subscription.get_current_user")
    @patch("src.api.v1.subscription.get_subscription_service")
    @pytest.mark.asyncio
    async def test_feature_access_control_flow(
        self, mock_get_service, mock_get_user, client, mock_user
    ):
        """Test feature access control flow."""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_service = Mock()

        # Mock free user features
        mock_service.get_available_features = AsyncMock(
            return_value={
                "daily_quotes": True,
                "quote_search": False,
                "unlimited_starred_quotes": False,
                "priority_support": False,
            }
        )
        mock_service.check_feature_access = AsyncMock(return_value=False)
        mock_get_service.return_value = mock_service

        # Step 1: Get available features
        response = await client.get("/api/v1/subscription/features")
        assert response.status_code == 200
        data = response.json()
        assert data["daily_quotes"] is True
        assert data["quote_search"] is False
        assert data["unlimited_starred_quotes"] is False

        # Step 2: Check specific feature access
        response = await client.get("/api/v1/subscription/check/quote_search")
        assert response.status_code == 200
        data = response.json()
        assert data["has_access"] is False
        assert data["feature"] == "quote_search"

        # Step 3: Check free feature access
        mock_service.check_feature_access = AsyncMock(return_value=True)

        response = await client.get("/api/v1/subscription/check/daily_quotes")
        assert response.status_code == 200
        data = response.json()
        assert data["has_access"] is True
        assert data["feature"] == "daily_quotes"

    @patch("src.api.v1.subscription.get_current_user")
    @patch("src.api.v1.subscription.get_subscription_service")
    @pytest.mark.asyncio
    async def test_error_handling_flow(
        self, mock_get_service, mock_get_user, client, mock_user
    ):
        """Test error handling in subscription flow."""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_service = Mock()

        # Mock service error
        mock_service.get_subscription_status = AsyncMock(
            side_effect=Exception("Database connection failed")
        )
        mock_get_service.return_value = mock_service

        # Step 1: Test subscription status error
        response = await client.get("/api/v1/subscription/")
        assert response.status_code == 500
        data = response.json()
        assert "Failed to get subscription status" in data["detail"]

        # Step 2: Test upgrade error
        mock_service.upgrade_to_premium = AsyncMock(
            side_effect=ValueError("Payment method invalid")
        )

        upgrade_data = {"payment_method_id": "invalid_pm"}
        response = await client.post("/api/v1/subscription/upgrade", json=upgrade_data)
        assert response.status_code == 400
        data = response.json()
        assert "Payment method invalid" in data["detail"]

        # Step 3: Test cancellation error
        mock_service.cancel_subscription = AsyncMock(
            side_effect=ValueError("No subscription found for user")
        )

        cancel_data = {}
        response = await client.post("/api/v1/subscription/cancel", json=cancel_data)
        assert response.status_code == 400
        data = response.json()
        assert "No subscription found for user" in data["detail"]

    @patch("src.api.v1.subscription.get_current_user")
    @patch("src.api.v1.subscription.get_subscription_service")
    @pytest.mark.asyncio
    async def test_validation_error_flow(
        self, mock_get_service, mock_get_user, client, mock_user
    ):
        """Test validation error handling."""
        # Arrange
        mock_get_user.return_value = mock_user
        mock_get_service.return_value = Mock()

        # Step 1: Test invalid payment method
        upgrade_data = {"payment_method_id": ""}  # Empty payment method
        response = await client.post("/api/v1/subscription/upgrade", json=upgrade_data)
        assert response.status_code == 422  # Validation error

        # Step 2: Test missing payment method
        upgrade_data = {}  # Missing payment method
        response = await client.post("/api/v1/subscription/upgrade", json=upgrade_data)
        assert response.status_code == 422  # Validation error

        # Step 3: Test invalid feature name
        response = await client.get("/api/v1/subscription/check/")
        assert response.status_code == 404  # Not found

    @pytest.mark.asyncio
    async def test_authentication_required(self, client):
        """Test that authentication is required for subscription endpoints."""
        # Create a client without dependency overrides
        from httpx import AsyncClient

        # Create a clean app instance without auth overrides
        clean_client = AsyncClient(app=app, base_url="http://test")

        # Test without authentication
        response = await clean_client.get("/api/v1/subscription/")
        assert response.status_code == 403  # Forbidden (not authenticated)

        response = await client.post("/api/v1/subscription/upgrade", json={})
        assert response.status_code == 401  # Unauthorized

        response = await client.post("/api/v1/subscription/cancel", json={})
        assert response.status_code == 401  # Unauthorized

        response = await client.get("/api/v1/subscription/features")
        assert response.status_code == 401  # Unauthorized

        response = await client.get("/api/v1/subscription/check/feature")
        assert response.status_code == 401  # Unauthorized
