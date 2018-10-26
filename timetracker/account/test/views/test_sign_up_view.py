from django.contrib.auth import get_user, get_user_model
from django.urls import reverse


URL = reverse('account:signup')


def test_sign_up(client, db):
    """
    Submitting the signup form should create a new user and authenticate
    them.
    """
    data = {
        'name': 'John Smith',
        'password1': 'c0mplexpassw0rd',
        'password2': 'c0mplexpassw0rd',
        'username': 'johnsmith',
    }

    response = client.post(URL, data)

    assert response.status_code == 302
    assert response.url == reverse('account:profile')

    user = get_user_model().objects.get()

    assert user.name == data['name']
    assert user.username == data['username']
    assert user.check_password(data['password1'])

    # A side effect of signing up should be that the user is now logged
    # in.
    assert get_user(client) == user


def test_sign_up_with_redirect(client, db):
    """
    If there is a 'next' parameter in the URL, it should be used to
    redirect the user after they sign up.
    """
    data = {
        'name': 'John Smith',
        'password1': 'c0mplexpassw0rd',
        'password2': 'c0mplexpassw0rd',
        'username': 'johnsmith',
    }

    next_url = '/'
    url = f'{URL}?next={next_url}'
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == next_url
