from flex_abac.models import RolePolicy
from flex_abac.serializers.role_policies import RolePolicySerializer
from rest_framework import viewsets
from flex_abac.permissions import CanExecuteMethodPermission
from django.conf import settings

USE_PERMISSIONS = getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False)


# ViewSets define the view behavior.
class RolePolicyViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission] if USE_PERMISSIONS else []
    queryset = RolePolicy.objects.all()
    serializer_class = RolePolicySerializer
