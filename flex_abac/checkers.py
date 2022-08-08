from .models import BaseAttribute
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import Q
from flex_abac.utils.helpers import get_subclasses


def is_object_in_scope(policy, obj):
    """
    Checks if the object is in the scope of a policy. It checks all the attributes related to a model and confirms
    that the values are valid for all the filters included on the policy for that attribute.

    :param policy: The policy to check.
    :type policy: flex_abac.models.Policy

    :param obj: The model object to check.
    :type obj: django.Model

    :returns:  bool -- True, if the object matches all the filters or no filter is applied over it. False, otherwise.
    """
    for attribute_type_model in get_subclasses(BaseAttribute):
        attribute_types = attribute_type_model.get_all_to_check_for_model(type(obj))
        for attribute_type in attribute_types:
            if not attribute_type.does_match(obj, policy):
                return False

    return True


def can_user_do(action_name, obj=None, user=None):
    """
    Given an action name, an object (optional), and a user, this function iterates over the entire set of
    policies associated with that user through the roles and checks the user has permissions.

    - If an object is provided, it checks that the user can do that action in any of the policies. If so, it then
      checks that the object is compliant with the set of filters associated with the matching policies.
    - If an object is not provided, it just checks that the action name is among the actions in the associated
      policies.

    Inside a policy, scopes are validated through an AND-like behavior; inside a role, policies are validated
    through an OR-like behavior. Therefore for optimization purposes, it is perfectly fine to check directly the
    policies. If one of them is in the scope, that means the user can do such action.

    :param action_name: The name of the action to check. It can be a single value or a string of comma-separated
           values.
    :type action_name: str

    :param obj: The model object type to check. Optional.
    :type obj: django.Model

    :param user: The user for which the permissions will be checked.
    :type user: django.contrib.auth.models.User

    :returns:  bool -- True, if the user can do the provided action. False, otherwise.
    """

    remaining_actions = action_name
    for policy in user.get_policies():
        try:
            if isinstance(action_name, list):
                for action in policy.actions.filter(name__in=action_name):
                    remaining_actions.remove(action.name)

                if len(remaining_actions) != 0:
                    continue
            else:
                policy.actions.get(name=action_name)
            if not obj or is_object_in_scope(policy, obj):
                return True
        except ObjectDoesNotExist:
            pass

    return False


def _are_all_required_attribute_types_in_query(
    query_attribute_values=None,
    target_model=None,
):
    are_all_types_covered = True
    missing_types = []
    for attribute_type_model in get_subclasses(BaseAttribute):
        attribute_types = attribute_type_model.get_all_to_check_for_model(
            target_model
        )
        for attribute_type in attribute_types:
            if not attribute_type.is_represented_in_query_values(
                [query_attribute_value for query_attribute_value in query_attribute_values
                 if query_attribute_value.attribute_type == attribute_type]
            ):
                are_all_types_covered = False
                missing_types.append(attribute_type)
    return are_all_types_covered, missing_types


def is_attribute_query_in_scope(
        query_attribute_values=None,
        target_model=None,
        user=None):
    """
    Checks whether the query attributes (e.g. REST api list filters) are allowed for the user, target model
    pair. The goal of this function is to forbid an user further access to resources if parameters used are
    already out of its scope.

    :param query_attribute_values: The list of attribute values (filters) to check.
    :type query_attribute_values: list <flex_abac.models.BaseFilter>

    :param user: The user for which the permissions will be checked.
    :type user: django.contrib.auth.models.User

    :returns: bool -- True, if the user can access the provided attribute values (filters). False,
              otherwise.
    """

    # We just need to fulfill one of the policies to ensure this
    for policy in user.get_policies():
        are_all_values_in_scope = True
        for value in query_attribute_values:
            if not value.is_in_policy_scope(policy):
                are_all_values_in_scope = False
                break
        if are_all_values_in_scope:
            return True

    return False


