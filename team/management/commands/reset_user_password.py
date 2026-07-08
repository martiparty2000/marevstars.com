from django.core.management.base import BaseCommand, CommandError
from team.models import UserProfile


class Command(BaseCommand):
    help = 'Reset a user password by EGN. Usage: python manage.py reset_user_password <egn> <new_password>'

    def add_arguments(self, parser):
        parser.add_argument('egn', type=str)
        parser.add_argument('new_password', type=str)

    def handle(self, *args, **options):
        egn = options['egn']
        new_password = options['new_password']
        try:
            user = UserProfile.objects.get(egn=egn)
        except UserProfile.DoesNotExist:
            raise CommandError(f'No user with EGN {egn}')

        user.set_password(new_password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Password for user {egn} has been reset.'))
