"""
Test debugging utilities.
"""
import logging
import sys
from functools import wraps
from typing import Type, Callable
from django.test import TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext
from quiz.tests.coverage_debug import coverage_debugger

logger = logging.getLogger('test_debug')

def debug_test(test_func: Callable) -> Callable:
    """Decorator to add debugging information to test functions."""
    @wraps(test_func)
    def wrapper(self, *args, **kwargs):
        logger.info(f"Running test: {test_func.__name__}")
        try:
            with CaptureQueriesContext(connection) as context:
                result = test_func(self, *args, **kwargs)
            logger.info(f"Queries executed: {len(context.captured_queries)}")
            for i, query in enumerate(context.captured_queries, 1):
                logger.info(f"Query {i}: {query['sql']}")
            return result
        except Exception as e:
            logger.error(f"Test failed: {test_func.__name__}")
            logger.error(f"Error: {str(e)}")
            logger.error("Test context:")
            for attr in dir(self):
                if not attr.startswith('_'):
                    value = getattr(self, attr)
                    logger.info(f"{attr}: {value}")
            raise
    return wrapper

class DebugTestCase(TestCase):
    """Base test case with debugging capabilities."""
    
    def setUp(self):
        super().setUp()
        self.debug_logger = logger
        self.coverage_debugger = coverage_debugger
    
    def assertQueryCount(self, expected_count: int, test_func: Callable, *args, **kwargs):
        """Assert that a function executes exactly the expected number of queries."""
        with CaptureQueriesContext(connection) as context:
            test_func(*args, **kwargs)
        actual_count = len(context.captured_queries)
        if actual_count != expected_count:
            queries = "\n".join(
                f"{i+1}. {q['sql']}" 
                for i, q in enumerate(context.captured_queries)
            )
            self.fail(
                f"Expected {expected_count} queries but got {actual_count}.\n"
                f"Executed queries:\n{queries}"
            )
    
    def assertModelValid(self, model_instance, exclude_fields=None):
        """Assert that a model instance is valid."""
        try:
            model_instance.full_clean(exclude=exclude_fields)
        except Exception as e:
            self.fail(f"Model validation failed: {str(e)}")
    
    def print_model_state(self, model_instance):
        """Print the current state of a model instance."""
        self.debug_logger.info(f"Model state for {model_instance.__class__.__name__}:")
        for field in model_instance._meta.fields:
            value = getattr(model_instance, field.name)
            self.debug_logger.info(f"{field.name}: {value}")

# Example usage:
# @debug_test
# def test_your_function(self):
#     self.assertQueryCount(1, self.client.get, '/your-url/')
