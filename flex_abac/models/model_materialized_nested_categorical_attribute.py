from django.db import models
from .model_base_attribute import ModelBaseAttribute


class ModelMaterializedNestedCategoricalAttribute(ModelBaseAttribute):
    attribute_type = models.ForeignKey(
        'flex_abac.MaterializedNestedCategoricalAttribute',
        on_delete=models.CASCADE
    )
