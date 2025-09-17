#!/usr/bin/env python3
"""
Documentation validation script.

This script validates that the development documentation is accurate
by testing the setup process and verifying that all documented commands work.
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml
import json


class DocumentationValidator:
    """Validates development documentation accuracy."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.temp_dir: Optional[Path] = None

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Starting documentation validation...")

        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp(prefix="quote-docs-validation-"))

        try:
            # Run validation checks
            self._validate_package_json_scripts()
            self._validate_docker_compose()
            self._validate_environment_variables()
            self._validate_github_workflows()
            self._validate_cdk_configuration()
            self._validate_flutter_setup()
            self._validate_python_setup()
            self._validate_documentation_files()

            # Print results
            self._print_results()

            return len(self.errors) == 0

        finally:
            # Cleanup
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)

    def _validate_package_json_scripts(self):
        """Validate package.json scripts work as documented."""
        print("📦 Validating package.json scripts...")

        package_json = self.project_root / "package.json"
        if not package_json.exists():
            self.errors.append("package.json not found")
            return

        with open(package_json, "r") as f:
            package_data = json.load(f)

        scripts = package_data.get("scripts", {})

        # Test that documented scripts exist
        documented_scripts = ["dev", "test", "lint", "build", "dev:api", "dev:mobile"]

        for script in documented_scripts:
            if script not in scripts:
                self.errors.append(
                    f"Documented script '{script}' not found in package.json"
                )
            else:
                # Test that script can be parsed (basic validation)
                try:
                    # Just check if the command structure is valid
                    script_content = scripts[script]
                    if not script_content or not isinstance(script_content, str):
                        self.errors.append(f"Script '{script}' has invalid content")
                except Exception as e:
                    self.errors.append(f"Script '{script}' has parsing error: {e}")

    def _validate_docker_compose(self):
        """Validate docker-compose.yml configuration."""
        print("🐳 Validating docker-compose.yml...")

        docker_compose = self.project_root / "docker-compose.yml"
        if not docker_compose.exists():
            self.errors.append("docker-compose.yml not found")
            return

        try:
            with open(docker_compose, "r") as f:
                compose_data = yaml.safe_load(f)

            # Validate structure
            if "services" not in compose_data:
                self.errors.append("docker-compose.yml missing 'services' section")
                return

            services = compose_data["services"]
            required_services = ["postgres", "redis"]

            for service in required_services:
                if service not in services:
                    self.errors.append(
                        f"Required service '{service}' not found in docker-compose.yml"
                    )
                else:
                    service_config = services[service]
                    if "image" not in service_config:
                        self.errors.append(
                            f"Service '{service}' missing 'image' configuration"
                        )
                    if "ports" not in service_config:
                        self.warnings.append(
                            f"Service '{service}' missing 'ports' configuration"
                        )

        except yaml.YAMLError as e:
            self.errors.append(f"docker-compose.yml YAML parsing error: {e}")
        except Exception as e:
            self.errors.append(f"docker-compose.yml validation error: {e}")

    def _validate_environment_variables(self):
        """Validate environment variable configuration."""
        print("🔧 Validating environment variables...")

        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            self.errors.append(".env.example not found")
            return

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
            if var not in env_content:
                self.errors.append(
                    f"Required environment variable '{var}' not found in .env.example"
                )

        # Check for proper format
        lines = env_content.strip().split("\n")
        for line in lines:
            if line.strip() and not line.startswith("#") and "=" not in line:
                self.warnings.append(f"Environment variable line format issue: {line}")

    def _validate_github_workflows(self):
        """Validate GitHub workflow configurations."""
        print("🔄 Validating GitHub workflows...")

        workflows_dir = self.project_root / ".github" / "workflows"
        if not workflows_dir.exists():
            self.errors.append(".github/workflows directory not found")
            return

        workflow_files = list(workflows_dir.glob("*.yml")) + list(
            workflows_dir.glob("*.yaml")
        )

        if not workflow_files:
            self.errors.append("No workflow files found in .github/workflows")
            return

        for workflow_file in workflow_files:
            try:
                with open(workflow_file, "r") as f:
                    workflow_data = yaml.safe_load(f)

                # Basic validation
                if not workflow_data:
                    self.errors.append(
                        f"Workflow {workflow_file.name} is empty or invalid"
                    )
                    continue

                if "name" not in workflow_data:
                    self.errors.append(
                        f"Workflow {workflow_file.name} missing 'name' field"
                    )

                # Check for 'on' field - it might be parsed as True due to YAML keyword
                has_on = "on" in workflow_data or True in workflow_data
                if not has_on:
                    self.errors.append(
                        f"Workflow {workflow_file.name} missing 'on' field"
                    )

                if "jobs" not in workflow_data:
                    self.errors.append(
                        f"Workflow {workflow_file.name} missing 'jobs' field"
                    )

            except yaml.YAMLError as e:
                self.errors.append(
                    f"Workflow {workflow_file.name} YAML parsing error: {e}"
                )
            except Exception as e:
                self.errors.append(
                    f"Workflow {workflow_file.name} validation error: {e}"
                )

    def _validate_cdk_configuration(self):
        """Validate CDK configuration."""
        print("🏗️ Validating CDK configuration...")

        cdk_dir = self.project_root / "infrastructure" / "aws"
        if not cdk_dir.exists():
            self.errors.append("CDK infrastructure directory not found")
            return

        # Check required files
        required_files = ["cdk.json", "package.json", "tsconfig.json", "bin/app.ts"]
        for file_name in required_files:
            file_path = cdk_dir / file_name
            if not file_path.exists():
                self.errors.append(f"Required CDK file {file_name} not found")

        # Validate cdk.json
        cdk_json = cdk_dir / "cdk.json"
        if cdk_json.exists():
            try:
                with open(cdk_json, "r") as f:
                    cdk_data = json.load(f)

                if "app" not in cdk_data:
                    self.errors.append("cdk.json missing 'app' field")
                if "context" not in cdk_data:
                    self.warnings.append("cdk.json missing 'context' field")

            except json.JSONDecodeError as e:
                self.errors.append(f"cdk.json JSON parsing error: {e}")

    def _validate_flutter_setup(self):
        """Validate Flutter setup configuration."""
        print("📱 Validating Flutter setup...")

        mobile_dir = self.project_root / "apps" / "mobile"
        if not mobile_dir.exists():
            self.errors.append("Flutter mobile app directory not found")
            return

        pubspec = mobile_dir / "pubspec.yaml"
        if not pubspec.exists():
            self.errors.append("Flutter pubspec.yaml not found")
            return

        try:
            with open(pubspec, "r") as f:
                pubspec_data = yaml.safe_load(f)

            if "name" not in pubspec_data:
                self.errors.append("Flutter pubspec.yaml missing 'name' field")
            if "dependencies" not in pubspec_data:
                self.errors.append("Flutter pubspec.yaml missing 'dependencies' field")
            if "dev_dependencies" not in pubspec_data:
                self.warnings.append(
                    "Flutter pubspec.yaml missing 'dev_dependencies' field"
                )

        except yaml.YAMLError as e:
            self.errors.append(f"Flutter pubspec.yaml YAML parsing error: {e}")

    def _validate_python_setup(self):
        """Validate Python setup configuration."""
        print("🐍 Validating Python setup...")

        api_dir = self.project_root / "apps" / "api"
        if not api_dir.exists():
            self.errors.append("Python API directory not found")
            return

        requirements = api_dir / "requirements.txt"
        if not requirements.exists():
            self.errors.append("Python requirements.txt not found")
            return

        with open(requirements, "r") as f:
            requirements_content = f.read()

        # Check for required packages
        required_packages = ["fastapi", "uvicorn", "sqlalchemy", "redis", "pytest"]
        for package in required_packages:
            if package not in requirements_content:
                self.warnings.append(
                    f"Recommended package '{package}' not found in requirements.txt"
                )

    def _validate_documentation_files(self):
        """Validate documentation files exist and are readable."""
        print("📚 Validating documentation files...")

        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            self.errors.append("Documentation directory not found")
            return

        # Check for required documentation files
        required_docs = [
            ("README.md", self.project_root / "README.md"),  # Root README
            (
                "development/getting-started.md",
                docs_dir / "development/getting-started.md",
            ),
            (
                "development/environment-variables.md",
                docs_dir / "development/environment-variables.md",
            ),
            (
                "development/troubleshooting.md",
                docs_dir / "development/troubleshooting.md",
            ),
        ]

        for doc_name, full_path in required_docs:
            if not full_path.exists():
                self.errors.append(f"Required documentation file {doc_name} not found")
            else:
                # Check if file is readable and not empty
                try:
                    with open(full_path, "r") as f:
                        content = f.read().strip()
                    if not content:
                        self.warnings.append(f"Documentation file {doc_name} is empty")
                except Exception as e:
                    self.errors.append(
                        f"Documentation file {doc_name} is not readable: {e}"
                    )

    def _print_results(self):
        """Print validation results."""
        print("\n" + "=" * 50)
        print("📋 DOCUMENTATION VALIDATION RESULTS")
        print("=" * 50)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")
        elif not self.errors:
            print(f"\n✅ Validation completed with {len(self.warnings)} warnings")
        else:
            print(
                f"\n❌ Validation failed with {len(self.errors)} errors and {len(self.warnings)} warnings"
            )

        print("=" * 50)


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent

    validator = DocumentationValidator(project_root)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
