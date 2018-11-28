import datetime

from django.views.generic.base import ContextMixin

from vms import mixins


class MockQueryset:
    """
    Mock queryset used to track filter calls.
    """
    def __init__(self):
        """
        Initialize the filter call tracker.
        """
        self.filter_kwargs = {}

    def filter(self, **kwargs):
        """
        Update the filter parameters with the most recent call.

        Args:
            **kwargs:
                The filter criteria.

        Returns:
            The instance.
        """
        self.filter_kwargs.update(kwargs)

        return self


def test_end_date(request_factory):
    """
    If an end date is provided as a GET parameter, it should be
    returned.
    """
    date = '2018-11-28'

    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get('/', {'end_date': date})

    assert mixin.end_date == datetime.datetime(
        2018,
        11,
        28,
        23,
        59,
        59,
    )


def test_end_date_before_start_date(request_factory):
    """
    If the end date is prior to the start date, the start date should be
    returned.
    """
    start = '2018-11-29'
    end = '2018-11-28'

    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get(
        '/',
        {
            'end_date': end,
            'start_date': start,
        }
    )

    assert mixin.end_date == datetime.datetime(
        2018,
        11,
        29,
        23,
        59,
        59,
    )


def test_end_date_malformed(request_factory):
    """
    If the end date is malformed, ``None`` should be returned.
    """
    date = 'foobar'

    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get('/', {'end_date': date})

    assert mixin.end_date is None


def test_end_date_not_specified(request_factory):
    """
    If the GET parameters do not include an end date, ``None`` should be
    returned.
    """
    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get('/')

    assert mixin.end_date is None


def test_filter_by_date_end(request_factory):
    """
    If only an end date is provided, the queryset should be filtered by
    the end date.
    """
    queryset = MockQueryset()
    end = '2018-11-29'

    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get('/', {'end_date': end})

    result = mixin.filter_by_date(queryset, end_attr='end')

    assert result.filter_kwargs == {
        'end__lte': mixin.end_date,
    }


def test_filter_by_date_start(request_factory):
    """
    The mixin should allow for filtering only by a start date.
    """
    queryset = MockQueryset()
    start = '2018-11-29'

    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get('/', {'start_date': start})

    result = mixin.filter_by_date(queryset, start_attr='start')

    assert result.filter_kwargs == {
        'start__gte': mixin.start_date,
    }


def test_filter_by_date_start_and_end(request_factory):
    """
    If an end date and start date are specified, the queryset should be
    filtered by both.
    """
    queryset = MockQueryset()

    start = '2018-11-28'
    end = '2018-11-29'

    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get(
        '/',
        {
            'end_date': end,
            'start_date': start,
        }
    )

    result = mixin.filter_by_date(
        queryset,
        end_attr='end',
        start_attr='start',
    )

    assert result.filter_kwargs == {
        'end__lte': mixin.end_date,
        'start__gte': mixin.start_date,
    }


def test_get_context_data(request_factory):
    """
    The context returned from the mixin should include the start and end
    date provided as GET parameters.
    """
    # Create a class using the mixin
    class Dummy(mixins.DateRangeMixin, ContextMixin):
        pass

    start = '2018-11-28'
    end = '2018-11-29'

    view = Dummy()
    view.request = request_factory.get(
        '/',
        {
            'end_date': end,
            'start_date': start,
        },
    )
    context = view.get_context_data()

    assert context['end_date'] == view.end_date
    assert context['start_date'] == view.start_date


def test_start_date(request_factory):
    """
    If a start date is provided as a GET parameter, it should be
    returned.
    """
    date = '2018-11-28'

    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get('/', {'start_date': date})

    assert mixin.start_date == datetime.datetime(2018, 11, 28)


def test_start_date_malformed(request_factory):
    """
    If an invalid start date is specified, ``None`` should be returned.
    """
    date = 'foobar'

    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get('/', {'start_date': date})

    assert mixin.start_date is None


def test_start_date_not_specified(request_factory):
    """
    If the GET parameters do not include a start date, ``None`` should
    be returned.
    """
    mixin = mixins.DateRangeMixin()
    mixin.request = request_factory.get('/')

    assert mixin.start_date is None
