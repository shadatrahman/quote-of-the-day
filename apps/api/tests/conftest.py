"""
Shared pytest fixtures and configuration for all tests.
"""

import pytest
import asyncio
import os
from unittest.mock import patch
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import application components
from src.main import app
from src.core.config import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with safe defaults."""
    test_env = {
        "SECRET_KEY": "test_secret_key_for_testing_12345",
        "DATABASE_URL": "postgresql+asyncpg://quote_user:quote_password@localhost:5432/quote_of_the_day_dev",
        "REDIS_URL": "redis://localhost:6379/1",
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "LOG_LEVEL": "debug",
        "ALLOWED_HOSTS": "localhost,testserver,test",
    }

    with patch.dict("os.environ", test_env):
        return Settings()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests."""
    with patch("src.main.db_manager.get_session") as mock:
        yield mock


@pytest.fixture
def mock_cache():
    """Mock cache manager for unit tests."""
    with patch("src.main.cache_manager") as mock:
        mock.ping.return_value = True
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = True
        yield mock


@pytest.fixture
def mock_logger():
    """Mock logger for unit tests."""
    with patch("src.main.logger") as mock:
        yield mock


@pytest.fixture
def mock_metrics():
    """Mock metrics collector for unit tests."""
    with patch("src.main.metrics") as mock:
        mock.get_metrics.return_value = {"test_metric": 1.0}
        yield mock


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment after each test to prevent contamination."""
    # Store original environment
    original_env = os.environ.copy()

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_health_response():
    """Sample health check response for testing."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "test",
        "checks": {"database": "healthy", "redis": "healthy"},
    }


@pytest.fixture
def sample_metrics_response():
    """Sample metrics response for testing."""
    return {
        "metrics": {
            "requests_total": 100,
            "response_time_avg": 0.5,
            "active_connections": 10,
        },
        "system": {"environment": "test", "version": "1.0.0"},
    }


# Test data fixtures
@pytest.fixture
def valid_cors_origins():
    """Valid CORS origins for testing."""
    return ["http://localhost:3000", "https://app.example.com"]


@pytest.fixture
def valid_allowed_hosts():
    """Valid allowed hosts for testing."""
    return ["localhost", "api.example.com"]


# Database test fixtures
@pytest.fixture
def mock_successful_db_query():
    """Mock successful database query."""
    with patch("src.core.database.db_manager") as mock:
        # Mock async context manager behavior
        mock_session = mock.return_value
        mock_session.__aenter__.return_value.execute.return_value.fetchone.return_value = (
            1,
        )
        yield mock


@pytest.fixture
def mock_failed_db_connection():
    """Mock failed database connection."""
    with patch("src.core.database.db_manager.get_session") as mock:
        mock.side_effect = Exception("Database connection failed")
        yield mock


# Redis test fixtures
@pytest.fixture
def mock_successful_redis():
    """Mock successful Redis operations."""
    with patch("src.core.cache.cache_manager") as mock:
        mock.ping.return_value = True
        mock.get.return_value = "test_value"
        mock.set.return_value = True
        mock.delete.return_value = True
        yield mock


@pytest.fixture
def mock_failed_redis():
    """Mock failed Redis connection."""
    with patch("src.core.cache.cache_manager") as mock:
        mock.ping.side_effect = Exception("Redis connection failed")
        yield mock


# Configuration test fixtures
@pytest.fixture
def minimal_config_env():
    """Minimal environment configuration for testing."""
    return {
        "SECRET_KEY": "test_secret_key_minimum",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
        "REDIS_URL": "redis://localhost:6379/0",
    }


@pytest.fixture
def full_config_env():
    """Full environment configuration for testing."""
    return {
        "SECRET_KEY": "test_secret_key_full_config",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
        "REDIS_URL": "redis://localhost:6379/0",
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "LOG_LEVEL": "debug",
        "API_HOST": "127.0.0.1",
        "API_PORT": "9000",
        "ALLOWED_ORIGINS": "http://localhost:3000,https://app.example.com",
        "ALLOWED_HOSTS": "localhost,api.example.com,testserver,test",
        "AWS_REGION": "us-west-2",
        "SENTRY_DSN": "https://test@sentry.io/12345",
    }


# Async test helpers
@pytest.fixture
async def async_mock_session():
    """Async mock database session."""
    from unittest.mock import AsyncMock

    session = AsyncMock()
    session.execute.return_value.fetchone.return_value = (1,)
    return session


# Cleanup fixtures
@pytest.fixture(scope="function", autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Any cleanup logic can go here
    # For now, this is just a placeholder


# Markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "smoke: Basic smoke tests")
