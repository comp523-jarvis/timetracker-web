from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from vms import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    date_hierarchy = 'time_created'
    fieldsets = (
        (
            None,
            {
                'fields': ('name', 'id'),
            },
        ),
        (
            _('Contact Information'),
            {
                'fields': ('email', 'phone_number', 'notes'),
            },
        ),
        (
            _('Detailed Information'),
            {
                'classes': ('collapse',),
                'fields': ('slug', 'time_created', 'time_updated'),
            },
        ),
    )
    list_display = ('name', 'id', 'email', 'time_created', 'time_updated')
    readonly_fields = ('id', 'slug', 'time_created', 'time_updated')
    search_fields = ('email', 'name')


@admin.register(models.ClientAdmin)
class ClientAdminAdmin(admin.ModelAdmin):
    autocomplete_fields = ('client', 'user')
    date_hierarchy = 'time_created'
    fields = ('client', 'user', 'time_created')
    list_display = ('user', 'client', 'time_created')
    readonly_fields = ('time_created',)
    search_fields = ('client__name', 'user__name')


@admin.register(models.ClientJob)
class ClientJobAdmin(admin.ModelAdmin):
    autocomplete_fields = ('client',)
    fields = ('client', 'name', 'pay_rate', 'description', 'slug')
    list_display = ('name', 'client', 'pay_rate')
    readonly_fields = ('slug',)
    search_fields = ('client__name', 'name', 'slug')


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('client', 'user')
    date_hierarchy = 'time_created'
    fieldsets = (
        (
            None,
            {
                'fields': ('user', 'client', 'staffing_agency', 'employee_id'),
            },
        ),
        (
            _('Employee Details'),
            {
                'fields': ('supervisor', 'is_active'),
            },
        ),
        (
            _('Approval Information'),
            {
                'fields': ('approved_by', 'time_approved'),
            },
        ),
        (
            _('Detailed Information'),
            {
                'classes': ('collapse',),
                'fields': ('time_created', 'time_updated'),
            },
        ),
    )
    list_display = (
        'employee_id',
        'user',
        'client',
        'staffing_agency',
        'supervisor_name',
        'is_active',
        'time_created',
    )
    list_filter = ('is_active',)
    readonly_fields = ('time_created', 'time_updated')
    search_fields = (
        'client__name',
        'staffing_agency__name',
        'supervisor__user__name',
        'user__name',
    )

    def supervisor_name(self, obj):
        """
        Get the name of the employee's supervisor.

        Args:
            obj:
                The employee to get the supervisor of.

        Returns:
            The name of the employee's supervisor if they have an
            assigned supervisor. Otherwise, a placeholder empty value is
            returned.
        """
        if obj.supervisor:
            return obj.supervisor.user.name
        else:
            return "-"
    supervisor_name.admin_order_field = 'supervisor__user__name'


@admin.register(models.StaffingAgency)
class StaffingAgencyAdmin(admin.ModelAdmin):
    date_hierarchy = 'time_created'
    fieldsets = (
        (
            None,
            {
                'fields': ('name',),
            },
        ),
        (
            _('Contact Information'),
            {
                'fields': ('email', 'phone_number', 'notes'),
            },
        ),
        (
            _('Detailed Information'),
            {
                'classes': ('collapse',),
                'fields': ('slug', 'time_created', 'time_updated'),
            },
        ),
    )
    list_display = ('name', 'email', 'time_created', 'time_updated')
    readonly_fields = ('slug', 'time_created', 'time_updated')
    search_fields = ('email', 'name')


@admin.register(models.StaffingAgencyAdmin)
class StaffingAgencyAdminAdmin(admin.ModelAdmin):
    autocomplete_fields = ('agency', 'user')
    date_hierarchy = 'time_created'
    fields = ('agency', 'user', 'time_created')
    list_display = ('user', 'agency', 'time_created')
    readonly_fields = ('time_created',)
    search_fields = ('agency__name', 'user__name')


@admin.register(models.StaffingAgencyEmployee)
class StaffingAgencyEmployeeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('agency', 'approved_by', 'user')
    date_hierarchy = 'time_created'
    fieldsets = (
        (
            None,
            {
                'fields': ('user', 'agency', 'time_created'),
            },
        ),
        (
            _('Approval'),
            {
                'fields': ('is_approved', 'approved_by', 'time_approved'),
            },
        ),
    )
    list_display = (
        'user',
        'agency',
        'time_created',
        'is_approved',
        'time_approved',
    )
    list_filter = ('is_approved',)
    readonly_fields = ('time_created',)
    search_fields = ('agency__name', 'approved_by__user__name', 'user__name')


@admin.register(models.TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    autocomplete_fields = ('job', 'employee')
    date_hierarchy = 'time_start'
    fields = ('employee', 'job', 'pay_rate', 'time_start', 'time_end')
    list_display = (
        'employee',
        'client',
        'job',
        'pay_rate',
        'time_start',
        'time_end',
    )
    search_fields = ('employee__user__name', 'job__client__name', 'job__name')

    def client(self, obj):
        return obj.employee.client
    client.admin_order_field = 'employee__client__name'


@admin.register(models.TimeRecordApproval)
class TimeRecordApprovalAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)
    date_hierarchy = 'time_approved'
    fields = ('time_record', 'user', 'time_approved')
    list_display = ('time_record', 'user', 'time_approved')
    readonly_fields = ('time_approved',)
    search_fields = ('user__name',)
