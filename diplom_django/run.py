import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diplom_django.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command


def create_superuser_if_not_exists():
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser {username} was created")
    else:
        print(f"Superuser {username} already exists")


if __name__ == "__main__":
    call_command("migrate")
    create_superuser_if_not_exists()
    call_command("runserver", "0.0.0.0:8000")
