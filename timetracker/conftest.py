import os

import factory
import pytest
from django.conf import settings
from django.test import RequestFactory


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for generating test users.
    """
    name = factory.Sequence(lambda n: f'User {n}')
    password = 'password'
    username = factory.Sequence(lambda n: f'user{n}')

    class Meta:
        model = settings.AUTH_USER_MODEL

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Override to use our custom ``create_user`` method.
        manager = cls._get_manager(model_class)

        return manager.create_user(*args, **kwargs)


@pytest.fixture
def env():
    """
    Fixture to get a mutable copy of the environment that is restored
    once the test is complete.
    """
    original = os.environ.copy()

    os.environ['foo'] = 'bar'
    yield os.environ

    os.environ = original
    assert 'foo' not in os.environ


@pytest.fixture
def request_factory() -> RequestFactory:
    """
    Get a factory used to generate test requests.
    """
    return RequestFactory()


@pytest.fixture
def user_factory(db):
    """
    Fixture to get the factory used to create test users.
    """
    return UserFactory
