import os
from threading import Lock

from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError


class EnsureDatabaseReadyMiddleware:
    """Ensure required tables and an optional first support admin exist."""

    _migrate_lock = Lock()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.ensure_database()
        self.ensure_initial_support_admin()
        return self.get_response(request)

    def ensure_database(self):
        try:
            tables = set(connection.introspection.table_names())
            if {'team_userprofile', 'team_supportticket', 'team_supportmessage'} <= tables:
                return
        except (OperationalError, Exception):
            pass
        with self._migrate_lock:
            try:
                tables = set(connection.introspection.table_names())
                if {'team_userprofile', 'team_supportticket', 'team_supportmessage'} <= tables:
                    return
            except (OperationalError, Exception):
                pass
            call_command('migrate', verbosity=0, interactive=False, run_syncdb=True, no_input=True)

    def ensure_initial_support_admin(self):
        egn = os.environ.get('INITIAL_ADMIN_EGN', '').strip()
        name = os.environ.get('INITIAL_ADMIN_NAME', '').strip()
        email = os.environ.get('INITIAL_ADMIN_EMAIL', '').strip()
        password = os.environ.get('INITIAL_ADMIN_PASSWORD', '')
        if not all((egn, name, email, password)):
            return
        try:
            from .models import UserProfile
            if not UserProfile.objects.filter(egn=egn).exists():
                UserProfile.objects.create_superuser(
                    egn=egn, full_name=name, email=email, password=password,
                )
        except (OperationalError, Exception):
            return
