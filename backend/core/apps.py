from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.core'
    label = 'core'  # Add this line to set the app label

    def ready(self):
        # import backend.core.signals  # Comment out to prevent circular import
        pass