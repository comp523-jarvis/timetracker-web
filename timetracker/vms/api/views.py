from rest_framework import generics

from vms.api import serializers


class DialogflowFulfillmentView(generics.CreateAPIView):
    serializer_class = serializers.DialogflowWebhookSerializer
