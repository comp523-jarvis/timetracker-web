import pytest
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from vms import models


def test_clean_new(client_factory):
    """
    Cleaning a new client job should generate a slug for the job.
    """
    job = models.ClientJob(
        client=client_factory(),
        name='Job Title',
        pay_rate=42,
    )
    job.clean()

    assert job.slug == slugify(job.name)


def test_clean_old(client_job_factory):
    """
    Cleaning an existing client job with a new name should not update
    the slug.
    """
    job = client_job_factory(name='Old Job Name')
    slug = job.slug

    job.name = 'New Job Name'
    job.clean()

    assert job.slug == slug


def test_clean_fields_duplicate_name(client_job_factory):
    """
    If a job will slugify to the same value as an existing job for the
    same client, the validation should fail.
    """
    old_job = client_job_factory()
    new_job = models.ClientJob(
        client=old_job.client,
        name=old_job.name,
        pay_rate=42,
    )
    new_job.clean()

    with pytest.raises(ValidationError):
        new_job.clean_fields()


def test_clean_fields_excluded(client_job_factory):
    """
    If the job is a duplicate but the name field is excluded, validation
    should pass.
    """
    old_job = client_job_factory()
    new_job = models.ClientJob(
        client=old_job.client,
        name=old_job.name,
        pay_rate=42,
    )

    new_job.clean()
    new_job.clean_fields(exclude=['name'])


def test_clean_fields_same_slug_different_client(client_job_factory):
    """
    If two jobs have the same slug but belong to different clients, the
    validation should pass.
    """
    job1 = client_job_factory(name='Common Name')
    job2 = client_job_factory(name='Common Name')

    job1.clean_fields()
    job2.clean_fields()


def test_string_conversion(client_job_factory):
    """
    Converting a client job to a string should return the name of the
    job.
    """
    job = client_job_factory()

    assert str(job) == job.name
