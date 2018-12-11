import pytest
import datetime

from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from vms import views


def test_get_object_client_admin(
    client_admin_factory,
    employee_factory,
    request_factory,
):
    """
    If the requesting user is an administrator of the client the
    employee works for, they should be able to access the view.
    """
    admin = client_admin_factory()
    employee = employee_factory(client=admin.client)

    url = employee.get_absolute_url()
    request = request_factory.get(url)
    request.user = admin.user

    view = views.EmployeeDetailView()
    view.kwargs = {
        'client_slug': employee.client.slug,
        'employee_id': employee.employee_id,
    }
    view.request = request

    assert view.get_object() == employee


def test_get_object_invalid_id(client_admin_factory, request_factory):
    """
    If the provided employee ID does not exist, a 404 response should be
    returned.
    """
    admin = client_admin_factory()
    kwargs = {'client_slug': admin.client.slug, 'employee_id': 1}

    url = reverse(
        'vms:employee-dash',
        kwargs=kwargs,
    )
    request = request_factory.get(url)
    request.user = admin.user

    view = views.EmployeeDetailView()
    view.kwargs = kwargs
    view.request = request

    with pytest.raises(Http404):
        view.get_object()


def test_get_object_other_user(
    employee_factory,
    request_factory,
    user_factory,
):
    """
    Users not affiliated with an employee should receive a 404 response
    if they try to view the employee.
    """
    user = user_factory()
    employee = employee_factory()

    url = employee.get_absolute_url()
    request = request_factory.get(url)
    request.user = user

    view = views.EmployeeDetailView()
    view.kwargs = {
        'client_slug': employee.client.slug,
        'employee_id': employee.employee_id,
    }
    view.request = request

    with pytest.raises(Http404):
        view.get_object()


def test_get_object_self(employee_factory, request_factory):
    """
    The employee should be able to fetch their own record.
    """
    employee = employee_factory()

    url = employee.get_absolute_url()
    request = request_factory.get(url)
    request.user = employee.user

    view = views.EmployeeDetailView()
    view.kwargs = {
        'client_slug': employee.client.slug,
        'employee_id': employee.employee_id,
    }
    view.request = request

    assert view.get_object() == employee


def test_get_object_self_and_multiple_admins(
    client_admin_factory,
    employee_factory,
    request_factory,
):
    """
    The employee should be able to fetch their own record if their are
    multiple admins for the client company.

    Regression test for GH-113.

    https://github.com/comp523-jarvis/timetracker-web/issues/113
    """
    admin = client_admin_factory()
    client_admin_factory(client=admin.client)
    employee = employee_factory(
        client=admin.client,
        user=admin.user,
    )

    url = employee.get_absolute_url()
    request = request_factory.get(url)
    request.user = employee.user

    view = views.EmployeeDetailView()
    view.kwargs = {
        'client_slug': employee.client.slug,
        'employee_id': employee.employee_id,
    }
    view.request = request

    assert view.get_object() == employee


def test_get_object_staffer(
    employee_factory,
    request_factory,
    staffing_agency_admin_factory,
):
    """
    Admins of the staffing agency the employee was hired by should be
    able to get the employee instance.
    """
    admin = staffing_agency_admin_factory()
    employee = employee_factory(staffing_agency=admin.agency)

    url = employee.get_absolute_url()
    request = request_factory.get(url)
    request.user = admin.user

    view = views.EmployeeDetailView()
    view.kwargs = {
        'client_slug': employee.client.slug,
        'employee_id': employee.employee_id,
    }
    view.request = request

    assert view.get_object() == employee


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
