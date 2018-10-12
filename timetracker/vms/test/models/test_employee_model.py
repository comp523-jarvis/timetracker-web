def test_string_conversion(employee_factory):
    """
    Converting an employee to a string should return a string with the
    employee's name and staffing agency.
    """
    employee = employee_factory()
    expected = f'{employee.user.name} (Hired by {employee.staffing_agency})'

    assert str(employee) == expected
