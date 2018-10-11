from django.contrib import admin

from vms import models


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)
    date_hierarchy = 'time_created'
    fields = (
        'user',
        'company',
        'supervisor',
        'is_active',
        'time_created',
        'time_updated',
    )
    list_display = (
        'user',
        'company',
        'supervisor',
        'is_active',
        'time_created',
    )
    list_filter = ('is_active',)
    readonly_fields = ('time_created', 'time_updated')
    search_fields = ('company', 'supervisor', 'user__name',)


@admin.register(models.TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    autocomplete_fields = ('employee',)
    date_hierarchy = 'time_start'
    fields = ('employee', 'time_start', 'time_end')
    list_display = ('employee', 'time_start', 'time_end')
    search_fields = ('employee__user__name',)


@admin.register(models.TimeRecordApproval)
class TimeRecordApprovalAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)
    date_hierarchy = 'time_approved'
    fields = ('time_record', 'user', 'time_approved')
    list_display = ('time_record', 'user', 'time_approved')
    readonly_fields = ('time_approved',)
    search_fields = ('user__name',)
