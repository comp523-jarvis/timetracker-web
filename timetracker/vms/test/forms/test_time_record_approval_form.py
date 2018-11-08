from vms import forms


def test_save_valid_form(time_record_factory, user_factory):
    """
    Saving a valid form should create an approval record for the time
    record associated with the form.
    """
    time_record = time_record_factory()
    user = user_factory()

    form = forms.TimeRecordApprovalForm(time_record, user)
    form.save()

    assert time_record.is_approved
    assert time_record.approval.user == user
