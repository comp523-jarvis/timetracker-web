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

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        model = model_class(*args, **kwargs)
        model.clean()
        model.save()

        return model


class ClientJobFactory(factory.django.DjangoModelFactory):
    """
    Factory for generating test client jobs.
    """
    client = factory.SubFactory('vms.test.conftest.ClientFactory')
    name = factory.Sequence(lambda n: f'Job {n}')
    pay_rate = 15

    class Meta:
        model = 'vms.ClientJob'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        model = super()._create(model_class, *args, **kwargs)

        model.clean()
        model.save()

        return model


class EmployeeFactory(factory.django.DjangoModelFactory):
    """
    Factory for generating test employees.
    """
    client = factory.SubFactory('vms.test.conftest.ClientFactory')
    staffing_agency = factory.SubFactory(
        'vms.test.conftest.StaffingAgencyFactory',
    )
    user = factory.SubFactory('conftest.UserFactory')

    class Meta:
        model = 'vms.Employee'


class StaffingAgencyAdminFactory(factory.django.DjangoModelFactory):
    """
    Factory for generating test staffing agency admins.
    """
    agency = factory.SubFactory('vms.test.conftest.StaffingAgencyFactory')
    user = factory.SubFactory('conftest.UserFactory')

    class Meta:
        model = 'vms.StaffingAgencyAdmin'


class StaffingAgencyFactory(factory.django.DjangoModelFactory):
    """
    Factory for generating test staffing agencies.
    """
    email = factory.LazyAttribute(lambda o: f'{slugify(o.name)}@example.com')
    name = factory.Sequence(lambda n: f'Staffing Agency {n}')

    class Meta:
        model = 'vms.StaffingAgency'


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
    job = factory.SubFactory('vms.test.conftest.ClientJobFactory')

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
def client_job_factory(db):
    """
    Fixture to get the factory used to create client jobs.
    """
    return ClientJobFactory


@pytest.fixture
def employee_factory(db):
    """
    Fixture to get the factory used to create employees.
    """
    return EmployeeFactory


@pytest.fixture
def staffing_agency_admin_factory(db):
    """
    Fixture to get the factory used to create staffing agency admins.
    """
    return StaffingAgencyAdminFactory


@pytest.fixture
def staffing_agency_factory(db):
    """
    Fixture to get the factory used to create staffing agencies.
    """
    return StaffingAgencyFactory


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
