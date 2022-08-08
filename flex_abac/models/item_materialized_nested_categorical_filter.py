from django.db import models
from .item_base_filter import ItemBaseFilter


class ItemMaterializedNestedCategoricalFilter(ItemBaseFilter):
    value = models.ForeignKey(
        'flex_abac.MaterializedNestedCategoricalFilter',
        on_delete=models.CASCADE
    )

























