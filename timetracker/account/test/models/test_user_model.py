def test_repr(user_factory):
    """
    The repr of a user should contain the information required to
    recreate the user.
    """
    user = user_factory()
    expected = (
        f'User('
        f'id={user.id!r}, '
        f'is_active={user.is_active}, '
        f'is_staff={user.is_staff}, '
        f'is_superuser={user.is_superuser}, '
        f'name={user.name!r}, '
        f'timezone={user.timezone!r}, '
        f'username={user.username!r})'
    )

    assert repr(user) == expected
