from flex_abac.models import (
    Policy, Action, PolicyFilter, BaseFilter, PolicyAction,
    ActionModel, BaseAttribute,
)

from flex_abac.checkers import get_filter_for_valid_objects
from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from flex_abac.serializers.actions import ActionSerializer
from flex_abac.serializers.filters import PolymorphicFilterSerializer
from flex_abac.serializers.attributes import PolymorphicAttributeTypeSerializer
from flex_abac.serializers.utils import WritableSerializerMethodField
from django.db import transaction
from flex_abac.utils.helpers import get_subclasses


class PolicySerializer(serializers.ModelSerializer):
    actions = WritableSerializerMethodField()
    scopes = WritableSerializerMethodField()
    remaining_depth = -1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.remaining_depth = -1

        if "remaining_depth" in self.context.keys():
            self.remaining_depth = self.context["remaining_depth"]

            if self.remaining_depth == 0:
                self.fields.pop("actions")
                self.fields.pop("scopes")

            if self.remaining_depth >= 0:
                self.remaining_depth -= 1


    class Meta:
        model = Policy
        fields = ['pk', 'name', 'actions', 'scopes']

    def get_actions(self, policy_obj):
        if getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False):
            valid_objects_filter = get_filter_for_valid_objects(policy_obj, Action, action_name="action__read")
            return ActionSerializer(policy_obj.actions.filter(valid_objects_filter), many=True).data
        else:
            return ActionSerializer(policy_obj.actions, many=True).data

    def get_scopes(self, policy_obj):
        scopes_list = []
        for policy_value_type in PolicyFilter.__subclasses__():
            if getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False) and policy_value_type.objects.exists():
                valid_objects_filter = get_filter_for_valid_objects(policy_obj, BaseFilter, base_lookup_name="value", action_name="basefilter__read")
                scopes = policy_value_type.objects.filter(policy=policy_obj).filter(valid_objects_filter)
            else:
                scopes = policy_value_type.objects.filter(policy=policy_obj)
            for scope in scopes:
                scopes_list.append(scope.value)

        return PolymorphicFilterSerializer(scopes_list, many=True).data

    @transaction.atomic
    def create(self, validated_data):
        policy, _ = Policy.objects.get_or_create(
            name=validated_data["name"]
        )
        for action_value in validated_data["actions"]:
            if type(action_value) == dict:
                try:
                    action_serializer = ActionSerializer(data=action_value, many=False)
                    action_serializer.is_valid(raise_exception=True)
                    action_serializer.save()

                    PolicyAction.objects.get_or_create(policy=policy, action=action_serializer.instance)
                except ValidationError as ve:
                    action = Action.objects.get(name=action_value["name"])
                    if action:
                        PolicyAction.objects.get_or_create(policy=policy, action=action)
                    else:
                        raise ve
            else:
                action = Action.objects.get(pk=action_value)
                PolicyAction.objects.get_or_create(policy=policy, action=action)

        for scope_value in validated_data["scopes"]:
            if type(scope_value) == dict:
                attr_value_serializer = PolymorphicFilterSerializer(data=scope_value, many=False)
                attr_value_serializer.is_valid(raise_exception=True)
                attr_value_serializer.save()

                attr_value_serializer.instance.add_to_policy(policy)
            else:
                scope = BaseFilter.objects.get(pk=scope_value)
                scope.add_to_policy(policy)

        return policy


    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.save()

        PolicyAction.objects.filter(policy=instance).delete()
        for policy_class in PolicyFilter.__subclasses__():
            policy_class.objects.filter(policy=instance).delete()

        if type(validated_data["actions"]) is not list:
            validated_data["actions"] = [validated_data["actions"]]
        if type(validated_data["scopes"]) is not list:
            validated_data["scopes"] = [validated_data["scopes"]]

        for action_id in validated_data["actions"]:
            action = Action.objects.get(pk=action_id)
            PolicyAction.objects.get_or_create(policy=instance, action=action)

        for scope_value in validated_data["scopes"]:
            if type(scope_value) == dict:
                attr_value_serializer = PolymorphicFilterSerializer(data=scope_value, many=False)
                attr_value_serializer.is_valid(raise_exception=True)
                attr_value_serializer.save()

                attr_value_serializer.instance.add_to_policy(instance)
            else:
                scope = BaseFilter.objects.get(pk=scope_value)
                scope.add_to_policy(instance)

        return instance

class PolicyActionSerializer(serializers.ModelSerializer):
    actions = WritableSerializerMethodField()

    class Meta:
        model = Policy
        fields = ['pk', 'actions']


    def get_actions(self, policy_obj):
        return ActionSerializer(policy_obj.actions, many=True).data


    def update(self, instance, validated_data):
        if type(validated_data["actions"]) is not list:
            validated_data["actions"] = [validated_data["actions"]]

        for action_id in validated_data["actions"]:
            action = Action.objects.get(pk=action_id)
            PolicyAction.objects.get_or_create(policy=instance, action=action)

        return instance

    def delete(self, instance, validated_data):
        if type(validated_data["actions"]) is not list:
            validated_data["actions"] = [validated_data["actions"]]

        PolicyAction.objects.filter(policy=instance, action__pk__in=validated_data["actions"]).delete()

        return instance


class PolicyScopeSerializer(serializers.ModelSerializer):
    scopes = WritableSerializerMethodField()

    class Meta:
        model = Policy
        fields = ['pk', 'scopes']

    def get_scopes(self, policy_obj):
        scopes_list = []
        for policy_value_type in get_subclasses(PolicyFilter):
            scopes = policy_value_type.objects.filter(policy=policy_obj)
            for scope in scopes:
                scopes_list.append(scope.value)

        return PolymorphicFilterSerializer(scopes_list, many=True).data


    def update(self, instance, validated_data):
        if type(validated_data["scopes"]) is not list:
            validated_data["scopes"] = [validated_data["scopes"]]


        for scope_id in validated_data["scopes"]:
            scope = BaseFilter.objects.get(pk=scope_id)
            scope.add_to_policy(instance)

        return instance


    def delete(self, instance, validated_data):
        if type(validated_data["scopes"]) is not list:
            validated_data["scopes"] = [validated_data["scopes"]]

        for policy_value_type in get_subclasses(PolicyFilter):
            policy_value_type.objects.filter(policy=instance, value__id__in=validated_data["scopes"]).delete()

        return instance


class PolicyAttributesSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = Policy
        fields = ['pk', 'attributes']

    def get_attributes(self, policy_obj):
        content_types = ActionModel.objects.filter(action__in=policy_obj.actions.all()).values_list("content_type", flat=True)

        attributes = []
        for attribute_type_model in get_subclasses(BaseAttribute):
            attributes += attribute_type_model.get_all_attributes_from_content_types(content_types).all()

        return PolymorphicAttributeTypeSerializer(attributes, many=True).data