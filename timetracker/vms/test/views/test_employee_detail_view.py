import pytest
import datetime
from django.utils import timezone


@pytest.mark.integration
def test_GET_as_employee(
    client,
    employee_factory,
):

    admin = employee_factory()
    client.force_login(admin.user)

    url = admin.get_absolute_url()
    response = client.get(url)

    assert response.status_code == 200
    assert not response.context_data['is_client_admin']
    assert response.context_data['is_employee']
    assert response.context_data['unapproved_count'] == 0
    assert response.context_data['total_hours'] == 0


@pytest.mark.integration
def test_GET_as_client_admin(
    client,
    client_admin_factory,
    employee_factory,
):

    admin = client_admin_factory()
    client.force_login(admin.user)

    employee = employee_factory(client=admin.client)

    url = employee.get_absolute_url()
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['is_client_admin']
    assert not response.context_data['is_employee']


@pytest.mark.integration
def test_GET_as_staffing_agency_admin(
    client,
    staffing_agency_admin_factory,
    employee_factory,
):

    admin = staffing_agency_admin_factory()
    client.force_login(admin.user)

    employee = employee_factory(staffing_agency=admin.agency)

    url = employee.get_absolute_url()
    response = client.get(url)

    assert response.status_code == 200
    assert not response.context_data['is_client_admin']
    assert not response.context_data['is_employee']


@pytest.mark.integration
def test_employee_detail_variables(
    client,
    employee_factory,
    client_job_factory,
    time_record_factory,
    time_record_approval_factory,
):
    """
    Testing EmployeeDetailView for having
    some unapproved records,
    an open time record,
    and a correct total hour count.
    """
    admin = employee_factory(is_active=True)
    client.force_login(admin.user)

    # Create time records.
    total_hours = 1
    now = timezone.now()
    later = now + datetime.timedelta(hours=total_hours)
    time_record_factory(
        employee=admin,
        time_start=now,
        time_end=later,
    )
    time_record_factory(
        employee=admin,
        time_start=now,
        time_end=later,
    )
    # The open time record.
    time_record_factory(
        employee=admin,
        time_start=now,
        time_end=None,
    )

    url = admin.get_absolute_url()
    response = client.get(url)

    assert response.context_data['open_time_record']
    assert response.context_data['unapproved_count'] == 2
    assert response.context_data['total_hours'] == 2
