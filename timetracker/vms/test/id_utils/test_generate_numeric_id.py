from unittest import mock

import pytest

from vms import id_utils


@pytest.mark.parametrize('digits', [-4, 0])
def test_generate_no_digits(digits):
    """
    If the number of digits is less than 1, a ``ValueError`` should be
    raised.
    """
    with pytest.raises(ValueError):
        id_utils.generate_numeric_id(digits)


@pytest.mark.parametrize('digits', [1, 2, 3])
def test_generate_valid_id(digits):
    """
    The method should generate a number with the provided number of
    digits.
    """
    lower_bound = 10 ** (digits - 1)
    upper_bound = 10 ** digits - 1
    rand_bound = upper_bound - lower_bound + 1

    with mock.patch(
        'vms.id_utils.secrets.randbelow',
        side_effect=lambda n: n,
    ) as mock_rand:
        result = id_utils.generate_numeric_id(digits)

    assert mock_rand.call_count == 1
    assert mock_rand.call_args[0] == (rand_bound,)

    assert result == rand_bound + lower_bound
