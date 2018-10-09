import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        username = os.environ['ADMIN_USERNAME']
        password = os.environ['ADMIN_PASSWORD']

        qs = get_user_model().objects.filter(username=username)
        if qs.exists():
            user = qs.get()
            user.set_password(password)
            user.save()
        else:
            get_user_model().objects.create_superuser(
                name='Admin',
                password=password,
                username=username,
            )
