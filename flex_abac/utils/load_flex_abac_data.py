from flex_abac.models import (
    UserRole, Role, Policy, Action,
    BaseAttribute, BaseFilter,
    CategoricalAttribute, ModelCategoricalAttribute, CategoricalFilter, PolicyCategoricalFilter
)

from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType

from django.conf import settings

import warnings


def load_flex_abac_data(admin_users=[], viewer_users=[], clean_users=False):
    """
    Loads the necessary permissions in the database in order to restrict permissions to the users for the provided
    REST API.

    It creates several attributes, filters, actions, policies, and roles, which are easily recognized through the
    name, which starts with ``flex-abac``.

    To make these permissions functional, the settings variable ``USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS``
    should be set to ``True``.

    There are two special roles, ``flex-abac Admin Role`` and ``flex-abac Admin Role``, which allow assigned users
    to admin and to read the flex-abac related permissions, respectively. Users can be easily assigned to these
    roles through the ``admin_users`` and ``viewer_users`` variables. By default, superusers will be added to the
    ``admin_users`` role.

    .. note::

        If you accidentally partially/fully removed the flex-abac permissions from the database, you can restore
        them at any moment using this function.

    :param admin_users: Adds the flex-abac admin role to the provided user names.
    :type admin_users: list<str>

    :param viewer_users: Adds the flex-abac viewer role to the provided user names.
    :type viewer_users: list<str>

    :param clean: Indicates whether flex-abac roles should be removed for all users before adding new permissions.
    :type clean: bool
    """

    if not getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", None):
        warnings.warn("Variable USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS is not set to True. Please be sure it set to "
                      "True in the settings.py file before sending this code to production, in case you want these "
                      "permissions to be applied.")

    flex_abac_admin_role, _ = Role.objects.get_or_create(name=flex_abac.constants.SUPERADMIN_ROLE)
    flex_abac_viewer_role, _ = Role.objects.get_or_create(name="flex-abac Viewer Role")

    flex_abac_admin_policy, _ = Policy.objects.get_or_create(name="flex-abac Admin Policy")
    flex_abac_viewer_policy, _ = Policy.objects.get_or_create(name="flex-abac Viewer Policy")

    # flex_abac_hidden_policy, _ = Policy.objects.get_or_create(name="flex-abac Hidden Policy")

    flex_abac_admin_role.policies.add(flex_abac_admin_policy)
    flex_abac_viewer_role.policies.add(flex_abac_viewer_policy)

    # flex_abac_admin_role.policies.add(flex_abac_hidden_policy)
    # flex_abac_viewer_role.policies.add(flex_abac_hidden_policy)

    # Actions creation
    admin_methods = ["read", "write"]
    viewer_methods = ["read"]
    model_names = ["user", "role", "policy", "action", "basefilter", "baseattribute"]
    for model_name in model_names:
        for method_name in admin_methods:
            admin_method, _ = Action.objects.get_or_create(name=f"{model_name}__{method_name}",
                                      pretty_name=f"flex-abac: Allows HTTP {method_name} method for {model_name}")
            flex_abac_admin_policy.actions.add(admin_method)

        for method_name in viewer_methods:
            viewer_method, _ = Action.objects.get_or_create(name=f"{model_name}__{method_name}",
                                      pretty_name=f"flex-abac: Allows HTTP {method_name} method for {model_name}")
            flex_abac_viewer_policy.actions.add(viewer_method)

    # Attributes creation
    role_attribute, _ = CategoricalAttribute.objects.get_or_create(name="flex-abac attr: Role name",
                                                                   field_name="name__fbnotsimilar")
    policy_attribute, _ = CategoricalAttribute.objects.get_or_create(name="flex-abac attr: Policy name",
                                                                     field_name="name__fbnotsimilar")
    action_attribute, _ = CategoricalAttribute.objects.get_or_create(name="flex-abac attr: Action name",
                                                                     field_name="pretty_name__fbnotsimilar")
    attributetype_attribute, _ = CategoricalAttribute.objects.get_or_create(name="flex-abac attr: Attribute Type name",
                                                                            field_name="name__fbnotsimilar")
    filter_attribute, _ = CategoricalAttribute.objects.get_or_create(name="flex-abac attr: Filter name",
                                                                     field_name="name__fbnotsimilar")

    # Content types
    role_content_type = ContentType.objects.get_for_model(Role)
    policy_content_type = ContentType.objects.get_for_model(Policy)
    action_content_type = ContentType.objects.get_for_model(Action)
    attributetype_content_type = ContentType.objects.get_for_model(BaseAttribute)
    filter_content_type = ContentType.objects.get_for_model(BaseFilter)

    # Adding to model registry
    if not ModelCategoricalAttribute.objects.filter(attribute_type=role_attribute).exists():
        ModelCategoricalAttribute.objects.create(attribute_type=role_attribute,
                                                 owner_content_object=role_content_type)

    if not ModelCategoricalAttribute.objects.filter(attribute_type=policy_attribute).exists():
        ModelCategoricalAttribute.objects.create(attribute_type=policy_attribute,
                                                 owner_content_object=policy_content_type)

    if not ModelCategoricalAttribute.objects.filter(attribute_type=action_attribute).exists():
        ModelCategoricalAttribute.objects.create(attribute_type=action_attribute,
                                                 owner_content_object=action_content_type)

    if not ModelCategoricalAttribute.objects.filter(attribute_type=attributetype_attribute).exists():
        ModelCategoricalAttribute.objects.create(attribute_type=attributetype_attribute,
                                                 owner_content_object=attributetype_content_type)

    if not ModelCategoricalAttribute.objects.filter(attribute_type=filter_attribute).exists():
        ModelCategoricalAttribute.objects.create(attribute_type=filter_attribute,
                                                 owner_content_object=filter_content_type)

    # Adding filters
    regex_role_filter, _ = CategoricalFilter.objects.get_or_create(name="flex-abac: Role filter",
                                                                   value="%flex-abac ((Admin)|(Viewer)) Role%",
                                                                   attribute_type=role_attribute)
    regex_policy_filter, _ = CategoricalFilter.objects.get_or_create(name="flex-abac: Policy filter",
                                                                     value="%flex-abac ((Admin)|(Viewer)|(Hidden)) Policy%",
                                                                     attribute_type=policy_attribute)
    regex_action_filter, _ = CategoricalFilter.objects.get_or_create(name="flex-abac: Action filter",
                                                                     value="%flex-abac: %",
                                                                     attribute_type=action_attribute)
    regex_attributetype_filter, _ = CategoricalFilter.objects.get_or_create(name="flex-abac: Attribute Type filter",
                                                                            value="%flex-abac attr: %",
                                                                            attribute_type=attributetype_attribute)
    regex_filter_filter, _ = CategoricalFilter.objects.get_or_create(name="flex-abac: Filter filter",
                                                                     value="%flex-abac: %",
                                                                     attribute_type=filter_attribute)

    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_admin_policy, value=regex_role_filter)
    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_admin_policy, value=regex_policy_filter)
    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_admin_policy, value=regex_action_filter)
    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_admin_policy, value=regex_attributetype_filter)
    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_admin_policy, value=regex_filter_filter)

    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_viewer_policy, value=regex_role_filter)
    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_viewer_policy, value=regex_policy_filter)
    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_viewer_policy, value=regex_action_filter)
    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_viewer_policy, value=regex_attributetype_filter)
    PolicyCategoricalFilter.objects.get_or_create(policy=flex_abac_viewer_policy, value=regex_filter_filter)

    # Adding superusers to admin role by default
    flex_abac_admin_role.users.add(*User.objects.filter(is_superuser=True))

    if clean_users:
        UserRole.objects.filter(role=flex_abac_admin_role).all().delete()
        UserRole.objects.filter(role=flex_abac_viewer_role).all().delete()

    flex_abac_admin_role.users.add(*User.objects.filter(username__in=admin_users))
    flex_abac_viewer_role.users.add(*User.objects.filter(username__in=viewer_users))



