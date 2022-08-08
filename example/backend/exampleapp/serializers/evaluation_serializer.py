from exampleapp.models import Evaluation

from exampleapp.serializers import DocumentSerializer

from rest_framework import serializers


class EvaluationSerializer(serializers.ModelSerializer):
    document = DocumentSerializer()

    class Meta:
        model = Evaluation
        fields = ['pk', 'name', 'document']