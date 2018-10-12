def test_string_conversion(client_admin_factory):
    """
    Converting a client admin to a string should return a string
    containing the name of the admin user and the name of the client.
    """
    admin = client_admin_factory()
    expected = f'{admin.client.name} admin {admin.user.name}'

    assert str(admin) == expected
