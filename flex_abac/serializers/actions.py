from flex_abac.models import Action

from rest_framework import serializers


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['name', 'pretty_name', 'models', 'pk']
