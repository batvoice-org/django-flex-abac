from flex_abac.checkers import can_user_do, is_attribute_query_in_scope_from_mapping
from rest_framework.permissions import BasePermission

from flex_abac.utils.mappings import get_mapping_from_viewset
from flex_abac.utils.action_names import get_action_name

from django.core.validators import ValidationError

import logging
logger = logging.getLogger(__name__)


class CanExecuteMethodPermission(BasePermission):
    """
    This class extends the ``rest_framework.permissions.BasePermission`` class and checks whether the user has access or not
    based on the permissions configured on the database.

    It can be added to your Views, ViewSets, etc. by adding it to the list of `permission_classes`.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(CanExecuteMethodPermission, self).__init__(*args, **kwargs)

        self.custom_error_message = "Unknown"

    def has_object_permission(self, request, view, obj):
        if getattr(view, "base_lookup", None):
            obj = getattr(obj, view.base_lookup, obj)

        self.custom_error_message = f"User is not allowed access object {obj.id}!. User: {request.user}, " \
                                    f"action_name: {get_action_name(view)}"
        return can_user_do(get_action_name(view), obj=obj, user=request.user)

    def has_permission(self, request, view):
        attribute_mapping = get_mapping_from_viewset(view)

        try:
            # Does mapping
            if attribute_mapping:
                # Checking for all the additional objects, not just the queryset
                attribute_query_in_scope_from_mapping = True
                for target_model in attribute_mapping.keys():
                    if not is_attribute_query_in_scope_from_mapping(attribute_mapping=attribute_mapping[target_model],
                                                               target_model=target_model,
                                                               user=request.user):

                        attribute_query_in_scope_from_mapping = False

                if attribute_query_in_scope_from_mapping:
                    self.custom_error_message = f"User is not allowed to do so!. User: {request.user}, " \
                                                f"action_name: {get_action_name(view)}"
                    return can_user_do(get_action_name(view), user=request.user)
                else:
                    self.custom_error_message = f"Attribute query is not in the scope for the given parameters! " \
                                                f"User: {request.user}, attribute mapping: {attribute_mapping}"
                    return False

            else:   # No get_attribute_mapping() provided or returns None
                self.custom_error_message = f"User is not allowed to do so!. User: {request.user}, " \
                                            f"action_name: {get_action_name(view)}"
                return can_user_do(get_action_name(view), user=request.user)

        except ValidationError as ve:
            logger.warning(f"Validation error: {repr(ve)}")
            self.custom_error_message = f"Validation error: {repr(ve)}"
            return False

    @property
    def message(self):
        return f"Permission not allowed: {self.custom_error_message}"

def flex_abac_params(flex_abac_action_name=None, attribute_mapping=None, obj=None):
    """
    This is a decorator you can use to pass permissions params to your view functions so permissions can be applied.

    Example:

    .. code-block:: python

        @flex_abac_params(flex_abac_action_name="example_action_name",
                 attribute_mapping={
                    MappingItem(obj_type=Document, field_name="topic__name", values_type=str,
                                function_value=lambda view: view.request.GET.getlist("brand")),
                    MappingItem(obj_type=Document, field_name="category__name", values_type=str,
                                function_value=lambda view: view.request.GET.getlist("category")),
                 })
        @api_view(['GET'])
        @permission_classes([CanExecuteMethodPermission])
        def example_view_as_function(request, format=None, **kwargs):
            return Response("OK")

    :param flex_abac_action_name: The action name (or action name generator) associated to the endpoint.
    :type flex_abac_action_name: str, flex_abac.utils.action_names.ActionNameGenerator

    :param attribute_mapping: Optional. The attribute mapping for which permissions will be checked.
    :type attribute_mapping: list<flex_abac.utils.mappings.MappingItem>
    """

    def decorator(api_view_obj):
        def wrapper(*args, **kwargs):
            if attribute_mapping:
                kwargs.update({"attribute_mapping": attribute_mapping})

            if not "flex_abac_action_name" in kwargs.keys():
                kwargs.update({"flex_abac_action_name": flex_abac_action_name if flex_abac_action_name else api_view_obj.__name__.lower()})

            output = api_view_obj(*args, **kwargs)

            return output

        return wrapper

    return decorator


def flex_abac_params_api_view(flex_abac_action_name=None, attribute_mapping=None, obj=None):
    """
    This is a decorator you can use to provide specific permissions to your actions inside an ``APIView``.

    Example:

    .. code-block:: python

        class ExampleAPIViewComplexFiltered(APIView):

            ...

            @flex_abac_params_api_view(flex_abac_action_name="example_action_name",
                                      attribute_mapping={
                                          MappingItem(obj_type=Document, field_name="topic__name", values_type=str,
                                                      function_value=lambda view: view.request.GET.getlist("brand")),
                                          MappingItem(obj_type=Document, field_name="category__name", values_type=str,
                                                      function_value=lambda view: view.request.GET.getlist("category")),
                                      })
            def get(self, request, format=None, **kwargs):

                return Response("OK")

    :param flex_abac_action_name: The action name (or action name generator) associated to the endpoint.
    :type flex_abac_action_name: str, flex_abac.utils.action_names.ActionNameGenerator

    :param attribute_mapping: Optional. The attribute mapping for which permissions will be checked.
    :type attribute_mapping: list<flex_abac.utils.mappings.MappingItem>

    :param obj: Optional. Object to which permissions will be checked against
    :type obj: django.Model

    """

    def decorator(func):
        def wrapper(api_view_obj, *args, **kwargs):

            kwargs.update({"attribute_mapping": attribute_mapping})

            api_view_obj.flex_abac_action_name = flex_abac_action_name if flex_abac_action_name else f"{api_view_obj.__class__.__name__.lower()}__{func.__name__.lower()}"
            api_view_obj.attribute_mapping = attribute_mapping

            if not CanExecuteMethodPermission in api_view_obj.permission_classes:
                api_view_obj.permission_classes += [CanExecuteMethodPermission]

            current_obj = obj if obj else None
            if callable(current_obj):
                current_obj = current_obj(kwargs)

            if current_obj:
                api_view_obj.check_object_permissions(api_view_obj.request, current_obj)
            else:
                api_view_obj.check_permissions(api_view_obj.request)

            output = func(api_view_obj, *args, **kwargs)

            return output

        return wrapper

    return decorator