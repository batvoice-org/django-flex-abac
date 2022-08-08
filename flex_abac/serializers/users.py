from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from flex_abac.models import UserRole, Role

from flex_abac.serializers.roles import RoleSerializer

from flex_abac.serializers.utils import WritableSerializerMethodField

from django.db import transaction

from flex_abac.checkers import get_filter_for_valid_objects

from django.conf import settings

USE_PERMISSIONS = getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False)

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    roles = WritableSerializerMethodField()
    remaining_depth = -1


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.remaining_depth = -1

        if "remaining_depth" in self.context.keys():
            self.remaining_depth = self.context["remaining_depth"]

            if self.remaining_depth == 0:
                self.fields.pop("roles")

            if self.remaining_depth >= 0:
                self.remaining_depth -= 1

    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'is_staff', 'roles']
        extra_kwargs = {
            'username': {'read_only': True},
            'email': {'read_only': True},
            'is_staff': {'read_only': True},
        }

    def get_roles(self, user_obj):
        if USE_PERMISSIONS:
            valid_objects_filter = get_filter_for_valid_objects(user_obj, Role)
            return RoleSerializer(Role.objects.filter(userrole__user=user_obj).filter(valid_objects_filter),
                                  context={"remaining_depth": self.remaining_depth}, many=True).data
        else:
            return RoleSerializer(Role.objects.filter(userrole__user=user_obj),
                                  context={"remaining_depth": self.remaining_depth}, many=True).data

    @transaction.atomic
    def update(self, instance, validated_data):
        UserRole.objects.filter(user=instance).\
            exclude(role__name__in=("flex-abac Admin Role", "flex-abac Viewer Role")).\
            delete()

        if type(validated_data["roles"]) is not list:
            validated_data["roles"] = [validated_data["roles"]]
        for role_value in validated_data["roles"]:
            if type(role_value) == dict:
                try:
                    role_serializer = RoleSerializer(data=role_value, many=False)
                    role_serializer.is_valid(raise_exception=True)
                    role_serializer.save()

                    UserRole.objects.get_or_create(user=instance, role=role_serializer.instance)
                except ValidationError as ve:
                    role = Role.objects.get(name=role_value["name"])
                    if role:
                        UserRole.objects.get_or_create(user=instance, role=role)
                    else:
                        raise ve
            else:
                role = Role.objects.get(pk=role_value)
                UserRole.objects.get_or_create(user=instance, role=role)

        return instance


class UserRoleSerializer(serializers.ModelSerializer):
    roles = WritableSerializerMethodField()

    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'is_staff', 'roles']
        extra_kwargs = {
            'username': {'read_only': True},
            'email': {'read_only': True},
            'is_staff': {'read_only': True},
        }

    def get_roles(self, user_obj):
        return RoleSerializer(Role.objects.filter(userrole__user=user_obj), many=True).data

    def update(self, instance, validated_data):
        if type(validated_data["roles"]) is not list:
            validated_data["roles"] = [validated_data["roles"]]

        for role_id in validated_data["roles"]:
            role = Role.objects.get(pk=role_id)
            UserRole.objects.get_or_create(user=instance, role=role)

        return instance

    def delete(self, instance, validated_data):
        if type(validated_data["roles"]) is not list:
            validated_data["roles"] = [validated_data["roles"]]

        UserRole.objects.filter(user=instance, role__pk__in=validated_data["roles"]).delete()

        return instance

