import datetime
import logging
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger(__name__)


def generate_slug(value, queryset, slug_dest='slug'):
    """
    Generate and save a unique slug for the provided instance.

    Args:
        value:
            The value to slugify.
        queryset:
            The queryset to search to ensure the generated slug is
            unique.
        slug_dest:
            The name of the attribute on the instance that the slug is
            saved to.
    """
    logger.debug('Generating unique slug for value %s', value)

    base = slugify(value)[:settings.SLUG_LENGTH]
    suffix = ''

    while queryset.filter(**{slug_dest: f'{base}{suffix}'}).exists():
        logger.debug('Slug %s%s is not unique', base, suffix)

        suffix = f'-{get_random_string(settings.SLUG_KEY_LENGTH)}'

    return f'{base}{suffix}'


class Client(models.Model):
    """
    A client is a company that employees perform work for.
    """
    email = models.EmailField(
        help_text=_('The primary email address for the client.'),
        verbose_name=_('primary email address'),
    )
    name = models.CharField(
        help_text=_('The name of the client company.'),
        max_length=100,
        verbose_name=_('name'),
    )
    notes = models.TextField(
        blank=True,
        help_text=_('Additional information about the client.'),
        verbose_name=_('notes'),
    )
    phone_number = models.CharField(
        blank=True,
        help_text=_('The phone number that the client can be reached at.'),
        max_length=30,
        verbose_name=_('phone number'),
    )
    slug = models.SlugField(
        help_text=_('The URL slug used to look up the client.'),
        max_length=settings.SLUG_LENGTH_TOTAL,
        verbose_name=_('slug'),
    )
    time_created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('The time the client was created.'),
        verbose_name=_('creation time'),
    )
    time_updated = models.DateTimeField(
        auto_now=True,
        help_text=_("The last time the client's information was updated."),
        verbose_name=_('last update time'),
    )

    class Meta:
        ordering = ('name', 'time_created',)
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    def save(self, *args, **kwargs):
        """
        Save the client, creating a slug if necessary.

        Args:
            *args:
                Positional arguments to pass to the original save
                method.
            **kwargs:
                Keyword arguments to pass to the original save method.
        """
        # TODO: Fix the race condition here

        # There is a race condition here where the slug is generated and
        # unique among the current clients, but a new client with the
        # same slug is saved before we get to the save call below.
        if not self.slug:
            self.slug = generate_slug(self.name, Client.objects.all())

        super().save(*args, **kwargs)

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            The client's name.
        """
        return self.name


class ClientAdmin(models.Model):
    """
    A link between a user and a client that grants the linked user admin
    permissions on the associated client company.
    """
    client = models.ForeignKey(
        'vms.Client',
        help_text=_('The client company that the user has admin rights to.'),
        on_delete=models.CASCADE,
        related_name='admins',
        related_query_name='admin',
        verbose_name=_('client'),
    )
    time_created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('The time the admin was created at.'),
        verbose_name=_('creation time'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_('The user who has admin rights on the linked client.'),
        on_delete=models.CASCADE,
        related_name='client_admins',
        related_query_name='client_admin',
        verbose_name=_('admin user'),
    )

    class Meta:
        ordering = ('client__name', 'time_created')
        unique_together = ('client', 'user')
        verbose_name = _('client administrator')
        verbose_name_plural = _('client administrators')

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string containing the names of the linked user and client.
        """
        return f'{self.client.name} admin {self.user.name}'


class ClientJob(models.Model):
    """
    A type of task that can be worked on for a specific client.
    """
    client = models.ForeignKey(
        'vms.Client',
        help_text=_('The client that the job is performed for.'),
        on_delete=models.CASCADE,
        related_name='jobs',
        related_query_name='job',
        verbose_name=_('client'),
    )
    description = models.TextField(
        blank=True,
        help_text=_('More details about the job.'),
        verbose_name=_('description'),
    )
    name = models.CharField(
        help_text=_('The name of the job'),
        max_length=100,
        verbose_name=_('name'),
    )
    pay_rate = models.DecimalField(
        decimal_places=2,
        max_digits=11,
    )
    slug = models.SlugField(
        help_text=_('A unique slug that can be used to retrieve the job.'),
        max_length=100,
        verbose_name=_('slug'),
    )

    class Meta:
        ordering = ('name',)
        unique_together = ('client', 'slug')
        verbose_name = _('client job')
        verbose_name_plural = _('client jobs')

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            The job name.
        """
        return self.name


class Employee(models.Model):
    """
    An employee working for a specific company.
    """
    is_active = models.BooleanField(
        default=True,
        help_text=_('A boolean indicating if this user is currently active. '
                    'Inactive employees log any working hours.'),
        verbose_name=_('is active'),
    )
    supervisor = models.ForeignKey(
        'vms.ClientAdmin',
        help_text=_(
            "The client administrator who can approve the user's hours.",
        ),
        null=True,
        on_delete=models.SET_NULL,
        related_name='employees',
        related_query_name='employee',
        verbose_name=_('supervisor'),
    )
    staffing_agency = models.ForeignKey(
        'vms.StaffingAgency',
        help_text=_('The staffing agency that hired the employee.'),
        on_delete=models.CASCADE,
        related_name='employees',
        related_query_name='employee',
        verbose_name=_('staffing agency'),
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

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string containing the name of the user who owns the
            employee instance.
        """
        return f'{self.user.name} (Hired by {self.staffing_agency})'

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


