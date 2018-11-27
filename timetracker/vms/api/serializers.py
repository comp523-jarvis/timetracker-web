from rest_framework import serializers

from vms.api.dialogflow import process


class IntentSerializer(serializers.Serializer):
    """
    Serializer to handle information about the intent triggered by
    Dialogflow.
    """
    name = serializers.CharField()


class QuerySerializer(serializers.Serializer):
    """
    Serializer to handle the query parameters for a Dialogflow
    fulfillment request.
    """
    intent = IntentSerializer(write_only=True)
    parameters = serializers.DictField(child=serializers.CharField())


class DialogflowWebhookSerializer(serializers.Serializer):
    """
    Serializer to handle a request from Dialogflow.
    """
    fulfillmentText = serializers.CharField(read_only=True)
    queryResult = QuerySerializer(write_only=True)

    def save(self, **kwargs):
        self.validated_data.update(process(self.validated_data))
