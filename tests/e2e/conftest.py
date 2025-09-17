"""
Configuration and fixtures for end-to-end tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict
import os


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def temp_project_dir(project_root: Path) -> Generator[Path, None, None]:
    """Create a temporary copy of the project for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "quote-of-the-day"
        shutil.copytree(project_root, temp_path)
        yield temp_path


@pytest.fixture
def test_environment() -> Dict[str, str]:
    """Get test environment configuration."""
    return {
        "API_BASE_URL": "http://localhost:8000",
        "DATABASE_URL": "postgresql://test_user:test_password@localhost:5432/quote_test_db",
        "REDIS_URL": "redis://localhost:6379/1",
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "SECRET_KEY": "test-secret-key-for-e2e-testing",
        "AWS_ACCESS_KEY_ID": "test-key",
        "AWS_SECRET_ACCESS_KEY": "test-secret",
        "AWS_DEFAULT_REGION": "us-east-1",
    }


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for testing."""
    with pytest.MonkeyPatch().context() as m:
        m.setenv("AWS_ACCESS_KEY_ID", "test-key")
        m.setenv("AWS_SECRET_ACCESS_KEY", "test-secret")
        m.setenv("AWS_DEFAULT_REGION", "us-east-1")
        m.setenv("CDK_DEFAULT_ACCOUNT", "123456789012")
        m.setenv("CDK_DEFAULT_REGION", "us-east-1")
        yield


@pytest.fixture
def mock_http_responses():
    """Mock HTTP responses for testing."""
    return {
        "health": {
            "status_code": 200,
            "json": {
                "status": "healthy",
                "timestamp": "2025-01-27T20:30:00Z",
                "version": "1.0.0",
            },
        },
        "metrics": {
            "status_code": 200,
            "text": "# HELP http_requests_total Total HTTP requests\n# TYPE http_requests_total counter\nhttp_requests_total 42",
        },
        "api_v1": {
            "status_code": 200,
            "json": {"message": "API v1 is working", "version": "1.0.0"},
        },
    }


@pytest.fixture
def mock_database_operations():
    """Mock database operations for testing."""
    return {"connection": True, "migration": True, "seed": True, "query": True}


@pytest.fixture
def mock_redis_operations():
    """Mock Redis operations for testing."""
    return {"connection": True, "get": "cached_value", "set": True, "delete": True}


@pytest.fixture(autouse=True)
def setup_test_environment(test_environment):
    """Set up test environment variables."""
    for key, value in test_environment.items():
        os.environ[key] = value
    yield
    # Cleanup is automatic when the test ends
