"""
Coverage debugging utilities for test suite.
"""
import logging
import sys
from functools import wraps
import traceback
from typing import Callable, Any, Optional
from datetime import datetime
import os
from django.conf import settings

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/coverage_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('coverage_debug')

def log_coverage_info(func: Callable) -> Callable:
    """Decorator to log information about test coverage execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.info(f"Starting coverage for: {func.__name__}")
            start_time = datetime.now()
            result = func(*args, **kwargs)
            execution_time = datetime.now() - start_time
            logger.info(f"Coverage completed for {func.__name__}. Time taken: {execution_time}")
            return result
        except Exception as e:
            logger.error(f"Coverage error in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    return wrapper

class CoverageDebugger:
    """Utility class for debugging coverage issues."""
    
    def __init__(self):
        self.logger = logging.getLogger('coverage_debug.debugger')
    
    def track_excluded_lines(self, filename: str, excluded_lines: list) -> None:
        """Track which lines are being excluded from coverage."""
        self.logger.info(f"Excluded lines in {filename}:")
        for line_num in excluded_lines:
            self.logger.info(f"Line {line_num} excluded")
    
    def track_included_modules(self, modules: list) -> None:
        """Track which modules are included in coverage."""
        self.logger.info("Included modules in coverage:")
        for module in modules:
            self.logger.info(f"- {module}")
    
    def track_coverage_run(self, command: str, result: Optional[Any] = None) -> None:
        """Track coverage command execution."""
        self.logger.info(f"Executing coverage command: {command}")
        if result:
            self.logger.info(f"Result: {result}")
    
    def analyze_coverage_config(self) -> None:
        """Analyze the current coverage configuration."""
        from coverage.files import FnmatchMatcher
        
        self.logger.info("Analyzing coverage configuration:")
        
        # Log source directories
        self.logger.info(f"Source directory: {settings.BASE_DIR}/quiz")
        
        # Log omitted patterns
        omit_patterns = [
            "*/migrations/*",
            "*/tests/*",
            "*/admin.py",
            "*/apps.py",
            "manage.py",
            "*/wsgi.py",
            "*/asgi.py",
            "*/settings.py"
        ]
        self.logger.info("Omitted patterns:")
        for pattern in omit_patterns:
            matcher = FnmatchMatcher(pattern)
            self.logger.info(f"- {pattern}")
            
        # Log excluded lines patterns
        exclude_patterns = [
            "pragma: no cover",
            "def __repr__",
            "if self.debug:",
            "raise NotImplementedError",
            "if __name__ == .__main__.:",
            "pass",
            "raise ImportError"
        ]
        self.logger.info("Excluded line patterns:")
        for pattern in exclude_patterns:
            self.logger.info(f"- {pattern}")

coverage_debugger = CoverageDebugger()

# Example usage in tests:
# @log_coverage_info
# def test_your_function():
#     coverage_debugger.analyze_coverage_config()
#     coverage_debugger.track_coverage_run("pytest --cov")
