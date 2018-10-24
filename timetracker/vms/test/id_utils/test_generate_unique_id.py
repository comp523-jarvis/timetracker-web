from unittest import mock

import pytest
from django.conf import settings

from vms import id_utils


class MockQuerysetBase:
    def filter(self, **kwargs):
        return self


class MockQuerysetAlways(MockQuerysetBase):
    @staticmethod
    def exists():
        return True


class MockQuerysetNever(MockQuerysetBase):
    @staticmethod
    def exists():
        return False


@mock.patch('vms.id_utils.generate_numeric_id')
def test_generate_id(mock_gen_numeric):
    """
    If the generated ID is unique, it should be returned.
    """
    mock_gen_numeric.return_value = 42
    queryset = MockQuerysetNever()

    value = id_utils.generate_unique_id(2, queryset)

    assert value == mock_gen_numeric.return_value
    assert mock_gen_numeric.call_count == 1


@mock.patch('vms.id_utils.generate_numeric_id')
def test_generate_id_fail(mock_gen_numeric):
    """
    If the method fails to generate a unique ID 1000 times, it should
    bail.
    """
    queryset = MockQuerysetAlways()

    with pytest.raises(RuntimeError):
        id_utils.generate_unique_id(3, queryset)

    assert mock_gen_numeric.call_count == settings.ID_GENERATION_ATTEMPTS_FAIL
