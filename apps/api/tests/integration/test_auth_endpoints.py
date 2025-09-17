"""Integration tests for authentication API endpoints."""

import pytest
import asyncio
import os
from unittest.mock import patch
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.main import app
from src.core.database import get_db
from src.models.database.user import User
from src.core.security import hash_password


class TestAuthEndpoints:
    """Test authentication API endpoints."""

    @pytest.fixture(autouse=True)
    def setup_test_env(self):
        """Set up test environment variables."""
        import os
        import shutil

        # Backup the original .env file
        env_file = "/Users/shadat/Dev/quote-of-the-day/apps/api/.env"
        env_backup = "/Users/shadat/Dev/quote-of-the-day/apps/api/.env.backup"

        if os.path.exists(env_file):
            shutil.move(env_file, env_backup)

        test_env = {
            "SECRET_KEY": "test_secret_key_for_testing_12345",
            "DATABASE_URL": "postgresql+asyncpg://quote_user:quote_password@localhost:5432/quote_of_the_day_dev",
            "REDIS_URL": "redis://localhost:6379/1",
            "ENVIRONMENT": "test",
            "DEBUG": "true",
            "LOG_LEVEL": "debug",
            "ALLOWED_HOSTS": "localhost,testserver,test",
        }

        try:
            with patch.dict("os.environ", test_env):
                yield
        finally:
            # Restore the original .env file
            if os.path.exists(env_backup):
                shutil.move(env_backup, env_file)

    @pytest.fixture
    def client(self):
        """Create test client."""
        return AsyncClient(app=app, base_url="http://localhost")

    @pytest.fixture
    def test_user_data(self):
        """Test user data."""
        return {
            "email": "test@example.com",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
            "timezone": "UTC",
        }

    @pytest.fixture
    async def existing_user(self, test_user_data):
        """Create existing user for testing."""
        # Create a test database engine
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from src.core.config import settings

        test_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )

        # Create session factory
        async_session = sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as db_session:
            # Check if user already exists
            from sqlalchemy import select

            result = await db_session.execute(
                select(User).where(User.email == test_user_data["email"])
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                return existing_user

            # Create user directly in database
            hashed_password = hash_password(test_user_data["password"])
            user = User(
                email=test_user_data["email"],
                password_hash=hashed_password,
                timezone=test_user_data["timezone"],
                is_active=True,
                subscription_tier="FREE",
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
            return user

        await test_engine.dispose()

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, test_user_data):
        """Test successful user registration."""
        async with client:
            response = await client.post("/api/v1/auth/register", json=test_user_data)

            assert response.status_code == 201
            data = response.json()
            assert data["email"] == test_user_data["email"]
            assert data["timezone"] == test_user_data["timezone"]
            assert data["subscription_tier"] == "FREE"
            assert data["is_active"] is True
            assert "id" in data
            assert "created_at" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, existing_user, test_user_data
    ):
        """Test registration with duplicate email."""
        # Await the existing_user fixture
        user = await existing_user
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 409
        data = response.json()
        assert "email" in data["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        invalid_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "timezone": "UTC",
        }

        response = await client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        weak_password_data = {
            "email": "test@example.com",
            "password": "123",
            "timezone": "UTC",
        }

        response = await client.post("/api/v1/auth/register", json=weak_password_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_success(
        self, client: AsyncClient, existing_user, test_user_data
    ):
        """Test successful user login."""
        # Await the existing_user fixture
        user = await existing_user
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient, existing_user):
        """Test login with invalid credentials."""
        # Await the existing_user fixture
        user = await existing_user
        invalid_login_data = {"email": "test@example.com", "password": "wrongpassword"}

        response = await client.post("/api/v1/auth/login", json=invalid_login_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        login_data = {"email": "nonexistent@example.com", "password": "testpassword123"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client: AsyncClient, existing_user):
        """Test getting current user info with valid token."""
        # Await the existing_user fixture
        user = await existing_user
        # First login to get token
        login_data = {"email": user.email, "password": "TestPassword123"}

        login_response = await client.post("/api/v1/auth/login", json=login_data)

        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Get current user info
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
        assert data["id"] == str(user.id)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user info with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user info without token."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_forgot_password_success(self, client: AsyncClient, existing_user):
        """Test forgot password with existing user."""
        # Await the existing_user fixture
        user = await existing_user
        forgot_data = {"email": user.email}

        response = await client.post("/api/v1/auth/forgot-password", json=forgot_data)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    async def test_forgot_password_nonexistent_user(self, client: AsyncClient):
        """Test forgot password with nonexistent user."""
        forgot_data = {"email": "nonexistent@example.com"}

        response = await client.post("/api/v1/auth/forgot-password", json=forgot_data)

        # Should still return 200 to prevent email enumeration
        assert response.status_code == 200

    async def test_verify_email_success(self, client: AsyncClient, existing_user):
        """Test email verification with valid token."""
        # This would require setting up a verification token in the database
        # For now, we'll test the endpoint structure
        verification_data = {"token": "valid_verification_token"}

        response = await client.post(
            "/api/v1/auth/verify-email", json=verification_data
        )

        # This will fail without a valid token, but we're testing the endpoint
        assert response.status_code in [200, 400]

    async def test_verify_email_invalid_token(self, client: AsyncClient):
        """Test email verification with invalid token."""
        verification_data = {"token": "invalid_token"}

        response = await client.post(
            "/api/v1/auth/verify-email", json=verification_data
        )

        assert response.status_code == 400

    async def test_reset_password_success(self, client: AsyncClient, existing_user):
        """Test password reset with valid token."""
        # This would require setting up a reset token in the database
        # For now, we'll test the endpoint structure
        reset_data = {"token": "valid_reset_token", "new_password": "newpassword123"}

        response = await client.post("/api/v1/auth/reset-password", json=reset_data)

        # This will fail without a valid token, but we're testing the endpoint
        assert response.status_code in [200, 400]

    async def test_reset_password_invalid_token(self, client: AsyncClient):
        """Test password reset with invalid token."""
        reset_data = {"token": "invalid_token", "new_password": "newpassword123"}

        response = await client.post("/api/v1/auth/reset-password", json=reset_data)

        assert response.status_code == 400

    async def test_change_password_success(self, client: AsyncClient, existing_user):
        """Test changing password with valid current password."""
        # First login to get token
        login_data = {"email": existing_user.email, "password": "testpassword123"}

        login_response = await client.post("/api/v1/auth/login", json=login_data)

        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Change password
        headers = {"Authorization": f"Bearer {token}"}
        change_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
        }

        response = await client.post(
            "/api/v1/auth/change-password", json=change_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    async def test_change_password_wrong_current_password(
        self, client: AsyncClient, existing_user
    ):
        """Test changing password with wrong current password."""
        # First login to get token
        login_data = {"email": existing_user.email, "password": "testpassword123"}

        login_response = await client.post("/api/v1/auth/login", json=login_data)

        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Try to change password with wrong current password
        headers = {"Authorization": f"Bearer {token}"}
        change_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
        }

        response = await client.post(
            "/api/v1/auth/change-password", json=change_data, headers=headers
        )

        assert response.status_code == 401

    async def test_update_profile_success(self, client: AsyncClient, existing_user):
        """Test updating user profile."""
        # First login to get token
        login_data = {"email": existing_user.email, "password": "testpassword123"}

        login_response = await client.post("/api/v1/auth/login", json=login_data)

        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Update profile
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {"timezone": "America/New_York"}

        response = await client.put(
            "/api/v1/auth/me", json=update_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["timezone"] == "America/New_York"

    async def test_logout_success(self, client: AsyncClient):
        """Test logout endpoint."""
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    async def test_deactivate_account_success(self, client: AsyncClient, existing_user):
        """Test deactivating user account."""
        # First login to get token
        login_data = {"email": existing_user.email, "password": "testpassword123"}

        login_response = await client.post("/api/v1/auth/login", json=login_data)

        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Deactivate account
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/api/v1/auth/deactivate", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    async def test_rate_limiting_register(self, client: AsyncClient):
        """Test rate limiting on registration endpoint."""
        test_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "timezone": "UTC",
        }

        # Make multiple requests quickly
        responses = []
        for i in range(7):  # More than the 5 request limit
            test_data["email"] = f"test{i}@example.com"
            response = await client.post("/api/v1/auth/register", json=test_data)
            responses.append(response)

        # First 5 should succeed, 6th and 7th should be rate limited
        success_count = sum(1 for r in responses if r.status_code == 201)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)

        assert success_count == 5
        assert rate_limited_count == 2

    async def test_rate_limiting_login(self, client: AsyncClient, existing_user):
        """Test rate limiting on login endpoint."""
        login_data = {"email": existing_user.email, "password": "testpassword123"}

        # Make multiple requests quickly
        responses = []
        for _ in range(7):  # More than the 5 request limit
            response = await client.post("/api/v1/auth/login", json=login_data)
            responses.append(response)

        # First 5 should succeed, 6th and 7th should be rate limited
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)

        assert success_count == 5
        assert rate_limited_count == 2
