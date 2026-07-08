from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
import json

from team.models import UserProfile


class Command(BaseCommand):
    help = 'Export all users to a JSON file (includes password hash, NOT plaintext)'

    def handle(self, *args, **options):
        outdir = settings.BASE_DIR / 'backups'
        outdir.mkdir(exist_ok=True)
        outpath = outdir / f'users_export_{timezone.now().strftime("%Y%m%d%H%M%S")}.json'

        users = []
        for u in UserProfile.objects.all():
            users.append({
                'egn': u.egn,
                'username': u.username,
                'email': u.email,
                'full_name': u.full_name,
                'role': getattr(u, 'role', None),
                'is_active': u.is_active,
                'is_staff': u.is_staff,
                'is_superuser': u.is_superuser,
                'is_approved': getattr(u, 'is_approved', False),
                'child_full_name': getattr(u, 'child_full_name', ''),
                'child_egn': getattr(u, 'child_egn', ''),
                'password_hash': u.password,
                'date_joined': u.date_joined.isoformat() if u.date_joined else None,
                'last_login': u.last_login.isoformat() if getattr(u, 'last_login', None) else None,
            })

        with open(outpath, 'w', encoding='utf-8') as fh:
            json.dump(users, fh, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f'Exported {len(users)} users to {outpath}'))
