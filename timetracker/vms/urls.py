from django.urls import include, path

from vms import views


app_name = 'vms'


client_detail_urls = [
    path(
        'admin-invites/<token>/',
        views.ClientAdminInviteAcceptView.as_view(),
        name='client-admin-invite-accept',
    ),
    path(
        'employees/pending/',
        views.PendingEmployeesView.as_view(),
        name='employee-pending'
    ),
    path(
        'employees/<int:employee_id>/',
        views.EmployeeDetailView.as_view(),
        name='employee-dash',
    ),
    path(
        'employees/<int:employee_id>/approve/',
        views.EmployeeApproveView.as_view(),
        name='employee-approval',
    ),
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
        'jobs/',
        views.ClientJobListView.as_view(),
        name='client-job-list',
    ),
    path(
        'jobs/create/',
        views.ClientJobCreateView.as_view(),
        name='client-job-create',
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
        views.ClientDetailView.as_view(),
        name='client-detail',
    ),
]


staff_detail_urls = [
    path(
        '',
        views.StaffingAgencyDetailView.as_view(),
        name='staffing-agency-view',
    ),
    path(
        'employees/pending/',
        views.StaffingAgencyEmployeePendingListView.as_view(),
        name='staffing-agency-employee-pending',
    ),
    path(
        'employees/<uuid:employee_id>/',
        views.StaffingAgencyEmployeeDetailView.as_view(),
        name='staffing-agency-employee',
    ),
    path(
        'employees/<uuid:employee_id>/apply/',
        views.EmployeeApplyView.as_view(),
        name='staffing-agency-employee-apply',
    ),
    path(
        'employees/<uuid:employee_id>/approve/',
        views.StaffingAgencyEmployeeApproveView.as_view(),
        name='staffing-agency-employee-approve',
    ),
]


urlpatterns = [
    path(
        'clients/<slug:client_slug>/',
        include(client_detail_urls)
    ),
    path(
        'create-client/',
        views.ClientCreateView.as_view(),
        name='client-create',
    ),
    path(
        'staffing-agencies/<slug:staffing_agency_slug>/',
        include(staff_detail_urls)
    ),
    path(
        'dashboard/',
        views.DashboardView.as_view(),
        name='dashboard',
    ),
    path(
        'time-records/<uuid:time_record_id>/approve/',
        views.TimeRecordApproveView.as_view(),
        name='time-record-approve',
    ),
    path(
        'create-staff-employee/',
        views.StaffingAgencyEmployeeCreateView.as_view(),
        name='create-staff-employee',
    ),
]