class StaffingAgency(models.Model):
    """
    A company that provides employees to clients.
    """
    email = models.EmailField(
        help_text=_('The primary email address for the agency.'),
        verbose_name=_('primary email address'),
    )
    name = models.CharField(
        help_text=_('The name of the staffing agency.'),
        max_length=100,
        verbose_name=_('name'),
    )
    notes = models.TextField(
        blank=True,
        help_text=_('Additional information about the staffing agency.'),
        verbose_name=_('notes'),
    )
    phone_number = models.CharField(
        blank=True,
        help_text=_('The phone number that the agency can be reached at.'),
        max_length=30,
        verbose_name=_('phone number'),
    )
    slug = models.SlugField(
        help_text=_('The URL slug used to look up the staffing agency.'),
        max_length=settings.SLUG_LENGTH_TOTAL,
        verbose_name=_('slug'),
    )
    time_created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('The time the agency was created.'),
        verbose_name=_('creation time'),
    )
    time_updated = models.DateTimeField(
        auto_now=True,
        help_text=_("The last time the agency's information was updated."),
        verbose_name=_('last update time'),
    )

    class Meta:
        ordering = ('name', 'time_created',)
        verbose_name = _('staffing agency')
        verbose_name_plural = _('staffing agencies')

    def save(self, *args, **kwargs):
        """
        Save the agency, creating a slug if necessary.

        Args:
            *args:
                Positional arguments to pass to the original save
                method.
            **kwargs:
                Keyword arguments to pass to the original save method.
        """
        # TODO: Fix the race condition here

        # There is a race condition here where the slug is generated and
        # unique among the current clients, but a new client with the
        # same slug is saved before we get to the save call below.
        if not self.slug:
            self.slug = generate_slug(self.name, Client.objects.all())

        super().save(*args, **kwargs)

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            The agency's name.
        """
        return self.name


class StaffingAgencyAdmin(models.Model):
    """
    A link between a user and a staffing agency that grants the linked
    user admin permissions on the associated staffing agency.
    """
    agency = models.ForeignKey(
        'vms.StaffingAgency',
        help_text=_('The staffing agency that the user has admin rights to.'),
        on_delete=models.CASCADE,
        related_name='admins',
        related_query_name='admin',
        verbose_name=_('staffing agency'),
    )
    time_created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('The time the admin was created at.'),
        verbose_name=_('creation time'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_('The user who has admin rights on the linked agency.'),
        on_delete=models.CASCADE,
        related_name='agency_admins',
        related_query_name='agency_admin',
        verbose_name=_('admin user'),
    )

    class Meta:
        ordering = ('agency__name', 'user__name', 'time_created')
        unique_together = ('agency', 'user')
        verbose_name = _('staffing agency administrator')
        verbose_name_plural = _('staffing agency administrators')

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string containing the names of the linked user and agency.
        """
        return f'{self.agency.name} admin {self.user.name}'


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
    job = models.ForeignKey(
        'vms.ClientJob',
        help_text=_('The job type that the employee worked on.'),
        null=True,
        on_delete=models.SET_NULL,
        related_name='time_records',
        related_query_name='time_record',
        verbose_name=_('client job'),
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

    @property
    def is_approved(self):
        """
        Determine if the time record is approved.

        Returns:
            A boolean indicating if there is an approval record for the
            time record.
        """
        return hasattr(self, 'approval')


class TimeRecordApproval(models.Model):
    """
    A record of the approval for a time record.
    """
    id = models.UUIDField(
        default=uuid.uuid4,
        help_text=_('A unique identifier for the approval record.'),
        primary_key=True,
        unique=True,
        verbose_name=_('ID'),
    )
    time_approved = models.DateTimeField(
        auto_now_add=True,
        help_text=_('The time that the associated time record was approved.'),
        verbose_name=_('approval time'),
    )
    time_record = models.OneToOneField(
        'vms.TimeRecord',
        help_text=_('The time record that is being approved.'),
        on_delete=models.CASCADE,
        related_name='approval',
        verbose_name=_('time record'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_('The user who approved the time record.'),
        on_delete=models.CASCADE,
        related_name='time_record_approvals',
        related_query_name='time_record_approval',
        verbose_name=_('approving user'),
    )

    class Meta:
        ordering = ('time_approved',)
        verbose_name = _('time record approval')
        verbose_name_plural = _('time record approvals')

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string containing the name of the approved time record.
        """
        return f'Approval for {self.time_record}'
