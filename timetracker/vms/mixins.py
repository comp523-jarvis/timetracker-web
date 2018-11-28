import datetime


class DateRangeMixin(object):
    """
    Mixin providing functionality for filtering by a date range.

    The starting and ending times are specified as GET parameters.
    """
    DATE_FMT = '%Y-%m-%d'
    END_OFFSET = datetime.timedelta(
        hours=23,
        minutes=59,
        seconds=59,
    )

    context_end_date = 'end_date'
    context_start_date = 'start_date'
    end_date_param = 'end_date'
    start_date_param = 'start_date'

    @property
    def end_date(self):
        """
        Returns:
            The end date provided in the URL. If both a start and end
            date are specified and the end date is prior to the start
            date, the start date is returned instead.

            Note the end date is specified as a datetime so that we can
            include results for the entire day. This results in an
            inclusive bound which is more intuitive.
        """
        date_str = self.request.GET.get(self.end_date_param)

        if not date_str:
            return None

        try:
            date = datetime.datetime.strptime(
                date_str,
                self.DATE_FMT,
            )
        except ValueError:
            return None

        date += self.END_OFFSET

        if self.start_date and self.start_date > date:
            return self.start_date + self.END_OFFSET

        return date

    def filter_by_date(
        self,
        queryset,
        start_attr='time_start',
        end_attr='time_end',
    ):
        """
        Filter a queryset based on a date range.

        If either bound is not provided, it is not restricted.

        Args:
            queryset:
                The queryset to filter.
            start_attr:
                The attribute on the queryset that should be compared to
                the start time given in the URL.
            end_attr:
                The attribute on the queryset that should be compared to
                the end time given in the URL.

        Returns:
            The provided queryset filtered such that no record's
            ``start_attr`` is before the start time in the URL and no
            record's ``end_attr`` is after the end time in the URL.
        """
        start_filter = f'{start_attr}__gte'
        end_filter = f'{end_attr}__lte'

        if self.start_date:
            queryset = queryset.filter(**{start_filter: self.start_date})

        if self.end_date:
            queryset = queryset.filter(**{end_filter: self.end_date})

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add date context to the view.

        Args:
            **kwargs:
                Keyword arguments to pass to the base method.

        Returns:
            A dictionary containing context used to render the view.
        """
        context = super().get_context_data(**kwargs)

        context[self.context_end_date] = self.end_date
        context[self.context_start_date] = self.start_date

        return context

    @property
    def start_date(self):
        """
        Returns:
            The start date provided in the URL as a datetime instance.
        """
        date_str = self.request.GET.get(self.start_date_param)

        if not date_str:
            return None

        try:
            return datetime.datetime.strptime(
                date_str,
                self.DATE_FMT,
            )
        except ValueError:
            return None
