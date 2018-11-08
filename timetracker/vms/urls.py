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
    path(
        'jobs/',
        views.ClientJobListView.as_view(),
        name='client-job-list',
    ),
    path(
        'jobs/<slug:job_slug>/',
        views.ClientJobDetailView.as_view(),
        name='client-job-detail',
    ),
    path(
        'time-records/unapproved/',
        views.UnapprovedTimeRecordListView.as_view(),
        name='unapproved-time-record-list',
    ),
    path(
        '',
        views.ClientView.as_view(),
        name='client-view',
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
    path(
        'time-records/<uuid:time_record_id>/approve/',
        views.TimeRecordApproveView.as_view(),
        name='time-record-approve',
    ),
]
