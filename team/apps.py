from django.apps import AppConfig

class TeamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team'

    def ready(self):
        # Тук импортираш сигналите, за да работят
        import team.signals