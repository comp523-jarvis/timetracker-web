import logging

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext as _

from vms import models


logger = logging.getLogger(__name__)


class ClockInForm(forms.Form):
    """
    Form to clock in the requesting user.
    """
    job = forms.ModelChoiceField(empty_label=None, queryset=None)

    def __init__(self, employee, *args, **kwargs):
        """
        Instantiate the form to clock in a specific employee.

        Args:
            employee:
                The employee that will be clocked in.
            *args:
                Positional arguments for the base form class.
            **kwargs:
                Keyword arguments for the base form class.
        """
        super().__init__(*args, **kwargs)

        self.employee = employee
        self.fields['job'].queryset = models.ClientJob.objects.filter(
            client=employee.client,
        )

    def clean(self):
        """
        Validate the form to ensure the employee is not already clocked
        in.
        """
        if not self.employee.is_active:
            raise forms.ValidationError(
                _('Inactive employees are not allowed to clock in.'),
            )

        if self.employee.is_clocked_in:
            raise forms.ValidationError(
                _('You are already clocked in.')
            )

    def save(self):
        """
        Save the form to create a new time record.
        """
        record = models.TimeRecord.objects.create(
            employee=self.employee,
            pay_rate=self.cleaned_data.get('job').pay_rate,
            **self.cleaned_data,
        )
        logger.info('Created time record %r', record)


class ClockOutForm(forms.Form):
    """
    Form to clock out an employee.
    """

    def __init__(self, employee, *args, **kwargs):
        """
        Initialize the form with an employee.

        Args:
            employee:
                The employee to clock out.
            *args:
                Positional arguments to initialize the form with.
            **kwargs:
                Keyword arguments to initialize the form with.
        """
        super().__init__(*args, **kwargs)

        self.employee = employee

    def clean(self):
        """
        Validate the form's data.

        Raises:
            forms.ValidationError:
                If the employee is not clocked in.
        """
        if not self.employee.is_clocked_in:
            raise forms.ValidationError(
                _('You must be clocked in to clock out.'),
            )

    def save(self):
        """
        Complete the employee's open time record.
        """
        record = self.employee.time_records.get(time_end=None)
        record.time_end = timezone.now()
        record.save()

        logger.info('Completed time record %r', record)


class CreateStaffAgencyForm(forms.Form):
    """
    Form to create staffing agency.
    """
    email_field = forms.EmailField(required=True)
    name_field = forms.CharField(required=True)
    notes_field = forms.CharField(required=False, widget=forms.Textarea)
    regex = '^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-'\
        '. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$'
    phone_number_field = forms.RegexField(regex=regex, required=False)

    def save(self, user):
        agency = models.StaffingAgency.objects.create(
            email=self.data.get('email_field'),
            name=self.data.get('name_field'),
            notes=self.data.get('notes_field'),
            phone_number=self.data.get('phone_number_field')
            )
        models.StaffingAgencyAdmin.objects.create(
            user=user,
            agency=agency
        )


class TimeRecordApprovalForm(forms.Form):
    """
    Form to approve a time record.
    """

    def __init__(self, time_record, approving_user, *args, **kwargs):
        """
        Initialize the form with the time record being approved and the
        supervisor doing the approval.

        Args:
            time_record:
                The time record being approved.
            approving_user:
                The user who is approving the time record.
            *args:
                Positional arguments for the base form class.
            **kwargs:
                Keyword arguments for the base form class.
        """
        super().__init__(*args, **kwargs)

        self.time_record = time_record
        self.approving_user = approving_user

    def save(self):
        """
        Create an approval for the time record associated with the form.

        Returns:
            The approval instance created for the time record.
        """
        return models.TimeRecordApproval.objects.create(
            time_record=self.time_record,
            user=self.approving_user,
        )
