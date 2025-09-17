"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

from src.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def create_verification_token() -> str:
    """Create a secure verification token."""
    return secrets.token_urlsafe(32)


def create_reset_token() -> str:
    """Create a secure password reset token."""
    return secrets.token_urlsafe(32)


def get_token_expiration(hours: int = 24) -> datetime:
    """Get token expiration datetime."""
    return datetime.utcnow() + timedelta(hours=hours)


def get_password_reset_expiration(hours: int = 1) -> datetime:
    """Get password reset token expiration datetime."""
    return datetime.utcnow() + timedelta(hours=hours)


def get_email_verification_expiration(hours: int = 24) -> datetime:
    """Get email verification token expiration datetime."""
    return datetime.utcnow() + timedelta(hours=hours)


def create_token_response(
    user_id: str, email: str, subscription_tier: str
) -> Dict[str, Any]:
    """Create token response data."""
    token_data = {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "subscription_tier": subscription_tier,
        "type": "access",
    }

    access_token = create_access_token(token_data)
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


def extract_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Extract user information from JWT token."""
    payload = verify_token(token)
    if not payload:
        return None

    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "subscription_tier": payload.get("subscription_tier"),
    }
