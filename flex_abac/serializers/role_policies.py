from flex_abac.models import RolePolicy
from rest_framework import serializers


class RolePolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = RolePolicy
        fields = ['pk', 'role', 'policy']
