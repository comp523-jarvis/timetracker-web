from django.urls import include, path

from vms import views


app_name = 'vms'


client_detail_urls = [
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
        'employees/<int:employee_id>/',
        views.EmployeeDashView.as_view(),
        name='employee-dash',
    ),
]


urlpatterns = [
    path(
        'clients/<slug:client_slug>/',
        include(client_detail_urls)
    ),
    path(
        'dashboard/',
        views.DashboardView.as_view(),
        name='dashboard',
    ),
    path(
        'create-staff-agency/',
        views.CreateStaffAgencyView.as_view(),
        name='create-staff-agency'
    ),
]
