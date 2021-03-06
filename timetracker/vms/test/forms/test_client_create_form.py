from unittest import mock

from vms import forms


@mock.patch(
    'vms.models.ClientAdminInvite.send',
    autospec=True,
)
def test_save(mock_send, db, request_factory):
    """
    Saving the form should create a new client and send an email to the
    new administrator.
    """
    data = {
        'admin_email': 'admin@example.com',
        'email': 'client@example.com',
        'name': 'Acme Client Inc.',
    }
    request = request_factory.get('/')
    form = forms.ClientCreateForm(data=data)

    assert form.is_valid()
    client = form.save(request)
    invite = client.admin_invites.get()

    assert client.email == data['email']
    assert client.name == data['name']

    assert invite.email == data['admin_email']
    assert mock_send.call_count == 1
    assert mock_send.call_args[0][1] == request
