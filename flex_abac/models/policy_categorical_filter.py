from django.db import models
from .policy_filter import PolicyFilter


class PolicyCategoricalFilter(PolicyFilter):
    value = models.ForeignKey(
        'flex_abac.CategoricalFilter',
        on_delete=models.CASCADE,
    )