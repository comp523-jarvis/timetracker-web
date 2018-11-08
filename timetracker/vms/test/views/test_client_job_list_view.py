def test_GET_client_admin(client, client_admin_factory, client_job_factory):
    """
    Sending a GET request to the view as a client administrator should
    list all the jobs for the client.
    """
    admin = client_admin_factory()
    client.force_login(admin.user)

    client_company = admin.client
    client_job_factory(client=client_company)
    client_job_factory(client=client_company)

    url = client_company.job_list_url
    response = client.get(url)

    expected_jobs = client_company.jobs.all()

    assert response.status_code == 200
    assert response.context_data['client'] == client_company
    assert list(response.context_data['jobs']) == list(expected_jobs)


def test_GET_other_user(client, client_factory, user_factory):
    """
    Sending a GET request to the view as a non-administrator should
    return a 404 response.
    """
    user = user_factory()
    client.force_login(user)

    client_company = client_factory()

    url = client_company.job_list_url
    response = client.get(url)

    assert response.status_code == 404
