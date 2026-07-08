from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
import json
import logging

from .models import UserProfile
from .gsheets import add_user_to_sheet  # Увери се, че това е името на файла ти

logger = logging.getLogger(__name__)

# --- 1. Твоят съществуващ backup код ---
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
    _export_users_to_backup()

@receiver(post_save, sender=UserProfile)
def sync_user_to_gsheet(sender, instance, created, **kwargs):
    if created:
        print(f"DEBUG: Сигналът се задейства за {instance.username}")
        try:
            add_user_to_sheet(instance.full_name or instance.username, instance.email)
            print("DEBUG: Успешно записано в Google Sheets!")
        except Exception as e:
            print(f"DEBUG: ГРЕШКА при запис: {e}")