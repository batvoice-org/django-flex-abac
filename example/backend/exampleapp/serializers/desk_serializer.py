from exampleapp.models import Desk
from django.db.models import F

from rest_framework import serializers

class DeskSerializer(serializers.Serializer):
    desk = serializers.SerializerMethodField()

    class Meta:
        fields = ['desk']

    def get_desk(self, obj):
        return obj["desk"]

    @classmethod
    def possible_values(cls):
        return Desk.objects.annotate(desk=F("pk")).values("desk")

    def get_extra(self, desk_info):
        desk = Desk.objects.get(pk=desk_info["desk"])
        return {
            'name': desk.name,
            'id': desk.pk
        }

    def create(self, validated_data):
        return validated_data