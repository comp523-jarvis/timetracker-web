

def test_string_conversion(staffing_agency_employee_factory):
    """
    Converting a staffing agency employee to a string should return the
    names of the employee and staffing agency.
    """
    employee = staffing_agency_employee_factory()
    expected = f"{employee.user.name} contracted by {employee.agency.name}"

    assert str(employee) == expected
