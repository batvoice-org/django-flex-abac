from django.db import models
from .model_base_attribute import ModelBaseAttribute


class ModelNestedCategoricalAttribute(ModelBaseAttribute):
    attribute_type = models.ForeignKey(
        'flex_abac.NestedCategoricalAttribute',
        on_delete=models.CASCADE
    )
