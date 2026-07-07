from threading import Lock

from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError


class EnsureDatabaseReadyMiddleware:
    """Ensure the custom user table exists before request handling touches the DB."""

    _migrate_lock = Lock()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.ensure_database()
        return self.get_response(request)

    def ensure_database(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='team_userprofile'"
                )
                if cursor.fetchone():
                    return
        except (OperationalError, Exception):
            pass

        with self._migrate_lock:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='team_userprofile'"
                    )
                    if cursor.fetchone():
                        return
            except (OperationalError, Exception):
                pass

            call_command("migrate", verbosity=0, interactive=False, run_syncdb=True, no_input=True)
