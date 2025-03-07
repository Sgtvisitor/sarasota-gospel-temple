from django.apps import AppConfig

class VisitorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'visitors'

    def ready(self):
        import visitors.signals  # Register the signals
