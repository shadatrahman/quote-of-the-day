"""User repository for data access operations."""

from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.database.user import User, SubscriptionTier
from src.models.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """Repository for user data access operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def create(self, user_data: UserCreate, password_hash: str) -> User:
        """Create a new user."""
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            timezone=user_data.timezone,
            notification_settings=user_data.notification_settings.dict(),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_verification_token(self, token: str) -> Optional[User]:
        """Get user by email verification token."""
        result = await self.session.execute(
            select(User).where(
                User.email_verification_token == token,
                User.email_verification_expires_at
                > User.created_at,  # Token not expired
            )
        )
        return result.scalar_one_or_none()

    async def get_by_reset_token(self, token: str) -> Optional[User]:
        """Get user by password reset token."""
        result = await self.session.execute(
            select(User).where(
                User.password_reset_token == token,
                User.password_reset_expires_at > User.created_at,  # Token not expired
            )
        )
        return result.scalar_one_or_none()

    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        update_data = user_data.dict(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(user_id)

        # Convert notification_settings to dict if present
        if "notification_settings" in update_data:
            update_data["notification_settings"] = update_data[
                "notification_settings"
            ].dict()

        await self.session.execute(
            update(User).where(User.id == user_id).values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_id(user_id)

    async def update_password(self, user_id: str, password_hash: str) -> bool:
        """Update user password."""
        await self.session.execute(
            update(User).where(User.id == user_id).values(password_hash=password_hash)
        )
        await self.session.commit()
        return True

    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        await self.session.execute(
            update(User).where(User.id == user_id).values(last_login_at=User.updated_at)
        )
        await self.session.commit()
        return True

    async def set_verification_token(
        self, user_id: str, token: str, expires_at
    ) -> bool:
        """Set email verification token."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                email_verification_token=token, email_verification_expires_at=expires_at
            )
        )
        await self.session.commit()
        return True

    async def set_reset_token(self, user_id: str, token: str, expires_at) -> bool:
        """Set password reset token."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_reset_token=token, password_reset_expires_at=expires_at)
        )
        await self.session.commit()
        return True

    async def verify_email(self, user_id: str) -> bool:
        """Mark user email as verified."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                is_verified=True,
                email_verification_token=None,
                email_verification_expires_at=None,
            )
        )
        await self.session.commit()
        return True

    async def clear_reset_token(self, user_id: str) -> bool:
        """Clear password reset token."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_reset_token=None, password_reset_expires_at=None)
        )
        await self.session.commit()
        return True

    async def deactivate(self, user_id: str) -> bool:
        """Deactivate user account."""
        await self.session.execute(
            update(User).where(User.id == user_id).values(is_active=False)
        )
        await self.session.commit()
        return True

    async def activate(self, user_id: str) -> bool:
        """Activate user account."""
        await self.session.execute(
            update(User).where(User.id == user_id).values(is_active=True)
        )
        await self.session.commit()
        return True

    async def update_subscription_tier(
        self, user_id: str, tier: SubscriptionTier
    ) -> bool:
        """Update user subscription tier."""
        await self.session.execute(
            update(User).where(User.id == user_id).values(subscription_tier=tier)
        )
        await self.session.commit()
        return True

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        result = await self.session.execute(
            select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        )
        return result.scalars().all()

    async def count(self) -> int:
        """Get total user count."""
        result = await self.session.execute(select(User.id))
        return len(result.scalars().all())

    async def delete(self, user_id: str) -> bool:
        """Delete user account."""
        await self.session.execute(delete(User).where(User.id == user_id))
        await self.session.commit()
        return True
