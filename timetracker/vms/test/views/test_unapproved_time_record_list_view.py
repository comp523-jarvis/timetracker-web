import datetime

import pytest
from django.utils import timezone


@pytest.mark.integration
def test_GET_as_other_user(client, client_factory, user_factory):
    """
    Sending a GET request to the view as a non-admin user should return
    a 404 response.
    """
    client.force_login(user_factory())
    client_company = client_factory()

    url = client_company.unapproved_time_record_list_url
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.integration
def test_GET_as_supervisor(client, client_admin_factory, time_record_factory):
    """
    Sending a GET request to the view as a client supervisor should
    list the unapproved time records for the client.
    """
    admin = client_admin_factory()
    client.force_login(admin.user)

    start_time = timezone.now()
    end_time = start_time + datetime.timedelta(hours=8)

    client_company = admin.client
    time_record_factory(
        employee__client=client_company,
        job__client=client_company,
        time_start=start_time,
    )
    r1 = time_record_factory(
        employee__client=client_company,
        job__client=client_company,
        time_end=end_time,
        time_start=start_time,
    )
    r2 = time_record_factory(
        employee__client=client_company,
        job__client=client_company,
        time_end=end_time,
        time_start=start_time,
    )

    expected_records = [r1, r2]

    url = client_company.unapproved_time_record_list_url
    response = client.get(url)

    assert response.status_code == 200
    assert list(response.context_data['time_records']) == expected_records
