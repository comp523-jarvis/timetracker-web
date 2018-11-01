import pytest
from django.core.exceptions import ValidationError

from vms import forms


def test_clean_clocked_in(employee_factory, time_record_factory):
    """
    If the employee given to the form is already clocked in, the form
    should raise a ``ValidationError``.
    """
    employee = employee_factory()
    time_record_factory(employee=employee)

    form = forms.ClockInForm(employee)

    with pytest.raises(ValidationError):
        form.clean()


def test_clean_not_clocked_in(employee_factory):
    """
    If the employee is not clocked in, cleaning the form should succeed.
    """
    employee = employee_factory()
    form = forms.ClockInForm(employee)

    form.clean()


def test_job_queryset(client_job_factory, employee_factory):
    """
    Only jobs owned by the client the employee works for should be
    presented in the form.
    """
    employee = employee_factory()
    client_job_factory(client=employee.client)
    client_job_factory(client=employee.client)
    client_job_factory()

    form = forms.ClockInForm(employee)

    expected = [(job.pk, str(job)) for job in employee.client.jobs.all()]

    assert list(form.fields['job'].choices) == expected


def test_save(client_job_factory, employee_factory):
    """
    Saving the form should create a new time record for the employee.
    """
    employee = employee_factory()
    job = client_job_factory(client=employee.client)
    form = forms.ClockInForm(employee, data={'job': job.id})

    assert form.is_valid()
    form.save()

    assert employee.is_clocked_in
    record = employee.time_records.get()

    assert record.job == job
    assert record.pay_rate == job.pay_rate
