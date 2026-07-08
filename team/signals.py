from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
import json
import logging

from .models import UserProfile

logger = logging.getLogger(__name__)


def _export_users_to_backup():
    try:
        outdir = settings.BASE_DIR / 'backups'
        outdir.mkdir(exist_ok=True)
        outpath = outdir / f'users_backup_{timezone.now().strftime("%Y%m%d%H%M%S")}.json'

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
                'password_hash': u.password,
                'date_joined': u.date_joined.isoformat() if u.date_joined else None,
            })

        with open(outpath, 'w', encoding='utf-8') as fh:
            json.dump(users, fh, ensure_ascii=False, indent=2)

        logger.info('Exported %d users to %s', len(users), outpath)
    except Exception as exc:
        logger.exception('Failed to export users backup: %s', exc)


@receiver(post_migrate)
def backup_users_on_migrate(sender, **kwargs):
    # Run a best-effort backup after migrations; never raise errors to interrupt deploy
    _export_users_to_backup()
