from django.db import models
from .policy_filter import PolicyFilter


class PolicyMaterializedNestedCategoricalFilter(PolicyFilter):
    value = models.ForeignKey(
        'flex_abac.MaterializedNestedCategoricalFilter',
        on_delete=models.CASCADE,
    )

























