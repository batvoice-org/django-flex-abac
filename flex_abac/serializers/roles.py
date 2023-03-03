from flex_abac.models import Role, RolePolicy, Policy
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from flex_abac.serializers import PolicySerializer
from flex_abac.serializers.utils import WritableSerializerMethodField
from django.db import transaction
from django.conf import settings

from flex_abac.checkers import get_filter_for_valid_objects


class RoleSerializer(serializers.ModelSerializer):
    policies = WritableSerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.remaining_depth = -1

        if "remaining_depth" in self.context.keys():
            self.remaining_depth = self.context["remaining_depth"]

            if self.remaining_depth == 0:
                self.fields.pop("policies")

            if self.remaining_depth >= 0:
                self.remaining_depth -= 1

    class Meta:
        model = Role
        fields = ['pk', 'name', 'policies']

    def get_policies(self, role_obj):
        if getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False):
            valid_objects_filter = get_filter_for_valid_objects(role_obj, Policy, action_name="policy__read")
            return PolicySerializer(role_obj.policies.filter(valid_objects_filter),
                                    context={"remaining_depth": self.remaining_depth}, many=True).data
        else:
            return PolicySerializer(role_obj.policies,
                                    context={"remaining_depth": self.remaining_depth}, many=True).data

    @transaction.atomic
    def create(self, validated_data):
        role, _ = Role.objects.get_or_create(
            name=validated_data["name"]
        )
        for policy_value in validated_data["policies"]:
            if type(policy_value) == dict:
                try:
                    policy_serializer = PolicySerializer(data=policy_value, many=False)
                    policy_serializer.is_valid(raise_exception=True)
                    policy_serializer.save()

                    RolePolicy.objects.get_or_create(role=role, policy=policy_serializer.instance)
                except ValidationError as ve:
                    policy = Policy.objects.get(name=policy_value["name"])
                    if policy:
                        RolePolicy.objects.create(role=role, policy=policy)
                    else:
                        raise ve
            else:
                policy = Policy.objects.get(pk=policy_value)
                RolePolicy.objects.get_or_create(role=role, policy=policy)

        return role

    @transaction.atomic
    def update(self, instance, validated_data):
        RolePolicy.objects.filter(role=instance).delete()

        instance.name = validated_data["name"]
        instance.save()

        if type(validated_data["policies"]) is not list:
            validated_data["policies"] = [validated_data["policies"]]

        for policy_id in validated_data["policies"]:
            policy = Policy.objects.get(pk=policy_id)
            RolePolicy.objects.get_or_create(role=instance, policy=policy)

        return instance

# Consider renaming this class, as it is attached to Role, not RolePolicy in Meta:
class RolePolicySerializer(serializers.ModelSerializer):
    policies = WritableSerializerMethodField()

    class Meta:
        model = Role
        fields = ['pk', 'name', 'policies']

    def get_policies(self, role_obj):
        return PolicySerializer(role_obj.policies, many=True).data

    def update(self, instance, validated_data):
        if type(validated_data["policies"]) is not list:
            validated_data["policies"] = [validated_data["policies"]]

        for policy_id in validated_data["policies"]:
            policy = Policy.objects.get(pk=policy_id)
            RolePolicy.objects.get_or_create(role=instance, policy=policy)

        return instance

    def delete(self, instance, validated_data):
        if type(validated_data["policies"]) is not list:
            validated_data["policies"] = [validated_data["policies"]]

        RolePolicy.objects.filter(role=instance, policy__pk__in=validated_data["policies"]).delete()

        return instance
