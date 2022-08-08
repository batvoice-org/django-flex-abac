from django.db import models
from django.db.models import Subquery
from django.db.models.query import Q


class Role(models.Model):
    name = models.CharField(
        max_length=512,
        unique=True
    )

    policies = models.ManyToManyField(
        'flex_abac.Policy',
        through='flex_abac.RolePolicy'
    )

    users = models.ManyToManyField(
        'auth.User',
        through='flex_abac.UserRole'
    )

    def get_filter_for_valid_objects(self, obj_type, action_name=None):
        or_filter = Q()
        all_values_fields = []
        policies = self.policies
        if action_name:
            policies = policies.filter(action__name=action_name)


        for policy in policies.all():
            current_filter, current_all_values_fields = policy.get_filter_for_valid_objects(obj_type)
            or_filter |= current_filter
            all_values_fields += current_all_values_fields

        return or_filter, all_values_fields


    def __str__(self):
        return '<Role: {}>'.format(
            self.name
        )
