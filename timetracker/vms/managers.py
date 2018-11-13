from django.db import models
from django.db.models import F, ExpressionWrapper, DurationField, Sum


class TimeRecordQuerySet(models.QuerySet):
    def with_deltas(self):
        """
        Annotate the queryset to include a delta for each time record.

        Because computing a delta relies on ``time_end`` being present,
        time records that have not been completed are excluded.

        Returns:
            A queryset annotated such that each time record has a
            ``delta`` attribute containing the delta between the
            record's ``time_start`` and ``time_end``.
        """
        expression = F('time_end') - F('time_start')
        wrapped_expression = ExpressionWrapper(expression, DurationField())

        return self.exclude(time_end=None).annotate(delta=wrapped_expression)

    def total_time(self):
        """
        Get the total duration of the time records in the queryset.

        Returns:
            The total duration of the time records in the queryset
            expressed as a ``datetime.timedelta`` instance.
        """
        aggregate = self.with_deltas().aggregate(sum=Sum('delta'))

        return aggregate['sum']


TimeRecordManager = TimeRecordQuerySet.as_manager
