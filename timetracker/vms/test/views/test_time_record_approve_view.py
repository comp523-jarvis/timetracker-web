import pytest


@pytest.mark.integration
def test_POST_as_admin(client, client_admin_factory, time_record_factory):
    """
    Sending a POST request to the view as an administrator at the client
    the time record is associated with should create an approval record
    for the time record.
    """
    time_record = time_record_factory()
    admin = client_admin_factory(client=time_record.employee.client)
    client.force_login(admin.user)

    url = time_record.approval_url
    response = client.post(url, {})

    assert response.status_code == 302
    assert response.url == admin.client.unapproved_time_record_list_url
    assert time_record.is_approved


@pytest.mark.integration
def test_POST_as_other_user(client, time_record_factory, user_factory):
    """
    Sending a POST request to the view as a non-admin should return a
    404 response.
    """
    client.force_login(user_factory())
    time_record = time_record_factory()

    url = time_record.approval_url
    response = client.post(url, {})

    assert response.status_code == 404
