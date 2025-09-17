#!/usr/bin/env python3
"""
Comprehensive smoke test runner for the Quote of the Day application.

This script runs all smoke tests including unit, integration, and end-to-end tests
to validate the complete application functionality.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import json


class SmokeTestRunner:
    """Runs comprehensive smoke tests for the application."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: Dict[str, Any] = {
            "start_time": None,
            "end_time": None,
            "duration": None,
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
            },
        }

    def run_all_tests(self, verbose: bool = False, parallel: bool = False) -> bool:
        """Run all smoke tests."""
        print("🚀 Starting comprehensive smoke test suite...")
        self.results["start_time"] = time.time()

        try:
            # Run different test suites
            test_suites = [
                ("unit", self._run_unit_tests),
                ("integration", self._run_integration_tests),
                ("e2e", self._run_e2e_tests),
                ("documentation", self._run_documentation_validation),
            ]

            all_passed = True

            for suite_name, test_function in test_suites:
                print(f"\n📋 Running {suite_name} tests...")
                suite_result = test_function(verbose, parallel)
                self.results["tests"][suite_name] = suite_result

                if not suite_result["success"]:
                    all_passed = False
                    print(f"❌ {suite_name} tests failed")
                else:
                    print(f"✅ {suite_name} tests passed")

            # Calculate summary
            self._calculate_summary()

            return all_passed

        finally:
            self.results["end_time"] = time.time()
            self.results["duration"] = (
                self.results["end_time"] - self.results["start_time"]
            )
            self._print_summary()

    def _run_unit_tests(self, verbose: bool, parallel: bool) -> Dict[str, Any]:
        """Run unit tests."""
        # Backend unit tests
        backend_result = self._run_pytest(
            "apps/api/tests/unit/", "Backend Unit Tests", verbose, parallel
        )

        # Frontend unit tests (Flutter)
        frontend_result = self._run_flutter_tests(
            "apps/mobile/test/unit/", "Frontend Unit Tests", verbose
        )

        return {
            "success": backend_result["success"] and frontend_result["success"],
            "backend": backend_result,
            "frontend": frontend_result,
        }

    def _run_integration_tests(self, verbose: bool, parallel: bool) -> Dict[str, Any]:
        """Run integration tests."""
        return self._run_pytest(
            "tests/integration/", "Integration Tests", verbose, parallel
        )

    def _run_e2e_tests(self, verbose: bool, parallel: bool) -> Dict[str, Any]:
        """Run end-to-end tests."""
        return self._run_pytest("tests/e2e/", "End-to-End Tests", verbose, parallel)

    def _run_documentation_validation(
        self, verbose: bool, parallel: bool
    ) -> Dict[str, Any]:
        """Run documentation validation."""
        script_path = self.project_root / "scripts" / "validate-documentation.py"

        if not script_path.exists():
            return {
                "success": False,
                "error": "Documentation validation script not found",
            }

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Documentation validation timed out"}
        except Exception as e:
            return {"success": False, "error": f"Documentation validation failed: {e}"}

    def _run_pytest(
        self, test_path: str, test_name: str, verbose: bool, parallel: bool
    ) -> Dict[str, Any]:
        """Run pytest tests."""
        full_path = self.project_root / test_path

        if not full_path.exists():
            return {"success": False, "error": f"Test path {test_path} not found"}

        cmd = [sys.executable, "-m", "pytest", str(full_path)]

        if verbose:
            cmd.append("-v")

        if parallel:
            cmd.extend(["-n", "auto"])

        cmd.extend(["--tb=short", "--disable-warnings"])

        try:
            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, timeout=600
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"{test_name} timed out"}
        except Exception as e:
            return {"success": False, "error": f"{test_name} failed: {e}"}

    def _run_flutter_tests(
        self, test_path: str, test_name: str, verbose: bool
    ) -> Dict[str, Any]:
        """Run Flutter tests."""
        full_path = self.project_root / test_path

        if not full_path.exists():
            return {
                "success": False,
                "error": f"Flutter test path {test_path} not found",
            }

        mobile_dir = self.project_root / "apps" / "mobile"

        cmd = ["flutter", "test", str(full_path)]

        if verbose:
            cmd.append("--verbose")

        try:
            result = subprocess.run(
                cmd, cwd=mobile_dir, capture_output=True, text=True, timeout=300
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"{test_name} timed out"}
        except Exception as e:
            return {"success": False, "error": f"{test_name} failed: {e}"}

    def _calculate_summary(self):
        """Calculate test summary statistics."""
        total = 0
        passed = 0
        failed = 0
        skipped = 0
        errors = 0

        for suite_name, suite_result in self.results["tests"].items():
            if suite_name == "documentation":
                total += 1
                if suite_result["success"]:
                    passed += 1
                else:
                    failed += 1
            else:
                # For pytest results, we need to parse the output
                if "backend" in suite_result and "frontend" in suite_result:
                    # Unit tests have backend and frontend components
                    for component in ["backend", "frontend"]:
                        total += 1
                        if suite_result[component]["success"]:
                            passed += 1
                        else:
                            failed += 1
                else:
                    # Other test suites
                    total += 1
                    if suite_result["success"]:
                        passed += 1
                    else:
                        failed += 1

        self.results["summary"] = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
        }

    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 SMOKE TEST SUMMARY")
        print("=" * 60)

        summary = self.results["summary"]
        duration = self.results["duration"]

        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Errors: {summary['errors']}")
        print(f"Duration: {duration:.2f} seconds")

        if summary["failed"] > 0 or summary["errors"] > 0:
            print("\n❌ Some tests failed!")
            print("\nFailed Tests:")
            for suite_name, suite_result in self.results["tests"].items():
                if not suite_result["success"]:
                    print(
                        f"  - {suite_name}: {suite_result.get('error', 'Unknown error')}"
                    )
        else:
            print("\n✅ All tests passed!")

        print("=" * 60)

    def save_results(self, output_file: Optional[Path] = None):
        """Save test results to file."""
        if output_file is None:
            output_file = self.project_root / "smoke-test-results.json"

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"📄 Test results saved to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run comprehensive smoke tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--parallel", "-p", action="store_true", help="Run tests in parallel"
    )
    parser.add_argument("--output", "-o", type=str, help="Output file for results")
    parser.add_argument(
        "--suite",
        "-s",
        type=str,
        choices=["unit", "integration", "e2e", "docs", "all"],
        default="all",
        help="Test suite to run",
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    runner = SmokeTestRunner(project_root)

    if args.suite == "all":
        success = runner.run_all_tests(args.verbose, args.parallel)
    else:
        # Run specific test suite
        if args.suite == "unit":
            result = runner._run_unit_tests(args.verbose, args.parallel)
        elif args.suite == "integration":
            result = runner._run_integration_tests(args.verbose, args.parallel)
        elif args.suite == "e2e":
            result = runner._run_e2e_tests(args.verbose, args.parallel)
        elif args.suite == "docs":
            result = runner._run_documentation_validation(args.verbose, args.parallel)

        success = result["success"]
        runner.results["tests"][args.suite] = result

    if args.output:
        runner.save_results(Path(args.output))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
