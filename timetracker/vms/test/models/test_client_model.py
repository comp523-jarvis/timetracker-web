from unittest import mock

from vms import models


@mock.patch('vms.models.generate_slug')
def test_save_existing_slug(mock_generate_slug, db):
    """
    If the client already has a slug, a new one should not be generated
    when saved.
    """
    client = models.Client(
        email='acme@example.com',
        name='Acme Inc.',
        slug='acme-inc',
    )
    client.save()

    assert mock_generate_slug.call_count == 0
    assert client.slug == 'acme-inc'


@mock.patch('vms.models.generate_slug', return_value='foo')
def test_save_generate_slug(mock_generate_slug, db):
    """
    If the instance does not have a slug, one should be generated when
    the instance is saved.
    """
    client = models.Client(
        email='acme@example.com',
        name='Acme Inc.',
    )
    client.save()

    assert mock_generate_slug.call_count == 1
    assert mock_generate_slug.call_args[0][0] == client.name
    assert client.slug == 'foo'


def test_string_conversion(client_factory):
    """
    Converting a client instance to a string should return the client's
    name.
    """
    client = client_factory()

    assert str(client) == client.name
