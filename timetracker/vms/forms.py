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

    def __init__(self, employee, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.employee = employee

    def clean(self):
        if self.employee.is_clocked_in:
            raise forms.ValidationError(
                _('You are already clocked in.')
            )

    def save(self):
        record = models.TimeRecord.objects.create(employee=self.employee)

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
