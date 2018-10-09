from django.urls import path

from vms import views


app_name = 'vms'

urlpatterns = [
    path(
        'employees/<int:employee_id>/clock-in/',
        views.ClockInView.as_view(),
        name='clock-in',
    ),
    path(
        'employees/<int:employee_id>/clock-out/',
        views.ClockOutView.as_view(),
        name='clock-out',
    ),
    path(
        'dashboard/',
        views.DashboardView.as_view(),
        name='dashboard',
    ),
]
