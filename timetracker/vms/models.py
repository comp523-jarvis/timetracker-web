import datetime
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Employee(models.Model):
    """
    An employee working for a specific company.
    """
    company = models.CharField(
        help_text=_('The name of the company the employee works for.'),
        max_length=100,
        verbose_name=_('company name'),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('A boolean indicating if this user is currently active. '
                    'Inactive employees log any working hours.'),
        verbose_name=_('is active'),
    )
    supervisor = models.CharField(
        help_text=_("The employee's supervisor."),
        max_length=100,
        verbose_name=_('supervisor'),
    )
    time_created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('The time the employee was created.'),
        verbose_name=_('time created'),
    )
    time_updated = models.DateTimeField(
        auto_now=True,
        help_text=_('The time the employee was last updated.'),
        verbose_name=_('time updated'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_('The user account the employee is attached to.'),
        on_delete=models.CASCADE,
        related_name='employees',
        related_query_name='employee',
        verbose_name=_('user'),
    )

    class Meta:
        ordering = ('time_created',)
        verbose_name = _('employee')
        verbose_name_plural = _('employees')

    def __repr__(self):
        """
        Get a string representation of the employee.

        Returns:
            A string containing the information required to reconstruct
            the employee.
        """
        return (
            f'Employee(id={self.id:r}, user_id={self.user.id:r}, '
            f'company={self.company:r}, supervisor={self.supervisor:r})'
        )

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string containing the name of the user who owns the
            employee instance.
        """
        return f'{self.user.name} ({self.company})'

    @property
    def is_clocked_in(self):
        """
        Determine if the employee is currently clocked in.

        Returns:
            A boolean indicating if the employee is clocked in.
        """
        return self.time_records.filter(time_end=None).exists()

    @property
    def total_time(self):
        """
        Get the total time that the employee has logged.

        Returns:
            The total time the employee has worked in seconds, rounded
            to the nearest 15 minute increment.
        """
        hours = datetime.timedelta(0)
        for record in self.time_records.exclude(time_end=None):
            hours += record.time_end - record.time_start

        return hours.total_seconds()


class TimeRecord(models.Model):
    """
    A record marking a work period for an employee.
    """
    employee = models.ForeignKey(
        'vms.Employee',
        help_text=_('The employee who worked during this time period.'),
        on_delete=models.CASCADE,
        related_name='time_records',
        related_query_name='time_record',
        verbose_name=_('employee'),
    )
    id = models.UUIDField(
        default=uuid.uuid4,
        help_text=_('A unique identifier for the time record.'),
        primary_key=True,
        unique=True,
        verbose_name=_('ID'),
    )
    is_approved = models.BooleanField(
        default=False,
        help_text=_("A boolean indicating if the time record has been "
                    "approved by the employee's manager."),
        verbose_name=_('is approved'),
    )
    time_end = models.DateTimeField(
        blank=True,
        help_text=_('The ending time of the work period.'),
        null=True,
        verbose_name=_('end time'),
    )
    time_start = models.DateTimeField(
        default=timezone.now,
        help_text=_('The start time of the work period.'),
        verbose_name=_('start time'),
    )

    class Meta:
        ordering = ('time_start',)
        verbose_name = _('time record')
        verbose_name_plural = _('time records')

    def __repr__(self):
        """
        Get a string representation of the instance.

        Returns:
            A string containing the information required to reconstruct
            the time record.
        """
        return (
            f'TimeRecord(id={self.id:r}, employee_id={self.employee.id:r}, '
            f'time_start={self.time_start:r}, time_end={self.time_end:r})'
        )

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string describing the time record including the start and
            end times.
        """
        if self.time_end:
            return f'Time Record from {self.time_start} to {self.time_end}'

        return f'Time Record starting at {self.time_start}'
