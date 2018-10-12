from unittest import mock

from vms import models


@mock.patch('vms.models.generate_slug')
def test_save_existing_slug(mock_generate_slug, db):
    """
    If the agency already has a slug, a new one should not be generated
    when saved.
    """
    agency = models.StaffingAgency(
        email='acme@example.com',
        name='Acme Inc.',
        slug='acme-inc',
    )
    agency.save()

    assert mock_generate_slug.call_count == 0
    assert agency.slug == 'acme-inc'


@mock.patch('vms.models.generate_slug', return_value='foo')
def test_save_generate_slug(mock_generate_slug, db):
    """
    If the instance does not have a slug, one should be generated when
    the instance is saved.
    """
    agency = models.StaffingAgency(
        email='acme@example.com',
        name='Acme Inc.',
    )
    agency.save()

    assert mock_generate_slug.call_count == 1
    assert mock_generate_slug.call_args[0][0] == agency.name
    assert agency.slug == 'foo'


def test_string_conversion(staffing_agency_factory):
    """
    Converting an agency instance to a string should return the agency's
    name.
    """
    agency = staffing_agency_factory()

    assert str(agency) == agency.name
