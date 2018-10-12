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
