"""
Integration tests for CI/CD pipeline validation.

These tests validate that the CI/CD pipeline components work correctly
and can be executed in a test environment.
"""

import os
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any
import pytest


class TestCIPipeline:
    """Test CI/CD pipeline components and workflows."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def workflow_files(self, project_root: Path) -> Dict[str, Path]:
        """Get all GitHub workflow files."""
        workflows_dir = project_root / ".github" / "workflows"
        return {
            "ci": workflows_dir / "ci.yaml",
            "deploy_staging": workflows_dir / "deploy-staging.yaml",
            "deploy_prod": workflows_dir / "deploy-prod.yaml",
            "security_scan": workflows_dir / "security-scan.yaml",
        }

    def test_workflow_files_exist(self, workflow_files: Dict[str, Path]):
        """Test that all required workflow files exist."""
        for name, path in workflow_files.items():
            assert path.exists(), f"Workflow file {name} not found at {path}"

    def test_ci_workflow_syntax(self, workflow_files: Dict[str, Path]):
        """Test that CI workflow YAML syntax is valid."""
        ci_workflow = workflow_files["ci"]
        with open(ci_workflow, "r") as f:
            workflow_data = yaml.safe_load(f)

        # Validate required fields
        assert "name" in workflow_data
        assert "on" in workflow_data
        assert "jobs" in workflow_data

        # Validate job structure
        jobs = workflow_data["jobs"]
        required_jobs = [
            "test-backend",
            "test-frontend",
            "test-shared-types",
            "security-scan",
        ]
        for job in required_jobs:
            assert job in jobs, f"Required job {job} not found in CI workflow"

    def test_deploy_staging_workflow_syntax(self, workflow_files: Dict[str, Path]):
        """Test that staging deployment workflow YAML syntax is valid."""
        staging_workflow = workflow_files["deploy_staging"]
        with open(staging_workflow, "r") as f:
            workflow_data = yaml.safe_load(f)

        # Validate required fields
        assert "name" in workflow_data
        assert "on" in workflow_data
        assert "jobs" in workflow_data

        # Validate job structure
        jobs = workflow_data["jobs"]
        required_jobs = [
            "check-tests",
            "deploy-infrastructure",
            "deploy-api",
            "run-smoke-tests",
        ]
        for job in required_jobs:
            assert job in jobs, f"Required job {job} not found in staging workflow"

    def test_environment_variables_consistency(self, project_root: Path):
        """Test that environment variables are consistent across workflows."""
        env_example = project_root / ".env.example"
        assert env_example.exists(), ".env.example file not found"

        # Read .env.example
        with open(env_example, "r") as f:
            env_content = f.read()

        # Check for required environment variables
        required_vars = [
            "DATABASE_URL",
            "REDIS_URL",
            "SECRET_KEY",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_REGION",
        ]

        for var in required_vars:
            assert (
                var in env_content
            ), f"Required environment variable {var} not found in .env.example"

    def test_docker_compose_configuration(self, project_root: Path):
        """Test that docker-compose.yml is properly configured."""
        docker_compose = project_root / "docker-compose.yml"
        assert docker_compose.exists(), "docker-compose.yml not found"

        with open(docker_compose, "r") as f:
            compose_data = yaml.safe_load(f)

        # Validate services
        assert "services" in compose_data
        services = compose_data["services"]

        # Check for required services
        required_services = ["postgres", "redis"]
        for service in required_services:
            assert (
                service in services
            ), f"Required service {service} not found in docker-compose.yml"

    def test_package_json_scripts(self, project_root: Path):
        """Test that package.json has required scripts for CI/CD."""
        package_json = project_root / "package.json"
        assert package_json.exists(), "package.json not found"

        with open(package_json, "r") as f:
            package_data = yaml.safe_load(f)

        # Validate scripts
        assert "scripts" in package_data
        scripts = package_data["scripts"]

        # Check for required scripts
        required_scripts = ["dev", "test", "lint", "build"]
        for script in required_scripts:
            assert (
                script in scripts
            ), f"Required script {script} not found in package.json"

    def test_flutter_dependencies(self, project_root: Path):
        """Test that Flutter dependencies are properly configured."""
        pubspec = project_root / "apps" / "mobile" / "pubspec.yaml"
        assert pubspec.exists(), "Flutter pubspec.yaml not found"

        with open(pubspec, "r") as f:
            pubspec_data = yaml.safe_load(f)

        # Validate dependencies
        assert "dependencies" in pubspec_data
        assert "dev_dependencies" in pubspec_data

    def test_python_dependencies(self, project_root: Path):
        """Test that Python dependencies are properly configured."""
        requirements = project_root / "apps" / "api" / "requirements.txt"
        assert requirements.exists(), "Python requirements.txt not found"

        with open(requirements, "r") as f:
            requirements_content = f.read()

        # Check for required packages
        required_packages = ["fastapi", "uvicorn", "sqlalchemy", "redis", "pytest"]
        for package in required_packages:
            assert (
                package in requirements_content
            ), f"Required package {package} not found in requirements.txt"

    def test_cdk_infrastructure_configuration(self, project_root: Path):
        """Test that CDK infrastructure is properly configured."""
        cdk_dir = project_root / "infrastructure" / "aws"
        assert cdk_dir.exists(), "CDK infrastructure directory not found"

        # Check for required CDK files
        required_files = ["cdk.json", "package.json", "tsconfig.json"]
        for file in required_files:
            file_path = cdk_dir / file
            assert file_path.exists(), f"Required CDK file {file} not found"

        # Check for stack files
        lib_dir = cdk_dir / "lib"
        assert lib_dir.exists(), "CDK lib directory not found"

        required_stacks = [
            "database-stack.ts",
            "api-stack.ts",
            "lambda-stack.ts",
            "monitoring-stack.ts",
        ]
        for stack in required_stacks:
            stack_path = lib_dir / stack
            assert stack_path.exists(), f"Required CDK stack {stack} not found"

    def test_security_scanning_configuration(self, project_root: Path):
        """Test that security scanning is properly configured."""
        security_workflow = (
            project_root / ".github" / "workflows" / "security-scan.yaml"
        )
        assert security_workflow.exists(), "Security scan workflow not found"

        with open(security_workflow, "r") as f:
            workflow_data = yaml.safe_load(f)

        # Validate security scanning steps
        jobs = workflow_data.get("jobs", {})
        assert "security-scan" in jobs, "Security scan job not found"

        security_job = jobs["security-scan"]
        steps = security_job.get("steps", [])

        # Check for Trivy and CodeQL steps
        step_names = [step.get("name", "") for step in steps]
        assert any(
            "Trivy" in name for name in step_names
        ), "Trivy security scanning not found"
        assert any("CodeQL" in name for name in step_names), "CodeQL analysis not found"

    def test_coverage_reporting_configuration(self, project_root: Path):
        """Test that coverage reporting is properly configured."""
        ci_workflow = project_root / ".github" / "workflows" / "ci.yaml"

        with open(ci_workflow, "r") as f:
            workflow_data = yaml.safe_load(f)

        jobs = workflow_data.get("jobs", {})

        # Check backend coverage
        backend_job = jobs.get("test-backend", {})
        backend_steps = backend_job.get("steps", [])
        backend_step_names = [step.get("name", "") for step in backend_steps]
        assert any(
            "coverage" in name.lower() for name in backend_step_names
        ), "Backend coverage reporting not found"

        # Check frontend coverage
        frontend_job = jobs.get("test-frontend", {})
        frontend_steps = frontend_job.get("steps", [])
        frontend_step_names = [step.get("name", "") for step in frontend_steps]
        assert any(
            "coverage" in name.lower() for name in frontend_step_names
        ), "Frontend coverage reporting not found"

    def test_deployment_environment_configuration(self, project_root: Path):
        """Test that deployment environments are properly configured."""
        # Check staging deployment
        staging_workflow = (
            project_root / ".github" / "workflows" / "deploy-staging.yaml"
        )
        with open(staging_workflow, "r") as f:
            staging_data = yaml.safe_load(f)

        staging_jobs = staging_data.get("jobs", {})
        assert (
            "deploy-infrastructure" in staging_jobs
        ), "Staging infrastructure deployment not found"
        assert "deploy-api" in staging_jobs, "Staging API deployment not found"
        assert "run-smoke-tests" in staging_jobs, "Staging smoke tests not found"

        # Check production deployment
        prod_workflow = project_root / ".github" / "workflows" / "deploy-prod.yaml"
        if prod_workflow.exists():
            with open(prod_workflow, "r") as f:
                prod_data = yaml.safe_load(f)

            prod_jobs = prod_data.get("jobs", {})
            assert (
                "deploy-infrastructure" in prod_jobs
            ), "Production infrastructure deployment not found"
            assert "deploy-api" in prod_jobs, "Production API deployment not found"
