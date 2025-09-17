"""Unit tests for Stripe service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import stripe

from src.services.stripe_service import StripeService


@pytest.fixture
def stripe_service():
    """Create Stripe service instance."""
    return StripeService()


@pytest.fixture
def mock_stripe_customer():
    """Mock Stripe customer data."""
    return {
        "id": "cus_test123",
        "email": "test@example.com",
        "name": "Test User",
        "metadata": {"source": "quote_of_the_day"},
    }


@pytest.fixture
def mock_stripe_subscription():
    """Mock Stripe subscription data."""
    return {
        "id": "sub_test123",
        "customer": "cus_test123",
        "status": "active",
        "current_period_start": 1640995200,
        "current_period_end": 1643673600,
        "items": {"data": [{"price": {"id": "price_test123"}}]},
    }


class TestStripeService:
    """Test cases for StripeService."""

    @patch("stripe.Customer.create")
    @pytest.mark.asyncio
    async def test_create_customer_success(
        self, mock_create, stripe_service, mock_stripe_customer
    ):
        """Test successful customer creation."""
        # Arrange
        mock_create.return_value = mock_stripe_customer

        # Act
        result = await stripe_service.create_customer("test@example.com", "Test User")

        # Assert
        assert result == mock_stripe_customer
        mock_create.assert_called_once_with(
            email="test@example.com",
            name="Test User",
            metadata={"source": "quote_of_the_day"},
        )

    @patch("stripe.Customer.create")
    @pytest.mark.asyncio
    async def test_create_customer_stripe_error(self, mock_create, stripe_service):
        """Test customer creation with Stripe error."""
        # Arrange
        mock_create.side_effect = stripe.error.StripeError("API Error")

        # Act & Assert
        with pytest.raises(stripe.error.StripeError):
            await stripe_service.create_customer("test@example.com")

    @patch("stripe.Customer.retrieve")
    @pytest.mark.asyncio
    async def test_get_customer_success(
        self, mock_retrieve, stripe_service, mock_stripe_customer
    ):
        """Test successful customer retrieval."""
        # Arrange
        mock_retrieve.return_value = mock_stripe_customer

        # Act
        result = await stripe_service.get_customer("cus_test123")

        # Assert
        assert result == mock_stripe_customer
        mock_retrieve.assert_called_once_with("cus_test123")

    @patch("stripe.Customer.retrieve")
    @pytest.mark.asyncio
    async def test_get_customer_not_found(self, mock_retrieve, stripe_service):
        """Test customer retrieval when customer not found."""
        # Arrange
        mock_retrieve.side_effect = stripe.error.InvalidRequestError(
            "Customer not found", None
        )

        # Act
        result = await stripe_service.get_customer("cus_nonexistent")

        # Assert
        assert result is None

    @patch("stripe.Customer.modify")
    @pytest.mark.asyncio
    async def test_update_customer_success(
        self, mock_modify, stripe_service, mock_stripe_customer
    ):
        """Test successful customer update."""
        # Arrange
        mock_modify.return_value = mock_stripe_customer

        # Act
        result = await stripe_service.update_customer(
            "cus_test123", name="Updated Name"
        )

        # Assert
        assert result == mock_stripe_customer
        mock_modify.assert_called_once_with("cus_test123", name="Updated Name")

    @patch("stripe.Customer.delete")
    @pytest.mark.asyncio
    async def test_delete_customer_success(self, mock_delete, stripe_service):
        """Test successful customer deletion."""
        # Arrange
        mock_delete.return_value = {"deleted": True}

        # Act
        result = await stripe_service.delete_customer("cus_test123")

        # Assert
        assert result is True
        mock_delete.assert_called_once_with("cus_test123")

    @patch("stripe.PaymentMethod.attach")
    @pytest.mark.asyncio
    async def test_create_payment_method_success(self, mock_attach, stripe_service):
        """Test successful payment method attachment."""
        # Arrange
        mock_payment_method = {"id": "pm_test123", "customer": "cus_test123"}
        mock_attach.return_value = mock_payment_method

        # Act
        result = await stripe_service.create_payment_method("cus_test123", "pm_test123")

        # Assert
        assert result == mock_payment_method
        mock_attach.assert_called_once_with("pm_test123", customer="cus_test123")

    @patch("stripe.Customer.modify")
    @pytest.mark.asyncio
    async def test_set_default_payment_method_success(
        self, mock_modify, stripe_service, mock_stripe_customer
    ):
        """Test successful default payment method setting."""
        # Arrange
        mock_modify.return_value = mock_stripe_customer

        # Act
        result = await stripe_service.set_default_payment_method(
            "cus_test123", "pm_test123"
        )

        # Assert
        assert result == mock_stripe_customer
        mock_modify.assert_called_once_with(
            "cus_test123", invoice_settings={"default_payment_method": "pm_test123"}
        )

    @patch("stripe.Subscription.create")
    @pytest.mark.asyncio
    async def test_create_subscription_success(
        self, mock_create, stripe_service, mock_stripe_subscription
    ):
        """Test successful subscription creation."""
        # Arrange
        mock_create.return_value = mock_stripe_subscription

        # Act
        result = await stripe_service.create_subscription(
            "cus_test123", "price_test123", "pm_test123"
        )

        # Assert
        assert result == mock_stripe_subscription
        mock_create.assert_called_once()

    @patch("stripe.Subscription.create")
    @pytest.mark.asyncio
    async def test_create_subscription_without_payment_method(
        self, mock_create, stripe_service, mock_stripe_subscription
    ):
        """Test subscription creation without payment method."""
        # Arrange
        mock_create.return_value = mock_stripe_subscription

        # Act
        result = await stripe_service.create_subscription(
            "cus_test123", "price_test123"
        )

        # Assert
        assert result == mock_stripe_subscription
        mock_create.assert_called_once()

    @patch("stripe.Subscription.retrieve")
    @pytest.mark.asyncio
    async def test_get_subscription_success(
        self, mock_retrieve, stripe_service, mock_stripe_subscription
    ):
        """Test successful subscription retrieval."""
        # Arrange
        mock_retrieve.return_value = mock_stripe_subscription

        # Act
        result = await stripe_service.get_subscription("sub_test123")

        # Assert
        assert result == mock_stripe_subscription
        mock_retrieve.assert_called_once_with("sub_test123")

    @patch("stripe.Subscription.retrieve")
    @pytest.mark.asyncio
    async def test_get_subscription_not_found(self, mock_retrieve, stripe_service):
        """Test subscription retrieval when subscription not found."""
        # Arrange
        mock_retrieve.side_effect = stripe.error.InvalidRequestError(
            "Subscription not found", None
        )

        # Act
        result = await stripe_service.get_subscription("sub_nonexistent")

        # Assert
        assert result is None

    @patch("stripe.Subscription.modify")
    @pytest.mark.asyncio
    async def test_update_subscription_success(
        self, mock_modify, stripe_service, mock_stripe_subscription
    ):
        """Test successful subscription update."""
        # Arrange
        mock_modify.return_value = mock_stripe_subscription

        # Act
        result = await stripe_service.update_subscription(
            "sub_test123", status="active"
        )

        # Assert
        assert result == mock_stripe_subscription
        mock_modify.assert_called_once_with("sub_test123", status="active")

    @patch("stripe.Subscription.modify")
    @pytest.mark.asyncio
    async def test_cancel_subscription_at_period_end(
        self, mock_modify, stripe_service, mock_stripe_subscription
    ):
        """Test subscription cancellation at period end."""
        # Arrange
        mock_modify.return_value = mock_stripe_subscription

        # Act
        result = await stripe_service.cancel_subscription(
            "sub_test123", immediately=False
        )

        # Assert
        assert result == mock_stripe_subscription
        mock_modify.assert_called_once_with("sub_test123", cancel_at_period_end=True)

    @patch("stripe.Subscription.delete")
    @pytest.mark.asyncio
    async def test_cancel_subscription_immediately(
        self, mock_delete, stripe_service, mock_stripe_subscription
    ):
        """Test immediate subscription cancellation."""
        # Arrange
        mock_delete.return_value = mock_stripe_subscription

        # Act
        result = await stripe_service.cancel_subscription(
            "sub_test123", immediately=True
        )

        # Assert
        assert result == mock_stripe_subscription
        mock_delete.assert_called_once_with("sub_test123")

    @patch("stripe.Subscription.modify")
    @pytest.mark.asyncio
    async def test_reactivate_subscription_success(
        self, mock_modify, stripe_service, mock_stripe_subscription
    ):
        """Test successful subscription reactivation."""
        # Arrange
        mock_modify.return_value = mock_stripe_subscription

        # Act
        result = await stripe_service.reactivate_subscription("sub_test123")

        # Assert
        assert result == mock_stripe_subscription
        mock_modify.assert_called_once_with("sub_test123", cancel_at_period_end=False)

    @patch("stripe.Subscription.list")
    @pytest.mark.asyncio
    async def test_get_customer_subscriptions_success(self, mock_list, stripe_service):
        """Test successful customer subscriptions retrieval."""
        # Arrange
        mock_subscriptions = Mock()
        mock_subscriptions.data = [{"id": "sub_test123"}, {"id": "sub_test456"}]
        mock_list.return_value = mock_subscriptions

        # Act
        result = await stripe_service.get_customer_subscriptions("cus_test123")

        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "sub_test123"
        mock_list.assert_called_once_with(customer="cus_test123")

    @patch("stripe.billing_portal.Session.create")
    @pytest.mark.asyncio
    async def test_create_billing_portal_session_success(
        self, mock_create, stripe_service
    ):
        """Test successful billing portal session creation."""
        # Arrange
        mock_session = {
            "id": "bps_test123",
            "url": "https://billing.stripe.com/session",
        }
        mock_create.return_value = mock_session

        # Act
        result = await stripe_service.create_billing_portal_session(
            "cus_test123", "https://example.com/return"
        )

        # Assert
        assert result == mock_session
        mock_create.assert_called_once_with(
            customer="cus_test123", return_url="https://example.com/return"
        )

    @patch("stripe.PaymentIntent.create")
    @pytest.mark.asyncio
    async def test_create_payment_intent_success(self, mock_create, stripe_service):
        """Test successful payment intent creation."""
        # Arrange
        mock_intent = {"id": "pi_test123", "client_secret": "pi_test123_secret"}
        mock_create.return_value = mock_intent

        # Act
        result = await stripe_service.create_payment_intent(
            1000, "usd", "cus_test123", "pm_test123"
        )

        # Assert
        assert result == mock_intent
        mock_create.assert_called_once()

    @patch("stripe.Webhook.construct_event")
    def test_verify_webhook_signature_success(self, mock_construct, stripe_service):
        """Test successful webhook signature verification."""
        # Arrange
        mock_construct.return_value = {
            "id": "evt_test123",
            "type": "customer.subscription.created",
        }
        payload = b'{"id": "evt_test123"}'
        signature = "t=1234567890,v1=signature"

        # Act
        result = stripe_service.verify_webhook_signature(payload, signature)

        # Assert
        assert result is True
        mock_construct.assert_called_once_with(
            payload, signature, stripe_service.webhook_secret
        )

    @patch("stripe.Webhook.construct_event")
    def test_verify_webhook_signature_invalid(self, mock_construct, stripe_service):
        """Test webhook signature verification with invalid signature."""
        # Arrange
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature", "signature"
        )
        payload = b'{"id": "evt_test123"}'
        signature = "invalid_signature"

        # Act
        result = stripe_service.verify_webhook_signature(payload, signature)

        # Assert
        assert result is False

    @patch("stripe.Webhook.construct_event")
    def test_parse_webhook_event_success(self, mock_construct, stripe_service):
        """Test successful webhook event parsing."""
        # Arrange
        mock_event = {"id": "evt_test123", "type": "customer.subscription.created"}
        mock_construct.return_value = mock_event
        payload = b'{"id": "evt_test123"}'
        signature = "t=1234567890,v1=signature"

        # Act
        result = stripe_service.parse_webhook_event(payload, signature)

        # Assert
        assert result == mock_event
        mock_construct.assert_called_once_with(
            payload, signature, stripe_service.webhook_secret
        )

    @patch("stripe.Webhook.construct_event")
    def test_parse_webhook_event_invalid_signature(
        self, mock_construct, stripe_service
    ):
        """Test webhook event parsing with invalid signature."""
        # Arrange
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature", "signature"
        )
        payload = b'{"id": "evt_test123"}'
        signature = "invalid_signature"

        # Act
        result = stripe_service.parse_webhook_event(payload, signature)

        # Assert
        assert result is None

    def test_get_publishable_key(self, stripe_service):
        """Test getting publishable key."""
        # Act
        result = stripe_service.get_publishable_key()

        # Assert
        assert result == stripe_service.publishable_key
