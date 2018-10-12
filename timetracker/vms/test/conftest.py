import factory
import pytest
from django.utils.text import slugify


class ClientAdminFactory(factory.django.DjangoModelFactory):
    """
    Factory for generating test client admins.
    """
    client = factory.SubFactory('vms.test.conftest.ClientFactory')
    user = factory.SubFactory('conftest.UserFactory')

    class Meta:
        model = 'vms.ClientAdmin'


class ClientFactory(factory.django.DjangoModelFactory):
    """
    Factory for generating test clients.
    """
    email = factory.LazyAttribute(lambda o: f'{slugify(o.name)}@example.com')
    name = factory.Sequence(lambda n: f'Client {n}')

    class Meta:
        model = 'vms.Client'


class EmployeeFactory(factory.django.DjangoModelFactory):
    """
    Factory for generating test employees.
    """
    company = 'Acme Inc.'
    supervisor = 'John Smith'
    user = factory.SubFactory('conftest.UserFactory')

    class Meta:
        model = 'vms.Employee'


class TimeRecordApprovalFactory(factory.DjangoModelFactory):
    """
    Factory for generating test time record approvals.
    """
    time_record = factory.SubFactory('vms.test.conftest.TimeRecordFactory')
    user = factory.SubFactory('conftest.UserFactory')

    class Meta:
        model = 'vms.TimeRecordApproval'


class TimeRecordFactory(factory.django.DjangoModelFactory):
    """
    Factory for generating test time records.
    """
    employee = factory.SubFactory('vms.test.conftest.EmployeeFactory')

    class Meta:
        model = 'vms.TimeRecord'


@pytest.fixture
def client_admin_factory(db):
    """
    Fixture to get the factory used to create client admins.
    """
    return ClientAdminFactory


@pytest.fixture
def client_factory(db):
    """
    Fixture to get the factory used to create clients.
    """
    return ClientFactory


@pytest.fixture
def employee_factory(db):
    """
    Fixture to get the factory used to create employees.
    """
    return EmployeeFactory


@pytest.fixture
def time_record_approval_factory(db):
    """
    Fixture to get the factory used to create time record approvals.
    """
    return TimeRecordApprovalFactory


@pytest.fixture
def time_record_factory(db):
    """
    Fixture to get the factory used to create time records.
    """
    return TimeRecordFactory
