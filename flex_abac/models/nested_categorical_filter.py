from django.db import models
from django.db.models import Subquery
from treebeard.models import Node as TreebeardNode
from flex_abac.utils.treebeard import print_node
from .base_filter import BaseFilter

from picklefield.fields import PickledObjectField

from .policy_nested_categorical_filter import PolicyNestedCategoricalFilter


class NestedCategoricalFilter(BaseFilter):
    value = PickledObjectField()

    attribute_type = models.ForeignKey(
        'flex_abac.NestedCategoricalAttribute',
        on_delete=models.CASCADE,
        related_name='values'
    )

    policies = models.ManyToManyField(
        'flex_abac.Policy',
        through='flex_abac.PolicyNestedCategoricalFilter'
    )

    class Meta:
        unique_together = ("value", "attribute_type")

    @classmethod
    def print_all(cls):
        for attr in NestedCategoricalFilter.objects.filter(depth=1):
            print_node(attr, "value")

    def __str__(self):
        return '<NestedCategoricalFilter:{}>'.format(self.value)


    def get_ancestors(self):
        if issubclass(self.attribute_type.field_type.model_class(), TreebeardNode):
            queryset = self.attribute_type.field_type.model_class().objects
            current_obj = queryset.get(**{f"{self.attribute_type.nested_field_name}": self.value})
            ancestors = [getattr(current_obj, self.attribute_type.nested_field_name)] + \
                        list(current_obj.get_ancestors().values_list(self.attribute_type.nested_field_name, flat=True))

            return ancestors
        else:
            queryset = self.attribute_type.field_type.model_class().objects
            current_obj = queryset.get(**{f"{self.attribute_type.nested_field_name}": self.value})
            ancestors_list = []
            while current_obj:
                ancestors_list.append(getattr(current_obj, self.attribute_type.nested_field_name))
                current_obj = current_obj.parent

            return ancestors_list

    def add_to_policy(self, policy):
        """
        TODO: Comment
        """
        PolicyNestedCategoricalFilter.objects.get_or_create(
            policy=policy,
            value=self
        )

    def is_in_policy_scope(self, policy):
        matching_policy_values = PolicyNestedCategoricalFilter.objects.filter(
                policy_id=policy.id,
                value_id__in=Subquery(
                    NestedCategoricalFilter.objects.filter(
                        attribute_type_id=self.attribute_type.id,
                        value__in=self.get_ancestors()
                    ).values('id')
                )
            )

        return matching_policy_values.exists()
