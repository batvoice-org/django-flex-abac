from django.db import models
from django.db.models import Subquery
from .base_filter import BaseFilter
from .policy_categorical_filter import PolicyCategoricalFilter
from django.core.exceptions import ValidationError

from picklefield.fields import PickledObjectField


class CategoricalFilter(BaseFilter):
    value = PickledObjectField(editable=True)

    attribute_type = models.ForeignKey(
        'flex_abac.CategoricalAttribute',
        on_delete=models.CASCADE,
        related_name='values'
    )

    class Meta:
        unique_together = ("attribute_type", "value")

    policies = models.ManyToManyField(
        'flex_abac.Policy',
        through='flex_abac.PolicyCategoricalFilter'
    )


    @classmethod
    def print_all(cls):
        for attr in CategoricalFilter.objects.all():
            print("-", attr.value)

    def add_to_policy(self, policy):
        """
        TODO: Comment
        """
        PolicyCategoricalFilter.objects.get_or_create(
            policy=policy,
            value=self
        )

    def is_in_policy_scope(self, policy):
        # Checks the attribute exists for that policy, otherwise the policy is accepted for this specific attribute
        if not PolicyCategoricalFilter.objects.filter(policy_id=policy.id,
                                                      value__attribute_type_id=self.attribute_type.id).exists():
            return True

        matching_policy_values = PolicyCategoricalFilter.objects.filter(
                policy_id=policy.id,
                value_id__in=Subquery(
                    CategoricalFilter.objects.filter(
                        attribute_type_id=self.attribute_type.id,
                        value=self.value
                    ).values('id')
                )
            )

        return matching_policy_values.exists()

    def __str__(self):
        return '<CategoricalFilter:{} ({})>'.format(self.value, self.attribute_type)