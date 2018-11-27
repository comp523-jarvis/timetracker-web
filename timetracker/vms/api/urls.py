from django.urls import path

from vms.api import views


app_name = 'vms_api'


urlpatterns = [
    path(
        'dialogflow/',
        views.DialogflowFulfillmentView.as_view(),
        name='dialogflow',
    ),
]
