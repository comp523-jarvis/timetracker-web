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
    autocomplete_fields = ('user',)
    date_hierarchy = 'time_created'
    fields = (
        'user',
        'staffing_agency',
        'supervisor',
        'is_active',
        'time_created',
        'time_updated',
    )
    list_display = (
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
        'staffing_agency__name',
        'supervisor__user__name',
        'user__name',
    )

    def client(self, obj):
        return obj.supervisor.client
    client.admin_order_field = 'supervisor__client__name'

    def supervisor_name(self, obj):
        return obj.supervisor.user.name
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


@admin.register(models.TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    autocomplete_fields = ('job', 'employee')
    date_hierarchy = 'time_start'
    fields = ('employee', 'job', 'time_start', 'time_end')
    list_display = ('employee', 'client', 'job', 'time_start', 'time_end')
    search_fields = ('employee__user__name', 'job__client__name', 'job__name')

    def client(self, obj):
        return obj.job.client
    client.admin_order_field = 'job__client__name'


@admin.register(models.TimeRecordApproval)
class TimeRecordApprovalAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)
    date_hierarchy = 'time_approved'
    fields = ('time_record', 'user', 'time_approved')
    list_display = ('time_record', 'user', 'time_approved')
    readonly_fields = ('time_approved',)
    search_fields = ('user__name',)
