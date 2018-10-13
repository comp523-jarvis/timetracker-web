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
