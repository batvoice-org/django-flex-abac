from django.db import models
from django.db.models import Subquery
from treebeard.mp_tree import MP_Node
from django.core.validators import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from flex_abac.utils.treebeard import print_node
from .base_filter import BaseFilter
from django.apps import apps

from .policy_materialized_nested_categorical_filter import PolicyMaterializedNestedCategoricalFilter

from polymorphic.base import ManagerInheritanceWarning
import warnings
warnings.filterwarnings('ignore', category=ManagerInheritanceWarning)

class MaterializedNestedCategoricalFilter(MP_Node, BaseFilter):
    value = models.CharField(max_length=100)
    attribute_type = models.ForeignKey(
        'flex_abac.MaterializedNestedCategoricalAttribute',
        on_delete=models.CASCADE,
        related_name='values'
    )
    node_order_by = ['value']

    policies = models.ManyToManyField(
        'flex_abac.Policy',
        through='flex_abac.PolicyMaterializedNestedCategoricalFilter'
    )

    class Meta:
        verbose_name = 'Materialized Nested Categorical Filter'
        verbose_name_plural = 'Materialized Nested Categorical Filters'

        unique_together = ("value", "attribute_type")

    @classmethod
    def print_all(cls):
        for attr in PolicyMaterializedNestedCategoricalFilter.objects.filter(depth=1):
            print_node(attr, "value")

    def __str__(self):
        return '<MaterializedNestedCategoricalFilter:{}>'.format(self.value)

    def clean(self, *args, **kwargs):
        parent = self.get_parent()
        if parent:
            if not self.attribute_type.is_child_of(parent.attribute_type):
                raise ValidationError({
                    NON_FIELD_ERRORS: ['value hierarchy does not match attribute hierarchy', ],
                })
        super(MP_Node, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(MP_Node, self).save(*args, **kwargs)

    def add_to_policy(self, policy):
        """
        TODO: Comment
        """
        PolicyMaterializedNestedCategoricalFilter.objects.get_or_create(
            policy=policy,
            value=self
        )

    def is_in_policy_scope(self, policy):
        MaterializedNestedCategoricalAttribute = apps.get_model(
            'flex_abac',
            'materializednestedcategoricalattribute'
        )

        self_and_ancestor_attribute_types = MaterializedNestedCategoricalAttribute.objects.filter(
                                                        id=self.attribute_type.id
                                                    ) \
                                                    | self.attribute_type.get_ancestors()

        policy_values_of_matching_types = PolicyMaterializedNestedCategoricalFilter.objects.filter(
            policy_id=policy.id,
            value_id__in=Subquery(
                MaterializedNestedCategoricalFilter.objects.filter(
                    attribute_type__in=self_and_ancestor_attribute_types
                ).values('id')
            )
        )
        values_of_matching_types = MaterializedNestedCategoricalFilter.objects.filter(
            id__in=policy_values_of_matching_types.values('value_id')
        )

        self_ancestors = self.get_ancestors()

        if self in values_of_matching_types:
            return True
        else:
            if any([self == v or v in self_ancestors for v in values_of_matching_types]):
                return True
        return False