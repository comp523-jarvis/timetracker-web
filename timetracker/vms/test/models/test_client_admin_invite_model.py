from django.conf import settings
from django.template.loader import render_to_string

from vms import models


def test_accept(client_admin_invite_factory, user_factory):
    """
    Accepting the invitation should create a new client admin for the
    user who accepts.
    """
    invite = client_admin_invite_factory()
    user = user_factory()

    admin = invite.accept(user)

    assert admin.client == invite.client
    assert models.ClientAdminInvite.objects.count() == 0


def test_send(client_admin_invite_factory, request_factory, mailoutbox):
    """
    Sending the invitation should send an email to the email address
    attached to the invite.
    """
    request = request_factory.get('/')

    invite = client_admin_invite_factory()
    invite.send(request)

    context = {
        'accept_url': f'{request.get_host()}{invite.accept_url}',
        'client': invite.client,
    }
    expected_msg = render_to_string(
        'vms/emails/client-admin-invite.txt',
        context=context,
    )

    assert len(mailoutbox) == 1
    msg = mailoutbox[0]

    assert msg.body == expected_msg
    assert msg.from_email == settings.DEFAULT_FROM_EMAIL
    assert msg.subject == 'Client Administrator Invitation'
    assert msg.to == [invite.email]


def test_string_conversion(client_admin_invite_factory):
    """
    Converting an invite to a string should return a string containing
    the email it was sent to and the linked client.
    """
    invite = client_admin_invite_factory()
    expected = f'Admin invite for {invite.email} from {invite.client}'

    assert str(invite) == expected
