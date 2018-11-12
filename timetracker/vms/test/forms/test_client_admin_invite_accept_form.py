from unittest import mock

import pytest
from django.core.exceptions import ValidationError

from vms import forms


def test_clean_invalid_token(db):
    """
    If there is no invite with the provided token, clean should raise
    a validation error.
    """
    form = forms.ClientAdminInviteAcceptForm('foo')

    with pytest.raises(ValidationError):
        form.clean()


def test_clean_valid_token(client_admin_invite_factory):
    """
    If the token provided to the form is valid, the clean method should
    save the associated invite on the form instance.
    """
    invite = client_admin_invite_factory()
    form = forms.ClientAdminInviteAcceptForm(invite.token)

    form.clean()

    assert form.invite == invite


def test_save(client_admin_invite_factory, user_factory):
    """
    Saving the form should accept the associate invite.
    """
    invite = client_admin_invite_factory()
    user = user_factory()

    form = forms.ClientAdminInviteAcceptForm(invite.token, data={})
    assert form.is_valid()

    with mock.patch.object(form.invite, 'accept') as mock_accept:
        result = form.save(user)

    assert mock_accept.call_args[0] == (user,)
    assert result == mock_accept.return_value
