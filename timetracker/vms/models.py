import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Employee(models.Model):
    """
    An employee working for a specific company.
    """
    id = models.UUIDField(
        default=uuid.uuid4,
        help_text=_('A unique identifier for the employee.'),
        primary_key=True,
        unique=True,
        verbose_name=_('ID'),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('A boolean indicating if this user is currently active. '
                    'Inactive employees log any working hours.'),
        verbose_name=_('is active'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_('The user account the employee is attached to.'),
        on_delete=models.CASCADE,
        related_name='employees',
        related_query_name='employee',
        verbose_name=_('user'),
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
    wage = models.DecimalField(
        decimal_places=2,
        help_text=_("The employee's hourly wage."),
        max_digits=10,
        verbose_name=_('hourly wage'),
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
        return f'Employee(id={self.id:r}, user_id={self.user.id:r})'

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string containing the name of the user who owns the
            employee instance.
        """
        return f'Employee {self.user.name}'
