from django import forms
from django.utils.translation import ugettext as _

from vms import models


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
        models.TimeRecord.objects.create(employee=self.employee)
        print('Clocked in', self.employee)
