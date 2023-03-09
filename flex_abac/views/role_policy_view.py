from flex_abac.models import RolePolicy
from flex_abac.serializers.role_policies import RolePolicySerializer
from rest_framework import viewsets
from django.conf import settings
from flex_abac.permissions import CanExecuteMethodPermission
from rest_framework.decorators import action
from rest_framework.response import Response

USE_PERMISSIONS = getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False)


# ViewSets define the view behavior.
class RolePolicyViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission] if USE_PERMISSIONS else []
    queryset = RolePolicy.objects.all()
    serializer_class = RolePolicySerializer

    @action(detail=False, methods=['post'])
    def detach_policy_and_role(self, request,):
        RolePolicy.objects.get(
            policy__id=request.data.get('policy_id'),
            role__id=request.data.get('role_id')
        ).delete()
        return Response({})
