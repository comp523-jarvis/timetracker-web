import pytest
from django.conf import settings
from django.urls import reverse

from vms import models


url = reverse('vms:client-create')


@pytest.mark.integration
def test_GET_anonymous(client):
    """
    If the user is anonymous, the view should redirect to the login
    page.
    """
    response = client.get(url)
    redirect_url = f'{reverse(settings.LOGIN_URL)}?next={url}'

    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.integration
def test_GET_as_admin(client, staffing_agency_admin_factory):
    """
    If the requesting user is a staffing agency admin, they should be
    allowed access to the view.
    """
    admin = staffing_agency_admin_factory()
    client.force_login(admin.user)

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.integration
def test_GET_non_admin(client, user_factory):
    """
    If the requesting user is non a staffing agency admin, a 403
    response should be returned.
    """
    client.force_login(user_factory())
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.integration
def test_POST_as_admin(client, staffing_agency_admin_factory):
    """
    Sending a POST request to the view as a staffing agency admin should
    create a new client company and send out the admin invitation.
    """
    admin = staffing_agency_admin_factory()
    client.force_login(admin.user)

    data = {
        'admin_email': 'admin@example.com',
        'email': 'acme@example.com',
        'name': 'Acme Client Inc.',
    }
    response = client.post(url, data)

    client = models.Client.objects.get()
    invite = client.admin_invites.get()

    assert response.status_code == 302
    assert response.url == client.get_absolute_url()

    assert client.email == data['email']
    assert client.name == data['name']

    assert invite.email == data['admin_email']
