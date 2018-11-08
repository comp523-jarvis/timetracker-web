

def test_GET_admin(client, client_admin_factory, client_job_factory):
    """
    Sending a GET request to the view as a client admin should return
    the details of the specified job.
    """
    admin = client_admin_factory()
    client.force_login(admin.user)

    job = client_job_factory(client=admin.client)

    url = job.get_absolute_url()
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['job'] == job


def test_GET_non_admin(client, client_job_factory, user_factory):
    """
    Sending a GET request to the view as a non-admin should return a 404
    response.
    """
    client.force_login(user_factory())
    job = client_job_factory()

    url = job.get_absolute_url()
    response = client.get(url)

    assert response.status_code == 404
