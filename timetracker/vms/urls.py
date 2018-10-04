from django.urls import path

from vms import views


app_name = 'vms'

urlpatterns = [
    path(
        'employees/<uuid:employee_id>/clock-in/',
        views.ClockInView.as_view(),
        name='clock-in',
    ),
    path(
        'dashboard/',
        views.DashboardView.as_view(),
        name='dashboard',
    ),
]
