from django.contrib.auth.models import User
from flex_abac.serializers import UserSerializer

from rest_framework import status

from rest_framework import viewsets

from flex_abac.serializers import UserRoleSerializer

from flex_abac.permissions import CanExecuteMethodPermission

from rest_framework.decorators import action
from rest_framework.response import Response

from flex_abac.models import BaseAttribute, ActionModel
from flex_abac.utils.helpers import get_subclasses
from django.contrib.contenttypes.models import ContentType
from flex_abac.serializers import PolymorphicFilterSerializer, PolymorphicPossibleValuesSerializer

from django.conf import settings

USE_PERMISSIONS = getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False)

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [CanExecuteMethodPermission] if USE_PERMISSIONS else []
    queryset = User.objects
    serializer_class = UserSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action == "list":
            context["remaining_depth"] = 1

        return context

    def get_permissions(self):
        if self.action in ('get_all_allowed_values',):
            self.permission_classes = []
        return super(self.__class__, self).get_permissions()

    @action(detail=True, methods=['put'])
    def add_roles(self, request, pk=None):
        serializer = UserRoleSerializer(self.get_object(), many=False)
        serializer.update(self.get_object(), {"roles": request.data.getlist("roles")})

        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_roles(self, request, pk=None):
        serializer = UserRoleSerializer(self.get_object(), many=False)
        serializer.delete(self.get_object(), {"roles": request.data.getlist("roles")})

        return Response(serializer.data)

    @action(detail=False, methods=['get', 'put'])
    def get_all_allowed_values(self, request):
        content_types = []
        models_list = request.GET.get("models", "")
        for model_name in models_list.split(","):
            try:
                app_label, model = model_name.split(".")
            except ValueError:
                return Response(f"{model_name} should follow the format <app_name>.<model_name>",
                                status=status.HTTP_400_BAD_REQUEST)
            content_type = ContentType.objects.filter(app_label=app_label, model=model)
            if not content_type.exists():
                return Response(f"{model_name} is not in the list of available models!",
                                status=status.HTTP_400_BAD_REQUEST)
            content_types.append(content_type[0].id)

        allowed_values = []
        possible_values = []
        for attribute_type_model in get_subclasses(BaseAttribute):
            for attribute_type in attribute_type_model.get_all_attributes_from_content_types(content_types).all():
                allowed_values_for_attribute = attribute_type.get_all_values_for_user(request.user)
                if allowed_values_for_attribute.exists():
                    allowed_values += allowed_values_for_attribute
                else:
                    possible_values += [attribute_type]

        allowed_values = list(set(allowed_values))


        final_possible_values = []
        for item in PolymorphicPossibleValuesSerializer(possible_values, many=True).data:
            final_possible_values += item["possible_values"]

        allowed_values_serializer = PolymorphicFilterSerializer(allowed_values, many=True)


        return Response(allowed_values_serializer.data + final_possible_values)
