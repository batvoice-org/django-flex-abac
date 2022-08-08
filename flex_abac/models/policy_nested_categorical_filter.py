from django.db import models
from .policy_filter import PolicyFilter


class PolicyNestedCategoricalFilter(PolicyFilter):
    value = models.ForeignKey(
        'flex_abac.NestedCategoricalFilter',
        on_delete=models.CASCADE,
    )

























