"""Authentication service for user management and authentication."""

from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database.user import User, SubscriptionTier
from src.models.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    EmailVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from src.repositories.user_repository import UserRepository
from src.core.security import (
    hash_password,
    verify_password,
    create_token_response,
    create_verification_token,
    create_reset_token,
    get_email_verification_expiration,
    get_password_reset_expiration,
)
from src.core.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
)


class AuthService:
    """Service for authentication and user management."""

    def __init__(self, session: AsyncSession):
        """Initialize auth service with database session."""
        self.session = session
        self.user_repo = UserRepository(session)

    async def register_user(self, user_data: UserCreate) -> Tuple[User, str]:
        """Register a new user."""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ConflictError("User with this email already exists")

        # Hash password
        password_hash = hash_password(user_data.password)

        # Create user
        user = await self.user_repo.create(user_data, password_hash)

        # Generate verification token
        verification_token = create_verification_token()
        expires_at = get_email_verification_expiration()

        await self.user_repo.set_verification_token(
            str(user.id), verification_token, expires_at
        )

        return user, verification_token

    async def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return token."""
        # Get user by email
        user = await self.user_repo.get_by_email(login_data.email)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        # Update last login
        await self.user_repo.update_last_login(str(user.id))

        # Create token response
        token_data = create_token_response(
            str(user.id), user.email, user.subscription_tier.value
        )

        return TokenResponse(
            **token_data, user=UserResponse.model_validate(user.to_dict())
        )

    async def verify_email(self, verification_data: EmailVerificationRequest) -> bool:
        """Verify user email with token."""
        user = await self.user_repo.get_by_verification_token(verification_data.token)
        if not user:
            raise ValidationError("Invalid or expired verification token")

        # Mark email as verified
        await self.user_repo.verify_email(str(user.id))
        return True

    async def resend_verification_email(self, email: str) -> str:
        """Resend verification email."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User not found")

        if user.is_verified:
            raise ValidationError("Email is already verified")

        # Generate new verification token
        verification_token = create_verification_token()
        expires_at = get_email_verification_expiration()

        await self.user_repo.set_verification_token(
            str(user.id), verification_token, expires_at
        )

        return verification_token

    async def forgot_password(self, forgot_data: ForgotPasswordRequest) -> str:
        """Initiate password reset process."""
        user = await self.user_repo.get_by_email(forgot_data.email)
        if not user:
            # Don't reveal if user exists for security
            return "If the email exists, a password reset link has been sent"

        # Generate reset token
        reset_token = create_reset_token()
        expires_at = get_password_reset_expiration()

        await self.user_repo.set_reset_token(str(user.id), reset_token, expires_at)

        return "If the email exists, a password reset link has been sent"

    async def reset_password(self, reset_data: ResetPasswordRequest) -> bool:
        """Reset user password with token."""
        user = await self.user_repo.get_by_reset_token(reset_data.token)
        if not user:
            raise ValidationError("Invalid or expired reset token")

        # Hash new password
        password_hash = hash_password(reset_data.new_password)

        # Update password and clear reset token
        await self.user_repo.update_password(str(user.id), password_hash)
        await self.user_repo.clear_reset_token(str(user.id))

        return True

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")

        # Hash new password
        password_hash = hash_password(new_password)

        # Update password
        await self.user_repo.update_password(user_id, password_hash)
        return True

    async def get_current_user(self, user_id: str) -> Optional[UserResponse]:
        """Get current user information."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        return UserResponse.model_validate(user.to_dict())

    async def update_user_profile(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> UserResponse:
        """Update user profile information."""
        from src.models.schemas.user import UserUpdate

        update_data = UserUpdate(**user_data)
        updated_user = await self.user_repo.update(user_id, update_data)

        if not updated_user:
            raise NotFoundError("User not found")

        return UserResponse.from_orm(updated_user)

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        await self.user_repo.deactivate(user_id)
        return True

    async def activate_user(self, user_id: str) -> bool:
        """Activate user account."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        await self.user_repo.activate(user_id)
        return True

    async def upgrade_subscription(self, user_id: str) -> bool:
        """Upgrade user to premium subscription."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if user.subscription_tier == SubscriptionTier.PREMIUM:
            raise ValidationError("User already has premium subscription")

        await self.user_repo.update_subscription_tier(user_id, SubscriptionTier.PREMIUM)
        return True

    async def downgrade_subscription(self, user_id: str) -> bool:
        """Downgrade user to free subscription."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if user.subscription_tier == SubscriptionTier.FREE:
            raise ValidationError("User already has free subscription")

        await self.user_repo.update_subscription_tier(user_id, SubscriptionTier.FREE)
        return True
