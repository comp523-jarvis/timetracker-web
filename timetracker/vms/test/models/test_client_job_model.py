def test_string_conversion(client_job_factory):
    """
    Converting a client job to a string should return the name of the
    job.
    """
    job = client_job_factory()

    assert str(job) == job.name
