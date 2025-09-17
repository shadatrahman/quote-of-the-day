"""Unit tests for authentication service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.services.auth_service import AuthService
from src.models.schemas.user import UserCreate, UserLogin, NotificationSettings
from src.models.database.user import SubscriptionTier
from src.core.exceptions import (
    AuthenticationError,
    ConflictError,
    ValidationError,
    UnauthorizedError,
)


@pytest.fixture
def mock_session():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_session):
    """AuthService instance with mocked session."""
    return AuthService(mock_session)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "test@example.com",
        "is_active": True,
        "is_verified": False,
        "subscription_tier": SubscriptionTier.FREE,
        "timezone": "UTC",
        "notification_settings": {
            "enabled": True,
            "delivery_time": "09:00",
            "weekdays_only": False,
            "pause_until": None,
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login_at": None,
        "last_quote_delivered": None,
    }


@pytest.fixture
def sample_user_create():
    """Sample UserCreate data."""
    return UserCreate(
        email="test@example.com",
        password="TestPassword123",
        password_confirm="TestPassword123",
        timezone="UTC",
        notification_settings=NotificationSettings(
            enabled=True, delivery_time="09:00", weekdays_only=False
        ),
    )


@pytest.fixture
def sample_login_data():
    """Sample UserLogin data."""
    return UserLogin(email="test@example.com", password="TestPassword123")


class TestAuthService:
    """Test cases for AuthService."""

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, auth_service, sample_user_create, sample_user_data
    ):
        """Test successful user registration."""
        # Mock repository methods
        auth_service.user_repo.get_by_email = AsyncMock(return_value=None)
        auth_service.user_repo.create = AsyncMock(
            return_value=MagicMock(**sample_user_data)
        )
        auth_service.user_repo.set_verification_token = AsyncMock(return_value=True)

        # Mock password hashing
        with patch(
            "src.services.auth_service.hash_password", return_value="hashed_password"
        ):
            user, token = await auth_service.register_user(sample_user_create)

        # Assertions
        assert user.email == sample_user_create.email
        assert user.timezone == sample_user_create.timezone
        assert token is not None
        auth_service.user_repo.get_by_email.assert_called_once_with(
            sample_user_create.email
        )
        auth_service.user_repo.create.assert_called_once()
        auth_service.user_repo.set_verification_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self, auth_service, sample_user_create):
        """Test user registration with existing email."""
        # Mock repository to return existing user
        auth_service.user_repo.get_by_email = AsyncMock(return_value=MagicMock())

        with pytest.raises(ConflictError, match="User with this email already exists"):
            await auth_service.register_user(sample_user_create)

    @pytest.mark.asyncio
    async def test_login_user_success(
        self, auth_service, sample_login_data, sample_user_data
    ):
        """Test successful user login."""
        # Mock repository and password verification
        mock_user = MagicMock()
        mock_user.id = sample_user_data["id"]
        mock_user.email = sample_user_data["email"]
        mock_user.is_active = sample_user_data["is_active"]
        mock_user.subscription_tier = sample_user_data["subscription_tier"]
        mock_user.to_dict.return_value = sample_user_data

        auth_service.user_repo.get_by_email = AsyncMock(return_value=mock_user)
        auth_service.user_repo.update_last_login = AsyncMock(return_value=True)

        with patch("src.services.auth_service.verify_password", return_value=True):
            with patch(
                "src.services.auth_service.create_token_response",
                return_value={
                    "access_token": "test_token",
                    "token_type": "bearer",
                    "expires_in": 1800,
                },
            ):
                result = await auth_service.login_user(sample_login_data)

        # Assertions
        assert result.access_token == "test_token"
        assert result.token_type == "bearer"
        assert result.user.email == sample_login_data.email
        auth_service.user_repo.get_by_email.assert_called_once_with(
            sample_login_data.email
        )
        auth_service.user_repo.update_last_login.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(
        self, auth_service, sample_login_data
    ):
        """Test login with invalid credentials."""
        # Mock repository to return None (user not found)
        auth_service.user_repo.get_by_email = AsyncMock(return_value=None)

        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            await auth_service.login_user(sample_login_data)

    @pytest.mark.asyncio
    async def test_login_user_wrong_password(
        self, auth_service, sample_login_data, sample_user_data
    ):
        """Test login with wrong password."""
        # Mock repository and password verification
        mock_user = MagicMock(**sample_user_data)
        auth_service.user_repo.get_by_email = AsyncMock(return_value=mock_user)

        with patch("src.services.auth_service.verify_password", return_value=False):
            with pytest.raises(AuthenticationError, match="Invalid email or password"):
                await auth_service.login_user(sample_login_data)

    @pytest.mark.asyncio
    async def test_login_user_inactive_account(
        self, auth_service, sample_login_data, sample_user_data
    ):
        """Test login with inactive account."""
        # Mock repository with inactive user
        sample_user_data["is_active"] = False
        mock_user = MagicMock(**sample_user_data)
        auth_service.user_repo.get_by_email = AsyncMock(return_value=mock_user)

        with patch("src.services.auth_service.verify_password", return_value=True):
            with pytest.raises(UnauthorizedError, match="Account is deactivated"):
                await auth_service.login_user(sample_login_data)

    @pytest.mark.asyncio
    async def test_verify_email_success(self, auth_service):
        """Test successful email verification."""
        # Mock repository
        mock_user = MagicMock()
        auth_service.user_repo.get_by_verification_token = AsyncMock(
            return_value=mock_user
        )
        auth_service.user_repo.verify_email = AsyncMock(return_value=True)

        from src.models.schemas.user import EmailVerificationRequest

        verification_data = EmailVerificationRequest(token="test_token")

        result = await auth_service.verify_email(verification_data)

        # Assertions
        assert result is True
        auth_service.user_repo.get_by_verification_token.assert_called_once_with(
            "test_token"
        )
        auth_service.user_repo.verify_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, auth_service):
        """Test email verification with invalid token."""
        # Mock repository to return None (token not found)
        auth_service.user_repo.get_by_verification_token = AsyncMock(return_value=None)

        from src.models.schemas.user import EmailVerificationRequest

        verification_data = EmailVerificationRequest(token="invalid_token")

        with pytest.raises(
            ValidationError, match="Invalid or expired verification token"
        ):
            await auth_service.verify_email(verification_data)

    @pytest.mark.asyncio
    async def test_forgot_password_success(self, auth_service):
        """Test successful forgot password."""
        # Mock repository
        mock_user = MagicMock()
        auth_service.user_repo.get_by_email = AsyncMock(return_value=mock_user)
        auth_service.user_repo.set_reset_token = AsyncMock(return_value=True)

        from src.models.schemas.user import ForgotPasswordRequest

        forgot_data = ForgotPasswordRequest(email="test@example.com")

        result = await auth_service.forgot_password(forgot_data)

        # Assertions
        assert "If the email exists" in result
        auth_service.user_repo.get_by_email.assert_called_once_with("test@example.com")
        auth_service.user_repo.set_reset_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_success(self, auth_service):
        """Test successful password reset."""
        # Mock repository
        mock_user = MagicMock()
        auth_service.user_repo.get_by_reset_token = AsyncMock(return_value=mock_user)
        auth_service.user_repo.update_password = AsyncMock(return_value=True)
        auth_service.user_repo.clear_reset_token = AsyncMock(return_value=True)

        from src.models.schemas.user import ResetPasswordRequest

        reset_data = ResetPasswordRequest(
            token="test_token",
            new_password="NewPassword123",
            password_confirm="NewPassword123",
        )

        with patch(
            "src.services.auth_service.hash_password",
            return_value="new_hashed_password",
        ):
            result = await auth_service.reset_password(reset_data)

        # Assertions
        assert result is True
        auth_service.user_repo.get_by_reset_token.assert_called_once_with("test_token")
        auth_service.user_repo.update_password.assert_called_once()
        auth_service.user_repo.clear_reset_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, auth_service):
        """Test password reset with invalid token."""
        # Mock repository to return None (token not found)
        auth_service.user_repo.get_by_reset_token = AsyncMock(return_value=None)

        from src.models.schemas.user import ResetPasswordRequest

        reset_data = ResetPasswordRequest(
            token="invalid_token",
            new_password="NewPassword123",
            password_confirm="NewPassword123",
        )

        with pytest.raises(ValidationError, match="Invalid or expired reset token"):
            await auth_service.reset_password(reset_data)

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, auth_service, sample_user_data):
        """Test getting current user info."""
        # Mock repository
        mock_user = MagicMock()
        mock_user.to_dict.return_value = sample_user_data
        auth_service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

        result = await auth_service.get_current_user("user_id")

        # Assertions
        assert result is not None
        assert result.email == sample_user_data["email"]
        auth_service.user_repo.get_by_id.assert_called_once_with("user_id")

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, auth_service):
        """Test getting current user when user not found."""
        # Mock repository to return None
        auth_service.user_repo.get_by_id = AsyncMock(return_value=None)

        result = await auth_service.get_current_user("user_id")

        # Assertions
        assert result is None
        auth_service.user_repo.get_by_id.assert_called_once_with("user_id")
