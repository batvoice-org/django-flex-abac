from django.contrib.auth.models import User, AnonymousUser
from . import UserRole, Role, Policy, Action
from django.db.models.query import Q


def get_filter_for_valid_objects(self, obj_type, action_name=None):
    or_filter = Q()
    all_values_fields = []

    if self.is_anonymous:
        user_roles = UserRole.objects.exclude(user__isnull=False)
    else:
        user_roles = UserRole.objects.filter(user=self)

    for user_role in user_roles:
        current_filter, current_all_values_fields = user_role.role.get_filter_for_valid_objects(obj_type, action_name)
        or_filter |= current_filter
        all_values_fields += current_all_values_fields

    return or_filter, all_values_fields


def get_roles(self):
    if self.is_anonymous:
        return Role.objects.filter(id__in=UserRole.objects.exclude(user__isnull=False).values("role"))
    else:
        return Role.objects.filter(users=self)


def get_policies(self):
    if self.is_anonymous:
        return Policy.objects.filter(roles__in=UserRole.objects.exclude(user__isnull=False).values("role"))
    else:
        return Policy.objects.filter(roles__users=self)

def get_actions(self):
    if self.is_anonymous:
        return Action.objects.filter(policies__roles__in=UserRole.objects.exclude(user__isnull=False).values("role"))
    else:
        return Action.objects.filter(policies__roles__users=self)


User.add_to_class("get_filter_for_valid_objects", get_filter_for_valid_objects)
User.add_to_class("get_roles", get_roles)
User.add_to_class("get_policies", get_policies)
User.add_to_class("get_actions", get_actions)

AnonymousUser.get_filter_for_valid_objects = get_filter_for_valid_objects
AnonymousUser.get_roles = get_roles
AnonymousUser.get_policies = get_policies
AnonymousUser.get_actions = get_actions
