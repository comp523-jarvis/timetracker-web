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
    fields = ('employee', 'time_start', 'time_end', 'is_approved')
    list_display = ('employee', 'time_start', 'time_end', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('employee__user__name',)
