from unittest import mock

from django.conf import settings

from vms import models


@mock.patch('vms.id_utils.generate_unique_id', return_value=42)
def test_clean_existing_id(mock_generate_id, db):
    """
    If the client already has an ID, it should not be altered when
    cleaned.
    """
    client = models.Client(
        email='acme@example.com',
        id=3,
        name='Acme Inc.',
    )
    old_id = client.id

    client.clean()

    assert client.id == old_id
    assert mock_generate_id.call_count == 0


@mock.patch('vms.models.generate_slug')
def test_clean_existing_slug(mock_generate_slug, db):
    """
    If the client already has a slug, a new one should not be generated
    when cleaned.
    """
    client = models.Client(
        email='acme@example.com',
        name='Acme Inc.',
        slug='acme-inc',
    )
    client.clean()

    assert mock_generate_slug.call_count == 0
    assert client.slug == 'acme-inc'


@mock.patch('vms.models.id_utils.generate_unique_id', return_value=42)
def test_clean_generate_id(mock_generate_id, db):
    """
    If the client does not have an ID, one should be generated when the
    model is cleaned.
    """
    client = models.Client(
        email='acme@example.com',
        name='Acme Inc.',
    )
    client.clean()

    assert client.id == 42
    assert mock_generate_id.call_args[0][0] == settings.CLIENT_ID_LENGTH


@mock.patch('vms.models.generate_slug', return_value='foo')
def test_clean_generate_slug(mock_generate_slug, db):
    """
    If the instance does not have a slug, one should be generated when
    the instance is cleaned.
    """
    client = models.Client(
        email='acme@example.com',
        name='Acme Inc.',
    )
    client.clean()

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
