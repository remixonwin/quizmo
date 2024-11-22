"""
Test runner settings.
"""
from django.test.runner import DiscoverRunner

class QuizTestRunner(DiscoverRunner):
    """Custom test runner for the quiz app."""
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
