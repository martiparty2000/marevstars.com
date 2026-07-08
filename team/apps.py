from django.apps import AppConfig

class TeamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team'

    def ready(self):
        # Import signals so that post_migrate backups run automatically
        try:
            import team.signals  # noqa: F401
        except Exception:
            # Avoid import-time failures blocking Django startup
            pass