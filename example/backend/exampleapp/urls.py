from django.urls import path, include
from rest_framework import routers

from .views import (
    SimpleExampleViewSet,
    ComplexExampleViewSet,
    RetrieveDocumentsViewSet,
    IndirectPermissionsViewSet,
    example_view_as_function_simple,
    example_view_as_function,
    example_detail_as_function,
    ExampleAPIViewSimple,
    ExampleAPIViewComplex,
    ExampleAPIViewComplexFiltered,
    ExampleAPIViewDetail,
    MappingExample1ViewSet,
    MappingExample2ViewSet,
    DocumentsViewSet,
    ExampleAppViewSet
)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'simple-example', SimpleExampleViewSet, basename="simple-example")
router.register(r'complex-example', ComplexExampleViewSet, basename="complex-example")
router.register(r'mapping-example1', MappingExample1ViewSet, basename="mapping-example1")
router.register(r'mapping-example2', MappingExample2ViewSet, basename="mapping-example2")
router.register(r'retrieve-all', RetrieveDocumentsViewSet, basename="retrieve-all")
router.register(r'indirect-permissions', IndirectPermissionsViewSet, basename="indirect-permissions")
router.register(r'documents', DocumentsViewSet, basename="documents")
router.register(r'exampleapp', ExampleAppViewSet, basename="exampleapp")

app_name = 'exampleapp'

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('example-view-as-function-simple/', example_view_as_function_simple, name="example_view_as_function_simple"),
    path('example-view-as-function/', example_view_as_function, name="example_view_as_function"),
    path('example-detail-as-function/<int:pk>/', example_detail_as_function, name="example_detail_as_function"),
    path('example-api-view-simple/', ExampleAPIViewSimple.as_view(), name="example_api_view_simple"),
    path('example-api-view-complex/', ExampleAPIViewComplex.as_view(), name="example_api_view_complex"),
    path('example-api-view-complex-filtered/', ExampleAPIViewComplexFiltered.as_view(), name="example_api_view_complex_filtered"),
    path('example-api-view-detail/<int:pk>/', ExampleAPIViewDetail.as_view(), name="example_api_view_detail"),
]

