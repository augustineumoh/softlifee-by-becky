from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Create superuser automatically from environment variables'

    def handle(self, *args, **kwargs):
        User       = get_user_model()
        email      = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password   = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        first_name = os.environ.get('DJANGO_SUPERUSER_NAME', 'Becky')

        if not email or not password:
            self.stdout.write('Skipping superuser — env vars not set.')
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(f'Superuser {email} already exists — skipping.')
            return

        try:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} created!'))
        except Exception as e:
            self.stdout.write(f'Skipping superuser creation: {e}')