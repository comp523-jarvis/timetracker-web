from django.contrib import admin

from vms import models


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)
    date_hierarchy = 'time_created'
    fields = ('user', 'wage')
    list_display = ('user', 'is_active', 'time_created')
    list_filter = ('is_active',)
    search_fields = ('user__name',)
