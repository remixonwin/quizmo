from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.core'
    label = 'core'

    def ready(self):
        try:
            import backend.core.signals  # Using absolute import
        except ImportError:
            pass