from threading import Lock

from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError


class EnsureDatabaseReadyMiddleware:
    """Ensure required application tables exist before request handling."""

    _migrate_lock = Lock()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.ensure_database()
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

            call_command("migrate", verbosity=0, interactive=False, run_syncdb=True, no_input=True)
