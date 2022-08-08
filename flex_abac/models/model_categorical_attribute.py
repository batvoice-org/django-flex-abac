from django.db import models
from .model_base_attribute import ModelBaseAttribute


class ModelCategoricalAttribute(ModelBaseAttribute):
    attribute_type = models.ForeignKey(
        'flex_abac.CategoricalAttribute',
        on_delete=models.CASCADE
    )
