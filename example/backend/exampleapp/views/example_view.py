from rest_framework import viewsets

from django.db import models
from django.db.models import Q
from django.http import HttpResponseForbidden

from flex_abac.checkers import get_filter_for_valid_objects
from rest_framework.decorators import api_view, permission_classes

from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView

from rest_framework.decorators import action
from rest_framework.response import Response
from exampleapp.serializers import DocumentSerializer, EvaluationSerializer
from exampleapp.models import Document, Evaluation

from flex_abac.utils.mappings import MappingItem, DefaultAttributeMappingGenerator


from flex_abac.permissions import (
    CanExecuteMethodPermission,
    flex_abac_params,
    flex_abac_params_api_view,
)

from flex_abac.utils import (
    ActionNameGenerator,
    DefaultActionNameGenerator,
    MethodAndTypeActionNameGenerator,
)
from flex_abac.checkers import can_user_do
from flex_abac.mixins import ApplyFilterMixin


class SimpleExampleViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission]
    serializer_class = DocumentSerializer
    queryset = Document.objects

    @action(detail=False, methods=["GET"])
    def filter(self, request, *args, **kwargs):
        return Response("example action")


class ComplexExampleViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission]
    serializer_class = DocumentSerializer
    queryset = Document.objects
    flex_abac_action_name = DefaultActionNameGenerator

    def get_attribute_mapping(self):
        if self.action == "filter":
            return [
                MappingItem(obj_type=Document, field_name="brand__name", values_type=str,
                            function_value=lambda view: view.request.GET.getlist("brand")),
                MappingItem(obj_type=Document, field_name="desk__name", values_type=str,
                            function_value=lambda view: view.request.GET.getlist("desk")),
                MappingItem(obj_type=Document, field_name="id", values_type=int,
                            function_value=lambda view: view.request.GET.getlist("id")),
            ]
        else:
            return None

    @action(detail=False, methods=["GET"])
    def filter(self, request, *args, **kwargs):
        return Response("example action")

    @action(detail=False, flex_abac_action_name="action_name_static")
    def checker_static_name(self, request, *args, **kwargs):
        return Response("example action")

    class CustomActionNameGenerator(ActionNameGenerator):
        @classmethod
        def get_action_name(cls, view):
            return "custom_name_generator"

    @action(detail=False, flex_abac_action_name=CustomActionNameGenerator)
    def checker_custom_generated_name(self, request, *args, **kwargs):
        return Response("example action")

    @action(detail=False, methods=["GET", "POST"], flex_abac_action_name=MethodAndTypeActionNameGenerator)
    def checker_method_and_type(self, request, *args, **kwargs):
        return Response("example action")

    @action(detail=False, methods=["GET"])
    def checker_no_scope(self, request, *args, **kwargs):
        return Response("example action")


