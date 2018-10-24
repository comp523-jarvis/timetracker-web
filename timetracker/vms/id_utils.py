import logging
import secrets

from django.conf import settings


logger = logging.getLogger(__name__)


def generate_numeric_id(num_digits):
    """
    Generate a numeric ID with the provided number of digits.

    Args:
        num_digits:
            The number of digits present in the returned ID.

    Returns:
        A random ID with the specified number of digits.
    """
    if num_digits < 1:
        raise ValueError('The number of digits in the ID must be at least 1.')

    lower_bound = 10 ** (num_digits - 1)
    upper_bound = 10 ** num_digits - 1

    # Random generates a number in the range [0, bound), so we have to
    # offset it by our lower bound.
    rand_bound = upper_bound - lower_bound + 1

    return secrets.randbelow(rand_bound) + lower_bound


def generate_unique_id(digits, queryset, queryset_attr='id'):
    """
    Generate a unique ID for a given queryset.

    The provided ID is guaranteed to be unique for the provided
    queryset.

    warning ..

        There is still a race condition between when the value is
        returned from the function and when it is saved to an instance.

    Args:
        digits:
            The number of digits in the returned ID.
        queryset:
            The queryset used to check for uniqueness.
        queryset_attr:
            The attribute of the queryset to check for uniqueness.
            Defaults to ``id``.

    Returns:
        A unique ID for the provided queryset of objects.
    """
    value = generate_numeric_id(digits)

    attempts = 1
    while queryset.filter(**{queryset_attr: value}).exists():
        if attempts == settings.ID_GENERATION_ATTEMPTS_NOTICE:
            logger.info(
                'Taking more than 10 attempts to generate unique ID for %s',
                queryset,
            )
        elif attempts == settings.ID_GENERATION_ATTEMPTS_WARNING:
            logger.warning(
                'Taking more than 100 attempts to generate unique ID for %s',
                queryset,
            )
        elif attempts == settings.ID_GENERATION_ATTEMPTS_FAIL:
            logger.error(
                'Bailing after 1000 attempts to generate a unique ID for %s.',
                queryset,
            )

            raise RuntimeError(
                'Failed to generate a unique ID after 1000 attempts.',
            )

        value = generate_numeric_id(digits)
        attempts += 1

    return value
