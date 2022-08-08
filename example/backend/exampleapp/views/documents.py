from rest_framework import viewsets

from django.db.models import Q

from flex_abac.views import AttributeTypeViewSet, UserViewSet

from flex_abac.checkers import get_filter_for_valid_objects

from exampleapp.serializers import DocumentSerializer, EvaluationSerializer
from exampleapp.models import Document, Evaluation, Desk

from rest_framework.decorators import action

from flex_abac.utils.mappings import DefaultAttributeMappingGenerator


from flex_abac.permissions import (
    CanExecuteMethodPermission,
    flex_abac_params,
    flex_abac_params_api_view,
)

from django.contrib.auth.models import User

from rest_framework.permissions import BasePermission


class SwitchRequestUserFromParam(BasePermission):
    message = 'This message should never be shown.'

    def has_object_permission(self, request, view, obj):
        if "as_user" in request.GET.keys():
            new_user = User.objects.filter(username=request.GET["as_user"])
            if not new_user.exists():
                return False
            request.user = new_user.first()

        return True

    def has_permission(self, request, view):
        if "as_user" in request.GET.keys():
            new_user = User.objects.filter(username=request.GET["as_user"])
            if not new_user.exists():
                return False
            request.user = new_user.first()

        return True


from flex_abac.mixins import ApplyFilterMixin
class DocumentsViewSet(ApplyFilterMixin, viewsets.ModelViewSet):
    permission_classes = [SwitchRequestUserFromParam, CanExecuteMethodPermission]
    serializer_class = DocumentSerializer
    queryset = Document.objects


    @action(detail=True, methods=['get'])
    def get_all_allowed_values(self, request, *args, **kwargs):
        view = AttributeTypeViewSet.as_view({'get': 'get_all_allowed_values'})
        data = view(request._request, *args, **kwargs)

        return data


class ExampleAppViewSet(viewsets.ModelViewSet):
    permission_classes = [SwitchRequestUserFromParam]

    @action(detail=False, methods=['get'])
    def get_all_allowed_values_per_user(self, request, *args, **kwargs):
        view = UserViewSet.as_view({'get': 'get_all_allowed_values'})
        data = view(request._request, *args, **kwargs)

        return data
