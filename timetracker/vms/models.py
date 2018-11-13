import datetime
import decimal
import logging
import uuid

import email_utils
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _, ugettext

from vms import id_utils, managers


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


def generate_token():
    """
    Generate a random token.

    Returns:
        A random 16-character alphanumeric string.
    """
    return get_random_string(16)


class Client(models.Model):
    """
    A client is a company that employees perform work for.
    """
    id = models.PositiveIntegerField(
        blank=True,
        editable=False,
        help_text=_(
            'A unique numeric identifier for the client. If not specified, it '
            'will be randomly generated.'
        ),
        primary_key=True,
        unique=True,
        verbose_name=_('client ID'),
    )
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

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            The client's name.
        """
        return self.name

    def clean(self):
        """
        Generate a unique ID and slug if necessary.
        """
        super().clean()

        if not self.id:
            self.id = id_utils.generate_unique_id(
                settings.CLIENT_ID_LENGTH,
                self.__class__.objects.all(),
            )

        if not self.slug:
            self.slug = generate_slug(self.name, self.__class__.objects.all())

    def get_absolute_url(self):
        """
        Get the URL of the instance's detail view.

        Returns:
            The absolute URL of the instance's detail view.
        """
        return reverse(
            'vms:client-detail',
            kwargs={'client_slug': self.slug},
        )

    @property
    def job_list_url(self):
        """
        Get the URL of the client's job list.

        Returns:
            The URL of the view where all the client's jobs are listed.
        """
        return reverse(
            'vms:client-job-list',
            kwargs={'client_slug': self.slug},
        )

    @property
    def unapproved_time_record_list_url(self):
        """
        Get the URL of the client's unapproved time record list.

        Returns:
            The absolute URL of the view to list the client's unapproved
            time records.
        """
        return reverse(
            'vms:unapproved-time-record-list',
            kwargs={'client_slug': self.slug},
        )


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


class ClientAdminInvite(models.Model):
    """
    An invitation for a user to become a client admin.
    """
    client = models.ForeignKey(
        'vms.Client',
        help_text=_('The client that the invitee will become an admin of.'),
        on_delete=models.CASCADE,
        related_name='admin_invites',
        related_query_name='admin_invite',
        verbose_name=_('client'),
    )
    email = models.EmailField(
        help_text=_('The email address to send the invitation to.'),
        verbose_name=_('email'),
    )
    time_created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('The time the invitation was created at.'),
        verbose_name=_('creation time'),
    )
    token = models.CharField(
        blank=True,
        default=generate_token,
        help_text=_('A unique token used to accept the invitation.'),
        max_length=16,
        unique=True,
        verbose_name=_('token'),
    )

    class Meta:
        ordering = ('time_created',)
        verbose_name = _('client administrator invitation')
        verbose_name_plural = _('client administrator invitations')

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string containing the email address the invite was sent to
            as well as the name of the client company.
        """
        return f'Admin invite for {self.email} from {self.client}'

    def accept(self, user):
        """
        Accept the invitation.

        Args:
            user:
                The user who accepted the invitation.

        Returns:
            The created client admin.
        """
        admin = ClientAdmin.objects.create(client=self.client, user=user)
        logger.info(
            'Create new client administrator from invite: %r',
            admin,
        )

        logger.debug('Deleting admin invitation %r after being accepted', self)
        self.delete()

        return admin

    @property
    def accept_url(self):
        """
        Returns:
            The absolute URL of the view to accept the invite.
        """
        return reverse(
            'vms:client-admin-invite-accept',
            kwargs={'client_slug': self.client.slug, 'token': self.token},
        )

    def send(self, request):
        """
        Send an invitation message to the email address associated with
        the instance.

        Args:
            request:
                The request that was made to trigger the send. This is
                used to build the full URL for accepting the invite.
        """
        email_utils.send_email(
            context={
                'accept_url': f'{request.get_host()}{self.accept_url}',
                'client': self.client,
            },
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            subject=ugettext('Client Administrator Invitation'),
            template_name='vms/emails/client-admin-invite',
        )

        logger.info('Sent client admin invitation to %s', self.email)


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

    def clean(self):
        """
        Generate a slug for the instance if necessary.
        """
        super().clean()

        if not self.slug:
            self.slug = slugify(self.name)

    def clean_fields(self, exclude=None):
        """
        Ensure the name of the instance is not too similar to other jobs
        owned by the same client.

        Args:
            exclude:
                An optional list of fields to exclude from validation.
                Defaults to ``None``.
        """
        super().clean_fields(exclude)

        if exclude is not None and 'name' in exclude:
            return

        slug = slugify(self.name)
        queryset = self.__class__.objects.filter(
            client=self.client,
            slug=slug,
        ).exclude(id=self.id)

        if queryset.exists():
            other = queryset.get()

            logger.info(
                'Client job %r failed unique validation for client %r',
                self,
                self.client,
            )

            message = ugettext(
                "The name '%(name)s' is too similar to the name of the "
                "existing job '%(existing_name)s'."
            ) % {
                'existing_name': other.name,
                'name': self.name,
            }

            raise ValidationError({'name': message})

    def get_absolute_url(self):
        """
        Get the absolute URL of the instance's detail view.

        Returns:
            The absolute URL of the instance's detail view.
        """
        return reverse(
            'vms:client-job-detail',
            kwargs={'client_slug': self.client.slug, 'job_slug': self.slug},
        )


