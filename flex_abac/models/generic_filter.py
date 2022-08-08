from django.db import models
from django.db.models import Subquery
from .base_filter import BaseFilter
from .policy_generic_filter import PolicyGenericFilter

from picklefield.fields import PickledObjectField


class GenericFilter(BaseFilter):
    value = PickledObjectField(editable=True)

    attribute_type = models.ForeignKey(
        'flex_abac.GenericAttribute',
        on_delete=models.CASCADE,
        related_name='values'
    )

    policies = models.ManyToManyField(
        'flex_abac.Policy',
        through='flex_abac.PolicyGenericFilter'
    )

    class Meta:
        unique_together = ("value", "attribute_type")

    @classmethod
    def print_all(cls):
        for attr in GenericFilter.objects.all():
            print("-", attr.value)

    def add_to_policy(self, policy):
        """
        TODO: Comment
        """
        PolicyGenericFilter.objects.get_or_create(
            policy=policy,
            value=self
        )

    def is_in_policy_scope(self, policy):
        matching_policy_values = PolicyGenericFilter.objects.filter(
                policy_id=policy.id,
                value_id__in=Subquery(
                    GenericFilter.objects.filter(
                        attribute_type_id=self.attribute_type.id,
                        value=self.value
                    ).values('id')
                )
            )

        return matching_policy_values.exists()

    def __str__(self):
        return '<GenericFilter:{}>'.format(self.value)