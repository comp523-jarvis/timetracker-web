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
