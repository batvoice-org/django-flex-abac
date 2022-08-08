from django.db import models
from .policy_filter import PolicyFilter


class PolicyGenericFilter(PolicyFilter):
    value = models.ForeignKey(
        'flex_abac.GenericFilter',
        on_delete=models.CASCADE,
    )