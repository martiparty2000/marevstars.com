from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from team.models import UserProfile

import json
from pathlib import Path


class Command(BaseCommand):
    help = 'Import users from a JSON backup created by export_users. Usage: python manage.py import_users <path>'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        p = Path(options['path'])
        if not p.exists():
            raise CommandError(f'File not found: {p}')

        with open(p, 'r', encoding='utf-8') as fh:
            data = json.load(fh)

        created = 0
        updated = 0
        for u in data:
            defaults = {
                'username': u.get('username'),
                'email': u.get('email'),
                'full_name': u.get('full_name'),
                'role': u.get('role'),
                'is_active': u.get('is_active', True),
            }

            if u.get('date_joined'):
                dt = parse_datetime(u['date_joined'])
                if dt:
                    defaults['date_joined'] = dt

            obj, did_create = UserProfile.objects.update_or_create(egn=u['egn'], defaults=defaults)

            # Ensure flags and child fields and password are set explicitly
            obj.is_staff = u.get('is_staff', False)
            obj.is_superuser = u.get('is_superuser', False)
            obj.is_active = u.get('is_active', True)
            if 'is_approved' in u:
                try:
                    obj.is_approved = bool(u.get('is_approved'))
                except Exception:
                    pass
            obj.child_full_name = u.get('child_full_name', '')
            obj.child_egn = u.get('child_egn', '')

            # Restore hashed password directly
            pw = u.get('password_hash')
            if pw:
                obj.password = pw

            # Restore last_login if present
            if u.get('last_login'):
                dt2 = parse_datetime(u['last_login'])
                if dt2:
                    obj.last_login = dt2

            obj.save()

            if did_create:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Imported users: created={created} updated={updated}'))
