from django.contrib.auth import get_user_model
from django.core.management import call_command


def test_new_user(db, env):
    """
    If no user exists with the provided username, a new user should be
    created.
    """
    env['ADMIN_USERNAME'] = 'admin'
    env['ADMIN_PASSWORD'] = 'password'

    call_command('createadmin')
    admin = get_user_model().objects.get()

    assert admin.is_staff
    assert admin.is_superuser
    assert admin.username == env['ADMIN_USERNAME']

    assert admin.check_password(env['ADMIN_PASSWORD'])


def test_update_user(env, user_factory):
    """
    If there is already a user with the provided username, the user's
    information should be updated to match the provided arguments.
    """
    user = user_factory(password='not-password')

    env['ADMIN_USERNAME'] = user.username
    env['ADMIN_PASSWORD'] = 'password'

    call_command('createadmin')
    user.refresh_from_db()

    assert user.is_staff
    assert user.is_superuser
    assert user.check_password(env['ADMIN_PASSWORD'])

    assert get_user_model().objects.count() == 1
