from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create a superuser with predefined credentials"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = settings.SUPERUSER
        email = "your_email@example.com"
        password = settings.SUPERUSER_PASSWORD

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS("Superuser created successfully."))
        else:
            self.stdout.write(self.style.WARNING("Superuser with this username already exists."))
