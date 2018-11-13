import datetime

import pytest
from django.utils import timezone

from vms import models


@pytest.mark.integration
def test_GET_as_admin(
        client,
        client_admin_factory,
        client_job_factory,
        employee_factory,
        time_record_factory):
    """
    Sending a GET request to the view as an administrator for the client
    should return information about the client.
    """
    admin = client_admin_factory()
    client.force_login(admin.user)

    client_company = admin.client

    # Create jobs
    client_job_factory(client=client_company)
    client_job_factory(client=client_company)

    # Create employees
    employee_factory(client=client_company, is_active=True)
    employee_factory(client=client_company, is_active=True)

    # Create time records
    now = timezone.now()
    later = now + datetime.timedelta(hours=1)
    time_record_factory(
        employee__client=client_company,
        job__client=client_company,
        time_end=later,
        time_start=now,
    )
    time_record_factory(
        employee__client=client_company,
        job__client=client_company,
        time_end=later,
        time_start=now,
    )

    active_employees = client_company.employees.filter(is_active=True).count()
    projects = client_company.jobs.count()
    total_hours = models.TimeRecord.objects.filter(
        employee__client=client_company,
    ).total_time().total_seconds() / (60 * 60)

    url = client_company.get_absolute_url()
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['active_employees'] == active_employees
    assert response.context_data['job_count'] == projects
    assert response.context_data['total_hours'] == total_hours
