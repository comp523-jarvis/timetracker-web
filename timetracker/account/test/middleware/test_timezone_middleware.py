from unittest import mock

import pytest
import pytz
from django.contrib.auth.models import AnonymousUser

from account import middleware


@pytest.fixture
def middleware_instance() -> middleware.TimezoneMiddleware:
    """
    Fixture to get an instance of the ``TimezoneMiddleware`` class.
    """
    get_response = mock.MagicMock(name='Mock get_response')

    return middleware.TimezoneMiddleware(get_response)


@pytest.fixture
def middleware_request(request_factory):
    """
    Return a generic request that can be used to test middleware.
    """
    request = request_factory.get('/')
    request.session = {}
    request.user = AnonymousUser()

    return request


@pytest.fixture
def mock_timezone():
    """
    Fixture to get a mock version of Django's timezone utilities.
    """
    with mock.patch(
        'account.middleware.timezone',
        autospec=True,
    ) as mock_timezone:
        yield mock_timezone


def test_no_timezone_anonymous_user(
        middleware_instance,
        middleware_request,
        mock_timezone):
    """
    If there is no timezone in the current session and the current user
    is anonymous, timezone support should be deactivated.
    """
    middleware_instance(middleware_request)

    assert mock_timezone.deactivate.call_count == 1
    assert middleware_instance.get_response.call_count == 1
    assert middleware_instance.get_response.call_args[0] == (
        middleware_request,
    )


def test_no_timezone_authenticated_user(
        middleware_instance,
        middleware_request,
        mock_timezone,
        user_factory):
    """
    If there is no timezone in the session but the user is
    authenticated, the user's timezone should be used and set in the
    session.
    """
    user = user_factory()
    middleware_request.user = user

    middleware_instance(middleware_request)

    assert mock_timezone.activate.call_args[0] == (user.timezone,)
    assert middleware_request.session['django_timezone'] == user.timezone
    assert middleware_instance.get_response.call_count == 1
    assert middleware_instance.get_response.call_args[0] == (
        middleware_request,
    )


def test_timezone_invalid(
        middleware_instance,
        middleware_request,
        mock_timezone):
    """
    If the timezone set in the session is invalid, timezone support
    should be disabled.
    """
    mock_timezone.activate = mock.MagicMock(
        side_effect=pytz.UnknownTimeZoneError,
    )

    middleware_request.session['django_timezone'] = 'foo'

    middleware_instance(middleware_request)

    assert mock_timezone.deactivate.call_count == 1
    assert middleware_instance.get_response.call_count == 1
    assert middleware_instance.get_response.call_args[0] == (
        middleware_request,
    )


def test_timezone_valid(
        middleware_instance,
        middleware_request,
        mock_timezone):
    """
    If the request session has a valid timezone set, that timezone
    should be activated.
    """
    middleware_request.session['django_timezone'] = 'America/New_York'

    middleware_instance(middleware_request)

    assert mock_timezone.activate.call_count == 1
    assert mock_timezone.activate.call_args[0] == (
        middleware_request.session['django_timezone'],
    )
    assert middleware_instance.get_response.call_count == 1
    assert middleware_instance.get_response.call_args[0] == (
        middleware_request,
    )
