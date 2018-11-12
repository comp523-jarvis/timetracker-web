import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.integration
def test_GET_anonymous(client, client_admin_invite_factory):
    """
    If an anonymous user sends a GET request to the view, they should be
    redirected to the login page.
    """
    invite = client_admin_invite_factory()
    redirect_url = f'{reverse(settings.LOGIN_URL)}?next={invite.accept_url}'

    url = invite.accept_url
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.integration
def test_POST_valid_token(client, client_admin_invite_factory, user_factory):
    """
    Sending a POST request with a valid token to the view should create
    a new client admin for the requesting user.
    """
    user = user_factory()
    client.force_login(user)

    invite = client_admin_invite_factory()

    url = invite.accept_url
    response = client.post(url, {})

    assert response.status_code == 302
    assert response.url == invite.client.get_absolute_url()

    assert invite.client.admins.filter(user=user).exists()
