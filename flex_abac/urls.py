from django.urls import path, include
from rest_framework import routers
from flex_abac.views import UserViewSet
from flex_abac.views import (
    RoleViewSet, PolicyViewSet, ActionViewSet, AttributeTypeViewSet, FilterViewSet, PossibleValuesViewSet
)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'policies', PolicyViewSet)
router.register(r'actions', ActionViewSet)
router.register(r'attribute-types', AttributeTypeViewSet)
router.register(r'attribute-filters', FilterViewSet)
router.register(r'possible-values', PossibleValuesViewSet, basename="possible-values")

app_name = 'flex-abac'

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
]
