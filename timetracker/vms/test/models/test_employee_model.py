import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from vms import models


def test_approve(client_admin_factory, employee_factory):
    """
    Approving an employee should save the approval information and mark
    the employee as active.
    """
    employee = employee_factory(is_active=False)
    admin = client_admin_factory(client=employee.client)

    employee.approve(admin)
    employee.refresh_from_db()

    assert employee.approved_by == admin
    assert employee.is_active
    assert employee.time_approved is not None


def test_approve_already_approved(client_admin_factory, employee_factory):
    """
    If the employee is already approved, no action should be taken.
    """
    admin = client_admin_factory()
    time = timezone.now()
    employee = employee_factory(
        approved_by=admin,
        client=admin.client,
        is_active=True,
        time_approved=time,
    )

    employee.approve(admin)
    employee.refresh_from_db()

    assert employee.approved_by == admin
    assert employee.time_approved == time


def test_clock_in_url(employee_factory):
    """
    This property should return the URL of the view used to clock in an
    employee.
    """
    employee = employee_factory()
    expected = reverse(
        'vms:clock-in',
        kwargs={
            'client_slug': employee.client.slug,
            'employee_id': employee.employee_id,
        },
    )

    assert employee.clock_in_url == expected


def test_clock_out_url(employee_factory):
    """
    This property should return the URL of the view used to clock out an
    employee.
    """
    employee = employee_factory()
    expected = reverse(
        'vms:clock-out',
        kwargs={
            'client_slug': employee.client.slug,
            'employee_id': employee.employee_id,
        },
    )

    assert employee.clock_out_url == expected


def test_save_new_employee(
        client_factory,
        staffing_agency_factory,
        user_factory):
    """
    Saving a new employee should generate a unique ID for the employee.
    """
    employee = models.Employee(
        client=client_factory(),
        staffing_agency=staffing_agency_factory(),
        user=user_factory()
    )
    employee.save()

    assert employee.employee_id is not None


def test_save_old_employee(employee_factory):
    """
    Saving an existing employee with an ID should not generate a new ID.
    """
    emp = employee_factory()
    old_id = emp.employee_id

    emp.save()

    assert emp.employee_id == old_id


def test_string_conversion(employee_factory):
    """
    Converting an employee to a string should return a string with the
    employee's name and staffing agency.
    """
    employee = employee_factory()
    expected = f'{employee.user.name} (Hired by {employee.staffing_agency})'

    assert str(employee) == expected


def test_validate_unique_excluded(employee_factory):
    """
    If an employee has a duplicate ID but the field is excluded from the
    check, the validation should pass.
    """
    emp1 = employee_factory()
    emp2 = employee_factory(client=emp1.client)

    emp1.employee_id = emp2.employee_id

    emp1.validate_unique(exclude=['employee_id'])


def test_validate_unique_new_employee_duplicate_id(
        employee_factory,
        user_factory):
    """
    If there is already an employee working for the same client with the
    same ID, the unique validation should fail.
    """
    old_emp = employee_factory()
    new_emp = models.Employee(
        client=old_emp.client,
        employee_id=old_emp.employee_id,
        staffing_agency=old_emp.staffing_agency,
        user=user_factory(),
    )

    with pytest.raises(ValidationError):
        new_emp.validate_unique()


def test_validate_unique_new_employee_unique_id(
        client_factory,
        employee_factory,
        user_factory):
    """
    If two employees have the same ID but work for different clients,
    the validation should succeed.
    """
    old_emp = employee_factory()
    new_emp = models.Employee(
        client=client_factory(),
        employee_id=old_emp.employee_id,
        staffing_agency=old_emp.staffing_agency,
        user=user_factory(),
    )

    new_emp.validate_unique()


def test_validate_unique_old_employee_duplicate_id(employee_factory):
    """
    If an existing employee's ID is changed to match the ID of another
    employee working for the same client, the validation should fail.
    """
    emp1 = employee_factory()
    emp2 = employee_factory(client=emp1.client)

    emp1.employee_id = emp2.employee_id

    with pytest.raises(ValidationError):
        emp1.validate_unique()


def test_validate_unique_old_employee_unique_id(employee_factory):
    """
    An existing employee with a unique ID should pass validation.
    """
    emp = employee_factory()
    emp.validate_unique()
