"""
Quiz application configuration.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class QuizConfig(AppConfig):
    """Quiz application configuration."""
    
    name = 'quiz'
    verbose_name = _('Minnesota Driver License Quiz')
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        """Initialize application signals and setup."""
        from . import signals  # noqa
        from .monitoring import setup_monitoring
        from .utils.logging import setup_logging
        
        # Setup application monitoring
        setup_monitoring()
        
        # Setup logging configuration
        setup_logging()