class RetrieveDocumentsViewSet(ApplyFilterMixin, viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    queryset = Document.objects

    @action(detail=False, methods=["GET"])
    def filter(self, request, *args, **kwargs):
        return Response("example action")


class IndirectPermissionsViewSet(ApplyFilterMixin, viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission]
    serializer_class = EvaluationSerializer
    queryset = Evaluation.objects
    base_lookup = "document"
    base_model = Document

    def get_attribute_mapping(self):
        if self.action in ("filter", "filter2"):
            return [
                MappingItem(obj_type=Document, field_name="brand__name", values_type=str,
                            function_value=lambda view: view.request.GET.getlist("brand")),
                MappingItem(obj_type=Document, field_name="desk__name", values_type=str,
                            function_value=lambda view: view.request.GET.getlist("desk")),
                MappingItem(obj_type=Document, field_name="id", values_type=int,
                            function_value=lambda view: view.request.GET.getlist("id")),
            ]
        else:
            return None

    @action(detail=False, methods=["GET"])
    def filter(self, request, *args, **kwargs):
        return Response("example action")

    @action(detail=False, methods=["GET"])
    def filter2(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset)

        return Response(EvaluationSerializer(queryset.all(), many=True).data)


@flex_abac_params(flex_abac_action_name="example_view_as_function_simple")
@api_view(['GET'])
@permission_classes([CanExecuteMethodPermission])
def example_view_as_function_simple(request, format=None, **kwargs):
    return Response("OK")


@flex_abac_params(flex_abac_action_name="example_view_as_function",
                 attribute_mapping={
                    MappingItem(obj_type=Document, field_name="brand__name", values_type=str,
                                function_value=lambda view: view.request.GET.getlist("brand")),
                    MappingItem(obj_type=Document, field_name="desk__name", values_type=str,
                                function_value=lambda view: view.request.GET.getlist("desk")),
                    MappingItem(obj_type=Document, field_name="id", values_type=int,
                                function_value=lambda view: view.request.GET.getlist("id")),
                 }
                 )
@api_view(['GET'])
@permission_classes([CanExecuteMethodPermission])
def example_view_as_function(request, format=None, **kwargs):
    valid_objects_filter = get_filter_for_valid_objects(request.user, Document)

    valid_objects_filter &= Q(brand__name__in=request.GET.getlist("brand"))
    valid_objects_filter &= Q(desk__name__in=request.GET.getlist("desk"))
    valid_objects_filter &= Q(id__in=list(map(int, request.GET.getlist("id"))))

    queryset = Document.objects.filter(valid_objects_filter)

    return Response(DocumentSerializer(queryset.all(), many=True).data)

@flex_abac_params(flex_abac_action_name="example_detail_as_function")
@api_view(['GET'])
@permission_classes([CanExecuteMethodPermission])
def example_detail_as_function(request, format=None, pk=None, **kwargs):
    if not can_user_do(action_name="example_detail_as_function",
                obj=Document.objects.get(id=pk),
                user=request.user):
        return HttpResponseForbidden(f"You cannot access object {pk}")

    return Response("OK")

class ExampleAPIViewSimple(APIView):
    permission_classes = [CanExecuteMethodPermission]

    def get(self, request, format=None):
        return Response("OK")


class ExampleAPIViewComplex(APIView):

    queryset = Document.objects

    @flex_abac_params_api_view()
    def get(self, request, format=None, **kwargs):
        return Response("OK")


class ExampleAPIViewComplexFiltered(APIView):

    queryset = Document.objects

    @flex_abac_params_api_view(flex_abac_action_name="example_filtered",
                              attribute_mapping={
                                  MappingItem(obj_type=Document, field_name="brand__name", values_type=str,
                                              function_value=lambda view: view.request.GET.getlist("brand")),
                                  MappingItem(obj_type=Document, field_name="desk__name", values_type=str,
                                              function_value=lambda view: view.request.GET.getlist("desk")),
                                  MappingItem(obj_type=Document, field_name="id", values_type=int,
                                              function_value=lambda view: view.request.GET.getlist("id")),
                              }
                              )
    def get(self, request, format=None, **kwargs):
        valid_objects_filter = get_filter_for_valid_objects(request.user, Document)

        valid_objects_filter &= Q(brand__name__in=request.GET.getlist("brand"))
        valid_objects_filter &= Q(desk__name__in=request.GET.getlist("desk"))
        valid_objects_filter &= Q(id__in=list(map(int, request.GET.getlist("id"))))

        queryset = Document.objects.filter(valid_objects_filter)

        return Response(DocumentSerializer(queryset.all(), many=True).data)


class ExampleAPIViewDetail(APIView):

    queryset = Document.objects

    @flex_abac_params_api_view(flex_abac_action_name="example_api_view_detail",
                              obj=lambda kwargs: Document.objects.get(pk=kwargs["pk"]))
    def get(self, *args, **kwargs):
        return Response("OK")


class MappingExample1ViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission]
    serializer_class = DocumentSerializer
    queryset = Document.objects
    flex_abac_action_name = DefaultActionNameGenerator
    attribute_mapping = DefaultAttributeMappingGenerator()

    @action(detail=False, methods=["GET"])
    def filter(self, request, *args, **kwargs):
        return Response("example action")

class MappingExample2ViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission]
    serializer_class = DocumentSerializer
    queryset = Document.objects
    flex_abac_action_name = DefaultActionNameGenerator

    def get_attribute_mapping(self):
        if self.action == "filter":
            return DefaultAttributeMappingGenerator.get_attribute_mapping(self)
        else:
            return None


    @action(detail=False, methods=["GET"])
    def filter(self, request, *args, **kwargs):
        return Response("example action")
