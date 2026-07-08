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
                'is_staff': u.get('is_staff', False),
                'is_superuser': u.get('is_superuser', False),
                'password': u.get('password_hash'),
            }

            if u.get('date_joined'):
                dt = parse_datetime(u['date_joined'])
                if dt:
                    defaults['date_joined'] = dt

            obj, did_create = UserProfile.objects.update_or_create(egn=u['egn'], defaults=defaults)
            if did_create:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Imported users: created={created} updated={updated}'))
