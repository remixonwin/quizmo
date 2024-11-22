"""
Pytest plugin for coverage debugging.
"""
import pytest
from .coverage_debug import coverage_debugger, log_coverage_info

def pytest_configure(config):
    """Configure pytest with coverage debugging."""
    coverage_debugger.analyze_coverage_config()
    coverage_debugger.logger.info("Starting test session with coverage debugging")

def pytest_runtest_setup(item):
    """Setup coverage debugging for each test."""
    coverage_debugger.logger.info(f"Setting up coverage tracking for test: {item.name}")

def pytest_runtest_teardown(item):
    """Teardown coverage debugging after each test."""
    coverage_debugger.logger.info(f"Completed coverage tracking for test: {item.name}")

def pytest_sessionfinish(session, exitstatus):
    """Final coverage debugging report."""
    coverage_debugger.logger.info(f"Test session completed with exit status: {exitstatus}")
    if exitstatus == 0:
        coverage_debugger.logger.info("All tests passed")
    else:
        coverage_debugger.logger.warning("Some tests failed - check coverage report for details")
