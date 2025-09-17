"""Authentication API endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import extract_user_from_token
from src.core.rate_limiting import rate_limit
from src.core.config import settings
from src.core.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
)
from src.models.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    EmailVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    UserUpdate,
)
from src.services.auth_service import AuthService
from src.services.email_service import EmailService

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get current authenticated user."""
    token = credentials.credentials
    user_data = extract_user_from_token(token)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_data


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@rate_limit(requests_per_minute=5, window_minutes=1)
async def register(
    user_data: UserCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    try:
        auth_service = AuthService(db)
        email_service = EmailService()

        # Register user
        user, verification_token = await auth_service.register_user(user_data)

        # Send verification email (skip in test environment)
        if settings.ENVIRONMENT != "test":
            verification_url = (
                f"{request.base_url}api/v1/auth/verify-email?token={verification_token}"
            )
            await email_service.send_verification_email(user.email, verification_url)

        return UserResponse.model_validate(user.to_dict())

    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        import traceback

        print(f"Registration error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/login", response_model=TokenResponse)
@rate_limit(requests_per_minute=5, window_minutes=1)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return access token."""
    try:
        auth_service = AuthService(db)
        return await auth_service.login_user(login_data)

    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        import traceback

        print(f"Login error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    verification_data: EmailVerificationRequest, db: AsyncSession = Depends(get_db)
):
    """Verify user email address."""
    try:
        auth_service = AuthService(db)
        await auth_service.verify_email(verification_data)

        return {"message": "Email verified successfully"}

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    email: str, request: Request, db: AsyncSession = Depends(get_db)
):
    """Resend email verification."""
    try:
        auth_service = AuthService(db)
        email_service = EmailService()

        verification_token = await auth_service.resend_verification_email(email)

        # Send verification email
        verification_url = (
            f"{request.base_url}api/v1/auth/verify-email?token={verification_token}"
        )
        await email_service.send_verification_email(email, verification_url)

        return {"message": "Verification email sent"}

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@rate_limit(requests_per_minute=3, window_minutes=1)
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Initiate password reset process."""
    try:
        auth_service = AuthService(db)
        email_service = EmailService()

        message = await auth_service.forgot_password(forgot_data)

        # Get user to send reset email if exists
        user = await auth_service.user_repo.get_by_email(forgot_data.email)
        if user:
            reset_url = f"{request.base_url}api/v1/auth/reset-password?token={user.password_reset_token}"
            await email_service.send_password_reset_email(user.email, reset_url)

        return {"message": message}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@rate_limit(requests_per_minute=3, window_minutes=1)
async def reset_password(
    reset_data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """Reset user password with token."""
    try:
        auth_service = AuthService(db)
        await auth_service.reset_password(reset_data)

        return {"message": "Password reset successfully"}

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user information."""
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(current_user["user_id"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    except Exception as e:
        import traceback

        print(f"Get current user error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile."""
    try:
        auth_service = AuthService(db)
        updated_user = await auth_service.update_user_profile(
            current_user["user_id"], user_data.dict(exclude_unset=True)
        )

        return updated_user

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password."""
    try:
        auth_service = AuthService(db)
        await auth_service.change_password(
            current_user["user_id"],
            password_data.current_password,
            password_data.new_password,
        )

        return {"message": "Password changed successfully"}

    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """Logout user (client-side token removal)."""
    return {"message": "Logged out successfully"}


@router.post("/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_account(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate user account."""
    try:
        auth_service = AuthService(db)
        await auth_service.deactivate_user(current_user["user_id"])

        return {"message": "Account deactivated successfully"}

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
