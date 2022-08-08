from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ModelBaseAttribute(models.Model):
    attribute_type = models.ForeignKey(
        'flex_abac.BaseAttribute',
        on_delete=models.CASCADE,
        unique=True
    )

    owner_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True
    )
    owner_object_id = models.PositiveIntegerField(null=True)
    owner_content_object = GenericForeignKey(
        'owner_content_type',
        'owner_object_id'
    )


    def __str(self):
        return '<{} % {}:{}>'.format(
            self.attribute_type,
            self.owner_content_type,
            self.owner_object_id
        )

    class Meta:
        abstract = True
        unique_together = ('attribute_type', 'owner_content_type',)
