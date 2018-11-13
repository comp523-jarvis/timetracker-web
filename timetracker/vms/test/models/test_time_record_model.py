import datetime

from django.utils import timezone

from vms import models


def test_is_approved_no_approval(time_record_factory):
    """
    If there is no approval record for the time record, the property
    should be ``False``.
    """
    record = time_record_factory()

    assert not record.is_approved


def test_is_approved_with_approval(time_record_approval_factory):
    """
    If there is an approval record for the time record, the property
    should be ``True``.
    """
    approval = time_record_approval_factory()
    record = approval.time_record

    assert record.is_approved


def test_queryset_with_deltas(time_record_factory):
    """
    This queryset method should annotate all completed time records
    with the delta between their start and end times.
    """
    now = timezone.now()
    time_record_factory(time_start=now)
    t1 = time_record_factory(
        time_end=now + datetime.timedelta(days=1),
        time_start=now,
    )
    t2 = time_record_factory(
        time_end=now + datetime.timedelta(hours=1),
        time_start=now,
    )

    records = models.TimeRecord.objects.with_deltas()

    # Only records with an end time should be included
    assert list(records) == [t1, t2]

    # Each record should be annotated with its delta
    for record in records:
        assert record.delta == record.time_end - record.time_start


def test_queryset_total_time(time_record_factory):
    """
    This queryset method should return the sum of the deltas of each of
    the time records in the queryset.
    """
    now = timezone.now()
    later = now + datetime.timedelta(hours=1)

    time_record_factory(time_end=later, time_start=now)
    time_record_factory(time_end=later, time_start=now)

    expected = sum(
        (record.delta for record in models.TimeRecord.objects.with_deltas()),
        datetime.timedelta(0),
    )

    assert models.TimeRecord.objects.total_time() == expected


def test_repr_with_job(time_record_factory):
    """
    Getting the repr of a time record should return a string with the
    information necessary to reconstruct it.
    """
    record = time_record_factory()
    expected = (
        f'TimeRecord('
        f'id={record.id!r}, '
        f'job_id={record.job.id!r}, '
        f'employee_id={record.employee.id!r}, '
        f'time_start={record.time_start!r}, '
        f'time_end={record.time_end!r})'
    )

    assert repr(record) == expected


def test_repr_without_job(time_record_factory):
    """
    If the time record has no associated job, the repr should still
    work.
    """
    record = time_record_factory(job=None)
    expected = (
        f'TimeRecord('
        f'id={record.id!r}, '
        f'job_id={record.job!r}, '
        f'employee_id={record.employee.id!r}, '
        f'time_start={record.time_start!r}, '
        f'time_end={record.time_end!r})'
    )

    assert repr(record) == expected


def test_1_time_string_conversion(time_record_factory):
    """
    Case with no end time
    """
    t = time_record_factory()
    expected = (
        f'Time Record starting at {t.time_start:%I:%M %p}'
        f' on {t.time_start:%m/%d/%Y}.'
    )
    assert str(t) == expected


def test_2_time_string_conversion(time_record_factory):
    """
    Case with different end times
    """
    t = time_record_factory(time_end=datetime.datetime(2020, 10, 1, 15, 26))
    expected = (
        f'Time Record from {t.time_start:%I:%M %p on %m/%d/%Y}, '
        f'{t.time_end:%I:%M %p on %m/%d/%Y}.'
    )
    assert str(t) == expected


def test_3_time_string_conversion(time_record_factory):
    """
    Case with same end times
    """
    d = datetime.datetime(2018, 10, 1, 15, 26)
    t = time_record_factory(time_start=d, time_end=d)
    expected = (
        f'Time Record from {t.time_start:%I:%M %p} to '
        f'{t.time_end:%I:%M %p} on {t.time_start:%m/%d/%Y}.'
    )
    assert str(t) == expected


def test_total_time_no_end_time(time_record_factory):
    """
    Case with no end time
    """
    d = datetime.datetime(2018, 10, 1, 15, 26)
    t = time_record_factory(time_start=d, time_end=None)
    expected = datetime.timedelta(0)
    assert t.total_time == expected


def test_total_time_with_start_and_end_times(time_record_factory):
    """
    Case with start and end times. Same day, 9-5 workday
    """
    ts = datetime.datetime(2018, 10, 1, 9, 0)
    te = datetime.datetime(2018, 10, 1, 17, 0)

    t = time_record_factory(time_start=ts, time_end=te)

    expected = te-ts

    assert t.total_time == expected


def test_total_time_projected_earnings(time_record_factory):
    ts = datetime.datetime(2018, 10, 1, 9, 0)
    te = datetime.datetime(2018, 10, 1, 17, 0)

    t = time_record_factory(time_start=ts, time_end=te)

    expected = (t.total_time.total_seconds() / (60*60)) * t.pay_rate

    assert t.projected_earnings == expected
