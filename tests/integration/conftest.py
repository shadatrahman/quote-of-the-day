"""
Configuration and fixtures for integration tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


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
def mock_github_workflow():
    """Mock GitHub workflow data for testing."""
    return {
        "name": "Test Workflow",
        "on": {"push": {"branches": ["main"]}},
        "jobs": {
            "test": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"name": "Checkout", "uses": "actions/checkout@v4"},
                    {"name": "Test", "run": "echo 'test'"},
                ],
            }
        },
    }


@pytest.fixture
def mock_cdk_outputs():
    """Mock CDK outputs for testing."""
    return {
        "QuoteApiStack-staging": {
            "ApiEndpoint": "https://api-staging.example.com",
            "ECSServiceName": "quote-api-staging",
            "ECSClusterName": "quote-cluster-staging",
        },
        "QuoteDatabaseStack-staging": {
            "DatabaseEndpoint": "db-staging.example.com",
            "RedisEndpoint": "redis-staging.example.com",
        },
    }
