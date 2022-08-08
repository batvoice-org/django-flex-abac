from flex_abac.models import (
    UserRole,
    Role,
    Policy,
    PolicyAction,
    PolicyFilter,
    Action,
    BaseAttribute,
    GenericAttribute,
    BaseFilter,
    GenericFilter,
)
from rest_framework import viewsets

from django.conf import settings

from flex_abac.serializers import (
    UserRoleSerializer, RoleSerializer, RolePolicySerializer,
    PolicySerializer, PolicyActionSerializer, PolicyScopeSerializer, PolicyAttributesSerializer,
    ActionSerializer,
    PolymorphicAttributeTypeSerializer,
    GenericAttributeSerializer,
    GenericFilterSerializer,
    PolymorphicFilterSerializer,
    PolymorphicPossibleValuesSerializer
)

from flex_abac.permissions import CanExecuteMethodPermission


from rest_framework.decorators import action
from rest_framework.response import Response

from flex_abac.checkers import get_filter_for_valid_objects

USE_PERMISSIONS = getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False)

class RoleViewSet(viewsets.ModelViewSet):


    permission_classes = [CanExecuteMethodPermission] if USE_PERMISSIONS else []
    queryset = Role.objects
    serializer_class = RoleSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action == "list":
            context["remaining_depth"] = 1

        return context

    def get_queryset(self):
        if USE_PERMISSIONS:
            valid_objects_filter = get_filter_for_valid_objects(self.request.user, Role, action_name="role__read")
            return self.queryset.filter(valid_objects_filter)
        else:
            return self.queryset

    @action(detail=True, methods=['put'])
    def add_policies(self, request, pk=None):
        serializer = RolePolicySerializer(self.get_object(), many=False)
        serializer.update(self.get_object(), {"policies": request.data.getlist("policies")})

        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_policies(self, request, pk=None):
        serializer = RolePolicySerializer(self.get_object(), many=False)
        serializer.delete(self.get_object(), {"policies": request.data.getlist("policies")})

        return Response(serializer.data)

class PolicyViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission] if USE_PERMISSIONS else []
    queryset = Policy.objects
    serializer_class = PolicySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action == "list":
            context["remaining_depth"] = 1

        return context

    def get_queryset(self):
        if USE_PERMISSIONS:
            valid_objects_filter = get_filter_for_valid_objects(self.request.user, Policy)
            queryset = self.queryset.filter(valid_objects_filter)
        else:
            return self.queryset

        return queryset

    @action(detail=True, methods=['put'])
    def add_actions(self, request, pk=None):
        serializer = PolicyActionSerializer(self.get_object(), many=False)
        serializer.update(self.get_object(), { "actions": request.data.getlist("actions") })

        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_actions(self, request, pk=None):
        serializer = PolicyActionSerializer(self.get_object(), many=False)
        serializer.delete(self.get_object(), {"actions": request.data.getlist("actions") })

        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def add_scopes(self, request, pk=None):
        serializer = PolicyScopeSerializer(self.get_object(), many=False)
        serializer.update(self.get_object(), {"scopes": request.data.getlist("scopes")})

        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_scopes(self, request, pk=None):
        serializer = PolicyScopeSerializer(self.get_object(), many=False)
        serializer.delete(self.get_object(), {"scopes": request.data.getlist("scopes")})

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_all_active_attributes(self, request, pk=None):
        serializer = PolicyAttributesSerializer(self.get_object(), many=False)
        return Response(serializer.data)


class ActionViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission] if USE_PERMISSIONS else []
    queryset = Action.objects
    serializer_class = ActionSerializer

    def get_queryset(self):
        if USE_PERMISSIONS:
            valid_objects_filter = get_filter_for_valid_objects(self.request.user, Action, action_name="action__read")
            return self.queryset.filter(valid_objects_filter)
        else:
           return self.queryset


class AttributeTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission] if USE_PERMISSIONS else []

    queryset = BaseAttribute.objects
    serializer_class = PolymorphicAttributeTypeSerializer

    def get_queryset(self):
        if USE_PERMISSIONS:
            valid_objects_filter = get_filter_for_valid_objects(self.request.user, BaseAttribute, action_name="baseattribute__read")
            return self.queryset.filter(valid_objects_filter)
        else:
            return self.queryset

    @action(detail=True, methods=['get'])
    def get_all_allowed_values(self, request, pk=None):
        attribute_type = self.get_object()

        values = attribute_type.get_all_values_for_user(request.user)
        serializer = PolymorphicFilterSerializer(values, many=True, fields=["pk", "value", "extra"])
        return Response(serializer.data)


class FilterViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission] if USE_PERMISSIONS else []
    queryset = BaseFilter.objects
    serializer_class = PolymorphicFilterSerializer

    def get_queryset(self):
        if USE_PERMISSIONS:
            valid_objects_filter = get_filter_for_valid_objects(self.request.user, BaseFilter)
            return self.queryset.filter(valid_objects_filter)
        else:
            return self.queryset


class PossibleValuesViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission] if USE_PERMISSIONS else []
    queryset = BaseAttribute.objects
    serializer_class = PolymorphicPossibleValuesSerializer

    def get_queryset(self):
        if USE_PERMISSIONS:
            valid_objects_filter = get_filter_for_valid_objects(self.request.user, BaseAttribute)
            return self.queryset.filter(valid_objects_filter)
        else:
            return self.queryset
