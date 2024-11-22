import logging
import sys
from functools import wraps
import traceback
from typing import Callable, Any, Optional
from datetime import datetime

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

# Example usage:
# @log_coverage_info
# def your_test_function():
#     pass
