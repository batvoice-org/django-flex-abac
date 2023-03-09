from django.db import models
from . import BaseAttribute
from django.db.models import Subquery
from django.db.models.query import Q
from flex_abac.utils.helpers import get_subclasses


class Policy(models.Model):
    name = models.CharField(
        max_length=512,
        unique=True
    )

    actions = models.ManyToManyField(
        'flex_abac.Action',
        through='flex_abac.PolicyAction'
    )

    roles = models.ManyToManyField(
        'flex_abac.Role',
        through='flex_abac.RolePolicy'
    )

    class Meta:
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'

    def get_attribute_values(
            self,
            attribute_value_model,
            policy_attribute_value_model
    ):

        return attribute_value_model.objects.filter(
            id__in=Subquery(
                policy_attribute_value_model.objects.filter(policy_id=self.pk).values('value_id')
            )
        )

    def get_filter_for_valid_objects(self, obj_type, *args, **kwargs):
        and_filter = Q()
        all_values_fields = []
        for attribute_type_model in get_subclasses(BaseAttribute):
            attribute_types = attribute_type_model.get_all_to_check_for_model(obj_type)
            for attribute_type in attribute_types:
                current_filter, current_all_values_fields = attribute_type.get_filter(self)
                and_filter &= current_filter
                all_values_fields += current_all_values_fields

        return and_filter, all_values_fields

    def __str__(self):
        return '<Policy: {}>'.format(self.name)