class Employee(models.Model):
    """
    An employee working for a specific company.
    """
    approved_by = models.ForeignKey(
        'vms.ClientAdmin',
        blank=True,
        help_text=_('The admin who approved the employee.'),
        null=True,
        on_delete=models.SET_NULL,
        related_name='approved_employees',
        related_query_name='approved_employee',
        verbose_name=_('approved by'),
    )
    client = models.ForeignKey(
        'vms.Client',
        help_text=_('The client company the employee works for.'),
        on_delete=models.CASCADE,
        related_name='employees',
        related_query_name='employee',
        verbose_name=_('client'),
    )
    employee_id = models.PositiveIntegerField(
        blank=True,
        db_index=True,
        help_text=_(
            'A unique number identifying the employee within the client '
            'company they work for.'
        ),
        verbose_name=_('employee ID'),
    )
    is_active = models.BooleanField(
        default=False,
        help_text=_(
            'A boolean indicating if this user is currently active. Inactive '
            'employees cannot log any working hours.'
        ),
        verbose_name=_('is active'),
    )
    supervisor = models.ForeignKey(
        'vms.ClientAdmin',
        blank=True,
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
        related_name='client_employees',
        related_query_name='client_employee',
        verbose_name=_('staffing agency'),
    )
    time_approved = models.DateTimeField(
        blank=True,
        help_text=_('The time that the employee was approved.'),
        null=True,
        verbose_name=_('approval time'),
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
        return (
            f'{self.user.name} (Hired by {self.staffing_agency})'
        )

    def approve(self, admin):
        """
        Approve the employee's request to join the client.

        Args:
            admin:
                The client admin who approved the request.
        """
        if self.time_approved is not None:
            logger.warning('Approving previously approved employee %r', self)

            return

        self.approved_by = admin
        self.is_active = True
        self.time_approved = timezone.now()
        self.save()

    @property
    def approve_url(self):
        """
        Returns:
            The absolute URL of the view used to approve the employee.
        """
        return reverse(
            'vms:employee-approval',
            kwargs={
                'client_slug': self.client.slug,
                'employee_id': self.employee_id,
            },
        )

    @property
    def clock_in_url(self):
        """
        Returns:
            The absolute URL of the view used to clock in the employee.
        """
        return reverse(
            'vms:clock-in',
            kwargs={
                'client_slug': self.client.slug,
                'employee_id': self.employee_id,
            },
        )

    @property
    def clock_out_url(self):
        """
        Returns:
            The absolute URL of the view used to clock out the employee.
        """
        return reverse(
            'vms:clock-out',
            kwargs={
                'client_slug': self.client.slug,
                'employee_id': self.employee_id,
            },
        )

    @property
    def is_clocked_in(self):
        """
        Determine if the employee is currently clocked in.

        Returns:
            A boolean indicating if the employee is clocked in.
        """
        return self.time_records.filter(time_end=None).exists()

    def get_absolute_url(self):
        """
        Returns:
            The URL of the view for an employee of a client
        """
        return reverse(
            'vms:employee-dash',
            kwargs={
                'client_slug': self.client.slug,
                'employee_id': self.employee_id,
            },
        )

    @property
    def total_time(self):
        """
        Get the total time that the employee has logged.

        Returns:
            The total time the employee has worked, in seconds.
        """
        return self.time_records.total_time().total_seconds()

    def save(self, *args, **kwargs):
        """
        Save the employee and generate an ID for them if necessary.
        """
        if not self.employee_id:
            query = self.__class__.objects.filter(client=self.client)
            self.employee_id = id_utils.generate_unique_id(
                settings.EMPLOYEE_ID_LENGTH,
                query,
                queryset_attr='employee_id',
            )

        super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        """
        Validate that the employee's ID is unique to the company they
        work for.

        Args:
            exclude:
                An optional list of field names to exclude from the
                check.
        """
        super().validate_unique(exclude)

        if exclude is not None and 'employee_id' in exclude:
            return

        queryset = self.__class__.objects.filter(
            client=self.client,
            employee_id=self.employee_id,
        )
        if self.id:
            queryset = queryset.exclude(id=self.id)

        if queryset.exists():
            raise ValidationError(
                'Employee IDs must be unique within a client company.',
            )


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

    def get_absolute_url(self):
        """
        Returns:
            The absolute URL of the instance's detail view.
        """
        return reverse(
            'vms:staffing-agency-view',
            kwargs={'staffing_agency_slug': self.slug},
        )


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


class StaffingAgencyEmployee(models.Model):
    """
    An employee who is contracted out by a staffing agency.
    """
    agency = models.ForeignKey(
        'vms.StaffingAgency',
        help_text=_(
            'The staffing agency the employee works for.'
        ),
        on_delete=models.CASCADE,
        related_name='employees',
        related_query_name='employee',
        verbose_name=_('staffing agency'),
    )
    approved_by = models.ForeignKey(
        'vms.StaffingAgencyAdmin',
        blank=True,
        help_text=_('The admin who accepted the employee.'),
        null=True,
        on_delete=models.SET_NULL,
        related_name='approved_employees',
    )
    id = models.UUIDField(
        default=uuid.uuid4,
        help_text=_('A unique identifier for the employee.'),
        primary_key=True,
        verbose_name=_('ID'),
    )
    is_approved = models.BooleanField(
        default=False,
        help_text=_(
            'A boolean indicating if the employee has been accepted into the '
            'agency.'
        ),
        verbose_name=_('is approved'),
    )
    time_approved = models.DateTimeField(
        blank=True,
        help_text=_('The time that the request was approved.'),
        null=True,
        verbose_name=_('approval time'),
    )
    time_created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('The time that the request was submitted.'),
        verbose_name=_('creation time'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_('The user that works for the agency.'),
        on_delete=models.CASCADE,
        related_name='staffing_agency_employees',
        related_query_name='staffing_agency_employee',
        verbose_name=_('user'),
    )

    class Meta:
        unique_together = ('agency', 'user')
        verbose_name = _('staffing agency employee')
        verbose_name_plural = _('staffing agency employees')

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string identifying the user and staffing agency attached
            to the employee record.
        """
        return (
            f"{self.user.name} contracted by {self.agency.name}"
        )

    def get_absolute_url(self):
        """
        Get the URL of the staffing agency's employee.

        Returns:
            The URL of the view where the staffing agency's employee
            information is listed.
        """
        return reverse(
            'vms:staffing-agency-employee',
            kwargs={'staffing_agency_slug': self.agency.slug,
                    'employee_id': self.id},)


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
    pay_rate = models.DecimalField(
        decimal_places=2,
        help_text=_('The hourly pay for the time record.'),
        max_digits=11,
        verbose_name=_('pay rate'),
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

    # Use our custom manager
    objects = managers.TimeRecordManager()

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
            f'TimeRecord('
            f'id={self.id!r}, '
            f'job_id={self.job.id if self.job else None!r}, '
            f'employee_id={self.employee.id!r}, '
            f'time_start={self.time_start!r}, '
            f'time_end={self.time_end!r})'
        )

    def __str__(self):
        """
        Get a user readable string describing the instance.

        Returns:
            A string describing the time record including the start and
            end times.
        """
        st = self.time_start
        if self.time_end:
            et = self.time_end
            if self.time_start.date() == self.time_end.date():
                return (
                    f'Time Record from {st:%I:%M %p} to '
                    f'{et:%I:%M %p} on {st:%m/%d/%Y}.'
                )
            else:
                return (
                    f'Time Record from {st:%I:%M %p on %m/%d/%Y}, '
                    f'{et:%I:%M %p on %m/%d/%Y}.'
                )
        return f'Time Record starting at {st:%I:%M %p} on {st:%m/%d/%Y}.'

    @property
    def approval_url(self):
        """
        Get the URL of the view used to approve the time record.

        Returns:
            The absolute URL of the view used to approve the time
            record.
        """
        return reverse(
            'vms:time-record-approve',
            kwargs={'time_record_id': self.id},
        )

    @property
    def is_approved(self):
        """
        Determine if the time record is approved.

        Returns:
            A boolean indicating if there is an approval record for the
            time record.
        """
        return hasattr(self, 'approval')

    @property
    def total_time(self):
        """
        Get the total time from this time record.
        Returns:
            The time delta between start time and end time
            or delta of 0 if no end time.
        """
        if self.time_end:
            return self.time_end - self.time_start
        return datetime.timedelta(0)

    @property
    def projected_earnings(self):
        """
        Get the projected earning from this time record.

        Returns:
            The total time multiplied by
            the pay rate for this job.
        """
        hours_dec = self.total_time.total_seconds() / (60*60)

        return decimal.Decimal(hours_dec) * self.pay_rate


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
