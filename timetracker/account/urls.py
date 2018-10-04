from django.contrib.auth.views import LoginView
from django.urls import path

from account import views


app_name = 'account'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(),
        name='login',
    ),
    path(
        'profile/',
        views.ProfileView.as_view(),
        name='profile',
    ),
]