def get_query_attribute_values_from_mapping(attribute_mapping, target_model):
    """
    Given an attribute mapping, translates it to attribute values (filters) to be used during permissions
    checking.

    :param attribute_mapping: Dictionary where the keys correspond to the field_name in the attribute types, and the
           values are the query params offered to the user.
    :type attribute_mapping: dict

    :param target_model: The model object type to check.
    :type target_model: django.Model

    :returns:  list <flex_abac.models.BaseFilter> -- The list of attribute values (filters) to check.
    """

    attribute_values = []
    for attribute_type_model in get_subclasses(BaseAttribute):
        attribute_types = attribute_type_model.get_all_to_check_for_model(
            target_model
        ).filter(field_name__in=attribute_mapping.keys())

        for attribute_type in attribute_types:
            for value in attribute_mapping[attribute_type.field_name]:
                attribute_values.append(attribute_type.get_attribute_value(value))

    return attribute_values


def is_attribute_query_in_scope_from_mapping(user, attribute_mapping, target_model):
    """
    Given an attribute mapping, it checks whether the query attributes (e.g. REST API list filters) are allowed
    for the user, target model pair. The goal of this function is to forbid a user further access to resources
    if the used parameters are already out of his/her scope.

    It first translates the mapping to actual filters and then checks the permissions.

    :param user: The user for which the permissions will be checked.
    :type user: django.contrib.auth.models.User

    :param attribute_mapping: Dictionary where the keys correspond to the field_name in the attribute types, and the
           values are the query params offered to the user.
    :type attribute_mapping: dict

    :param target_model: The model object type to check.
    :type target_model: django.Model

    :returns: bool -- True, if the user can access the provided attribute values (filters). False,
              otherwise.
    """

    attribute_values = get_query_attribute_values_from_mapping(attribute_mapping, target_model)

    return is_attribute_query_in_scope(attribute_values, target_model, user)


def get_filter_for_valid_objects(scope, obj_type, base_lookup_name=None, action_name=None):
    """
    Given a scope and a model type, it provides a Django-ORM filter to be used to filter out just the valid objects
    for that model type, given the model type provided.

    Additionally, it is possible to provide an action_name to limit the scope, as well as a base_lookup name that
    will be used to nest the filter into a foreign-key field which will be referenced from an outer model.

    :param scope: The scope from which the filter will be applied. It can be a policy, a role (in which case all the
                  associated policies will be checked), or a user (which checks all the associated roles).
    :type scope: django.contrib.auth.models.User, flex_abac.models.Role, flex_abac.models.Policy

    :param obj_type: The model object type to check.
    :type obj_type: django.Model

    :param base_lookup_name: Optional. Name of the foreign-key field which will be checked on an outer model to reach
                             the provided ``obj_type``.
    :type base_lookup_name: str

    :param action_name: The name of the action to which the scope will be limited.
    :type action_name: str

    :returns: django.utils.tree.Node -- The tree of filters which represent the applicable filters.
    """

    filter, all_values_fields = scope.get_filter_for_valid_objects(obj_type, action_name)
    all_values_fields = set(all_values_fields)

    unrolled_filter = {}
    def unroll_filter(filter):
        for child in filter.children:
            if isinstance(child, Q):
                unroll_filter(child)
            else:
                key, value = child
                if not key in unrolled_filter.keys():
                    unrolled_filter[key] = []

                unrolled_filter[key].append(value)

    unroll_filter(filter)

    final_filter = Q()
    for key, values in unrolled_filter.items():
        if key in all_values_fields:
            continue

        current_filter = Q()

        if base_lookup_name:
            key = f"{base_lookup_name}__{key}"

        for value in values:
            current_filter |= Q(**{key: value})

        final_filter &= current_filter

    return final_filter


def list_valid_objects(policy, obj_type):
    """
    Given a policy and a model type, lists the valid object instances for that specific policy.

    :param policy: The policy from which the filter will be applied.
    :type policy: flex_abac.models.Policy

    :param obj_type: The model object type to check.
    :type obj_type: django.Model

    :returns:  list<django.Model> -- The list of valid instances for the provided policy and model type.
    """

    return obj_type.objects.filter(get_filter_for_valid_objects(policy, obj_type))




