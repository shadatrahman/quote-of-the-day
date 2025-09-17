"""User Pydantic schemas for API validation and serialization."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from enum import Enum

from src.models.database.user import SubscriptionTier


class NotificationSettings(BaseModel):
    """Notification settings schema."""

    enabled: bool = Field(default=True, description="Whether notifications are enabled")
    delivery_time: str = Field(
        default="09:00", description="Time to deliver notifications (HH:MM)"
    )
    weekdays_only: bool = Field(
        default=False, description="Only send notifications on weekdays"
    )
    pause_until: Optional[datetime] = Field(
        default=None, description="Pause notifications until this date"
    )

    @field_validator("delivery_time")
    @classmethod
    def validate_delivery_time(cls, v):
        """Validate delivery time format."""
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("delivery_time must be in HH:MM format")


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")
    timezone: str = Field(default="UTC", description="User timezone")
    notification_settings: NotificationSettings = Field(
        default_factory=NotificationSettings,
        description="User notification preferences",
    )


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )
    password_confirm: str = Field(..., description="Password confirmation")

    @model_validator(mode="after")
    def passwords_match(self):
        """Validate that passwords match."""
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for user updates."""

    timezone: Optional[str] = Field(None, description="User timezone")
    notification_settings: Optional[NotificationSettings] = Field(
        None, description="Notification preferences"
    )


class UserResponse(UserBase):
    """Schema for user API responses."""

    id: str = Field(..., description="User unique identifier")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    subscription_tier: SubscriptionTier = Field(
        ..., description="User subscription tier"
    )
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    last_quote_delivered: Optional[datetime] = Field(
        None, description="Last quote delivery timestamp"
    )

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""

    token: str = Field(..., description="Email verification token")


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""

    email: EmailStr = Field(..., description="User email address")


class ResetPasswordRequest(BaseModel):
    """Schema for password reset request."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )
    password_confirm: str = Field(..., description="Password confirmation")

    @model_validator(mode="after")
    def passwords_match(self):
        """Validate that passwords match."""
        if self.new_password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain at least one digit")
        return v


class ChangePasswordRequest(BaseModel):
    """Schema for change password request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )
    password_confirm: str = Field(..., description="Password confirmation")

    @model_validator(mode="after")
    def passwords_match(self):
        """Validate that passwords match."""
        if self.new_password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain at least one digit")
        return v
