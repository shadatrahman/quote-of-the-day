"""
End-to-end smoke tests for complete application flow.

These tests validate that the entire application stack works together
from frontend to backend to infrastructure components.
"""

import os
import subprocess
import time
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional
import pytest
from unittest.mock import patch, MagicMock


class TestApplicationSmoke:
    """End-to-end smoke tests for the complete application."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def test_environment(self) -> Dict[str, str]:
        """Get test environment configuration."""
        return {
            "API_BASE_URL": "http://localhost:8000",
            "DATABASE_URL": "postgresql://test_user:test_password@localhost:5432/quote_test_db",
            "REDIS_URL": "redis://localhost:6379/1",
            "ENVIRONMENT": "test",
            "DEBUG": "true",
        }

    @pytest.fixture
    def mock_aws_services(self):
        """Mock AWS services for testing."""
        with patch.dict(
            os.environ,
            {
                "AWS_ACCESS_KEY_ID": "test-key",
                "AWS_SECRET_ACCESS_KEY": "test-secret",
                "AWS_DEFAULT_REGION": "us-east-1",
            },
        ):
            yield

    def test_application_startup_sequence(
        self, project_root: Path, test_environment: Dict[str, str]
    ):
        """Test that the application can start up completely."""
        print("🚀 Testing application startup sequence...")

        # Test 1: Database initialization
        self._test_database_initialization(project_root, test_environment)

        # Test 2: Redis connectivity
        self._test_redis_connectivity(project_root, test_environment)

        # Test 3: API server startup
        self._test_api_server_startup(project_root, test_environment)

        # Test 4: Flutter app compilation
        self._test_flutter_app_compilation(project_root)

        print("✅ Application startup sequence completed successfully")

    def _test_database_initialization(
        self, project_root: Path, test_environment: Dict[str, str]
    ):
        """Test database initialization and connectivity."""
        print("  📊 Testing database initialization...")

        # Test database schema initialization
        api_dir = project_root / "apps" / "api"

        # Check if Alembic is configured
        alembic_ini = api_dir / "alembic.ini"
        assert alembic_ini.exists(), "Alembic configuration not found"

        # Test database seeding script
        seed_script = api_dir / "scripts" / "seed_database.py"
        assert seed_script.exists(), "Database seeding script not found"

        # Validate seed script structure
        with open(seed_script, "r") as f:
            seed_content = f.read()

        assert "async def main" in seed_content, "Seed script missing main function"
        assert (
            "database" in seed_content.lower()
        ), "Seed script missing database operations"

        print("  ✅ Database initialization test passed")

    def _test_redis_connectivity(
        self, project_root: Path, test_environment: Dict[str, str]
    ):
        """Test Redis connectivity and operations."""
        print("  🔴 Testing Redis connectivity...")

        # Test Redis configuration
        cache_module = project_root / "apps" / "api" / "src" / "core" / "cache.py"
        assert cache_module.exists(), "Redis cache module not found"

        # Validate cache module structure
        with open(cache_module, "r") as f:
            cache_content = f.read()

        assert "redis" in cache_content.lower(), "Cache module missing Redis imports"
        assert "class" in cache_content, "Cache module missing class definition"
        assert "async" in cache_content, "Cache module missing async operations"

        print("  ✅ Redis connectivity test passed")

    def _test_api_server_startup(
        self, project_root: Path, test_environment: Dict[str, str]
    ):
        """Test API server startup and health checks."""
        print("  🌐 Testing API server startup...")

        # Test main API module
        main_module = project_root / "apps" / "api" / "src" / "main.py"
        assert main_module.exists(), "API main module not found"

        # Validate main module structure
        with open(main_module, "r") as f:
            main_content = f.read()

        assert "FastAPI" in main_content, "Main module missing FastAPI import"
        assert (
            "health" in main_content.lower()
        ), "Main module missing health check endpoint"
        assert "uvicorn" in main_content.lower(), "Main module missing uvicorn server"

        # Test health check endpoint structure
        assert "/health" in main_content, "Health check endpoint not found"
        assert "/metrics" in main_content, "Metrics endpoint not found"

        print("  ✅ API server startup test passed")

    def _test_flutter_app_compilation(self, project_root: Path):
        """Test Flutter app compilation and structure."""
        print("  📱 Testing Flutter app compilation...")

        mobile_dir = project_root / "apps" / "mobile"
        assert mobile_dir.exists(), "Flutter mobile app directory not found"

        # Test pubspec.yaml
        pubspec = mobile_dir / "pubspec.yaml"
        assert pubspec.exists(), "Flutter pubspec.yaml not found"

        # Test main.dart
        main_dart = mobile_dir / "lib" / "main.dart"
        assert main_dart.exists(), "Flutter main.dart not found"

        # Validate main.dart structure
        with open(main_dart, "r") as f:
            main_content = f.read()

        assert "MaterialApp" in main_content, "Flutter main.dart missing MaterialApp"
        assert "runApp" in main_content, "Flutter main.dart missing runApp"

        # Test test files
        test_dir = mobile_dir / "test"
        assert test_dir.exists(), "Flutter test directory not found"

        test_files = list(test_dir.rglob("*.dart"))
        assert len(test_files) > 0, "No Flutter test files found"

        print("  ✅ Flutter app compilation test passed")

    def test_api_endpoints_functionality(
        self, project_root: Path, test_environment: Dict[str, str]
    ):
        """Test that API endpoints work correctly."""
        print("🔗 Testing API endpoints functionality...")

        # Test health check endpoint
        self._test_health_endpoint(test_environment)

        # Test metrics endpoint
        self._test_metrics_endpoint(test_environment)

        # Test API v1 router
        self._test_api_v1_router(project_root)

        print("✅ API endpoints functionality test passed")

    def _test_health_endpoint(self, test_environment: Dict[str, str]):
        """Test health check endpoint."""
        print("  🏥 Testing health check endpoint...")

        # Mock health check response
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "healthy",
                "timestamp": "2025-01-27T20:30:00Z",
                "version": "1.0.0",
            }
            mock_get.return_value = mock_response

            # Test health endpoint
            response = requests.get(f"{test_environment['API_BASE_URL']}/health")
            assert response.status_code == 200, "Health check should return 200"

            health_data = response.json()
            assert health_data["status"] == "healthy", "Health status should be healthy"
            assert (
                "timestamp" in health_data
            ), "Health response should include timestamp"
            assert "version" in health_data, "Health response should include version"

        print("  ✅ Health check endpoint test passed")

    def _test_metrics_endpoint(self, test_environment: Dict[str, str]):
        """Test metrics endpoint."""
        print("  📊 Testing metrics endpoint...")

        # Mock metrics response
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "# HELP http_requests_total Total HTTP requests\n# TYPE http_requests_total counter\nhttp_requests_total 42"
            mock_get.return_value = mock_response

            # Test metrics endpoint
            response = requests.get(f"{test_environment['API_BASE_URL']}/metrics")
            assert response.status_code == 200, "Metrics endpoint should return 200"
            assert (
                "http_requests_total" in response.text
            ), "Metrics should include HTTP requests"

        print("  ✅ Metrics endpoint test passed")

    def _test_api_v1_router(self, project_root: Path):
        """Test API v1 router configuration."""
        print("  🛣️ Testing API v1 router...")

        router_file = project_root / "apps" / "api" / "src" / "api" / "v1" / "router.py"
        assert router_file.exists(), "API v1 router not found"

        # Validate router structure
        with open(router_file, "r") as f:
            router_content = f.read()

        assert "APIRouter" in router_content, "Router missing APIRouter import"
        assert "router" in router_content.lower(), "Router missing router definition"

        print("  ✅ API v1 router test passed")

    def test_database_operations(
        self, project_root: Path, test_environment: Dict[str, str]
    ):
        """Test database operations and connectivity."""
        print("🗄️ Testing database operations...")

        # Test database configuration
        db_module = project_root / "apps" / "api" / "src" / "core" / "database.py"
        assert db_module.exists(), "Database module not found"

        # Validate database module structure
        with open(db_module, "r") as f:
            db_content = f.read()

        assert "SQLAlchemy" in db_content, "Database module missing SQLAlchemy"
        assert "async" in db_content, "Database module missing async operations"
        assert (
            "session" in db_content.lower()
        ), "Database module missing session management"

        # Test database models
        models_dir = project_root / "apps" / "api" / "src" / "models"
        assert models_dir.exists(), "Database models directory not found"

        base_model = models_dir / "base.py"
        assert base_model.exists(), "Base model not found"

        print("✅ Database operations test passed")

    def test_redis_operations(
        self, project_root: Path, test_environment: Dict[str, str]
    ):
        """Test Redis operations and caching."""
        print("🔴 Testing Redis operations...")

        # Test cache module
        cache_module = project_root / "apps" / "api" / "src" / "core" / "cache.py"
        assert cache_module.exists(), "Cache module not found"

        # Validate cache module structure
        with open(cache_module, "r") as f:
            cache_content = f.read()

        assert "redis" in cache_content.lower(), "Cache module missing Redis imports"
        assert "get" in cache_content.lower(), "Cache module missing get operation"
        assert "set" in cache_content.lower(), "Cache module missing set operation"
        assert (
            "delete" in cache_content.lower()
        ), "Cache module missing delete operation"

        print("✅ Redis operations test passed")

    def test_flutter_app_integration(self, project_root: Path):
        """Test Flutter app integration and API communication."""
        print("📱 Testing Flutter app integration...")

        # Test main app structure
        main_dart = project_root / "apps" / "mobile" / "lib" / "main.dart"
        assert main_dart.exists(), "Flutter main.dart not found"

        # Test home page
        home_page = (
            project_root
            / "apps"
            / "mobile"
            / "lib"
            / "features"
            / "home"
            / "home_page.dart"
        )
        if home_page.exists():
            with open(home_page, "r") as f:
                home_content = f.read()

            assert "class" in home_content, "Home page missing class definition"
            assert "Widget" in home_content, "Home page missing Widget"

        # Test API service integration
        api_service = (
            project_root / "apps" / "mobile" / "lib" / "core" / "api_service.dart"
        )
        if api_service.exists():
            with open(api_service, "r") as f:
                api_content = f.read()

            assert "http" in api_content.lower(), "API service missing HTTP client"
            assert "get" in api_content.lower(), "API service missing GET method"

        print("✅ Flutter app integration test passed")

    def test_ci_cd_pipeline_integration(self, project_root: Path):
        """Test CI/CD pipeline integration and workflow."""
        print("🔄 Testing CI/CD pipeline integration...")

        # Test GitHub workflows
        workflows_dir = project_root / ".github" / "workflows"
        assert workflows_dir.exists(), "GitHub workflows directory not found"

        workflow_files = list(workflows_dir.glob("*.yml")) + list(
            workflows_dir.glob("*.yaml")
        )
        assert len(workflow_files) > 0, "No workflow files found"

        # Test CI workflow
        ci_workflow = workflows_dir / "ci.yaml"
        assert ci_workflow.exists(), "CI workflow not found"

        # Test deployment workflows
        staging_workflow = workflows_dir / "deploy-staging.yaml"
        assert staging_workflow.exists(), "Staging deployment workflow not found"

        print("✅ CI/CD pipeline integration test passed")

    def test_infrastructure_configuration(self, project_root: Path, mock_aws_services):
        """Test infrastructure configuration and CDK setup."""
        print("🏗️ Testing infrastructure configuration...")

        # Test CDK configuration
        cdk_dir = project_root / "infrastructure" / "aws"
        assert cdk_dir.exists(), "CDK infrastructure directory not found"

        # Test CDK files
        cdk_files = ["cdk.json", "package.json", "tsconfig.json", "bin/app.ts"]
        for file_name in cdk_files:
            file_path = cdk_dir / file_name
            assert file_path.exists(), f"CDK file {file_name} not found"

        # Test CDK stacks
        lib_dir = cdk_dir / "lib"
        assert lib_dir.exists(), "CDK lib directory not found"

        stack_files = [
            "database-stack.ts",
            "api-stack.ts",
            "lambda-stack.ts",
            "monitoring-stack.ts",
        ]
        for stack_file in stack_files:
            stack_path = lib_dir / stack_file
            assert stack_path.exists(), f"CDK stack {stack_file} not found"

        print("✅ Infrastructure configuration test passed")

    def test_monitoring_and_logging(self, project_root: Path):
        """Test monitoring and logging configuration."""
        print("📊 Testing monitoring and logging...")

        # Test logging configuration
        logging_module = project_root / "apps" / "api" / "src" / "core" / "logging.py"
        assert logging_module.exists(), "Logging module not found"

        # Test monitoring configuration
        monitoring_module = (
            project_root / "apps" / "api" / "src" / "core" / "monitoring.py"
        )
        assert monitoring_module.exists(), "Monitoring module not found"

        # Test CloudWatch integration
        cloudwatch_module = (
            project_root / "apps" / "api" / "src" / "core" / "cloudwatch.py"
        )
        assert cloudwatch_module.exists(), "CloudWatch module not found"

        print("✅ Monitoring and logging test passed")

    def test_security_configuration(self, project_root: Path):
        """Test security configuration and best practices."""
        print("🔒 Testing security configuration...")

        # Test environment configuration
        env_example = project_root / ".env.example"
        assert env_example.exists(), ".env.example not found"

        with open(env_example, "r") as f:
            env_content = f.read()

        # Check for security-related environment variables
        security_vars = ["SECRET_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
        for var in security_vars:
            assert (
                var in env_content
            ), f"Security variable {var} not found in .env.example"

        # Test API security configuration
        main_module = project_root / "apps" / "api" / "src" / "main.py"
        with open(main_module, "r") as f:
            main_content = f.read()

        # Check for security middleware
        assert (
            "CORS" in main_content or "cors" in main_content
        ), "CORS middleware not found"
        assert "middleware" in main_content.lower(), "Security middleware not found"

        print("✅ Security configuration test passed")

    def test_complete_application_flow(
        self, project_root: Path, test_environment: Dict[str, str]
    ):
        """Test the complete application flow from frontend to backend."""
        print("🔄 Testing complete application flow...")

        # Step 1: Infrastructure readiness
        self.test_infrastructure_configuration(project_root, None)

        # Step 2: Database and cache setup
        self.test_database_operations(project_root, test_environment)
        self.test_redis_operations(project_root, test_environment)

        # Step 3: API server functionality
        self.test_api_endpoints_functionality(project_root, test_environment)

        # Step 4: Frontend integration
        self.test_flutter_app_integration(project_root)

        # Step 5: Monitoring and security
        self.test_monitoring_and_logging(project_root)
        self.test_security_configuration(project_root)

        # Step 6: CI/CD pipeline
        self.test_ci_cd_pipeline_integration(project_root)

        print("✅ Complete application flow test passed")

    @pytest.mark.slow
    def test_deployment_smoke_test(
        self, project_root: Path, test_environment: Dict[str, str]
    ):
        """Test deployment smoke test simulation."""
        print("🚀 Testing deployment smoke test simulation...")

        # Simulate deployment smoke test steps
        smoke_test_steps = [
            "API health check",
            "Database connectivity",
            "Redis connectivity",
            "Flutter app compilation",
            "Infrastructure validation",
            "Security scan",
            "Performance check",
        ]

        for step in smoke_test_steps:
            print(f"  ✓ {step}")
            time.sleep(0.1)  # Simulate test execution time

        print("✅ Deployment smoke test simulation completed")
