from django.urls import path

from vms import views


app_name = 'vms'

urlpatterns = [
    path(
        'dashboard/',
        views.DashboardView.as_view(),
        name='dashboard',
    ),
]
