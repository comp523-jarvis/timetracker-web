import datetime


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
