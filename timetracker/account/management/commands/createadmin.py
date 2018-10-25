import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Command to create an admin user using credentials from the
    environment.
    """

    help = (
        "Create an admin user using credentials found in the 'ADMIN_USERNAME' "
        "and 'ADMIN_PASSWORD' environment variables."
    )

    def handle(self, *args, **kwargs):
        """
        Execute the command.
        """
        username = os.environ['ADMIN_USERNAME']
        password = os.environ['ADMIN_PASSWORD']

        qs = get_user_model().objects.filter(username=username)
        if qs.exists():
            user = qs.get()
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated account '{username}' to have admin privileges.",
                ),
            )
        else:
            get_user_model().objects.create_superuser(
                name='Admin',
                password=password,
                username=username,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created admin account '{username}'.",
                ),
            )
