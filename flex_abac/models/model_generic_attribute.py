from django.db import models
from .model_base_attribute import ModelBaseAttribute


class ModelGenericAttribute(ModelBaseAttribute):
    attribute_type = models.ForeignKey(
        'flex_abac.GenericAttribute',
        on_delete=models.CASCADE
    )
