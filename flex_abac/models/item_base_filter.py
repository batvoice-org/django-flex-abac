from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ItemBaseFilter(models.Model):
    value = models.ForeignKey(
        'flex_abac.BaseFilter',
        on_delete=models.CASCADE
    )
    # the owner is the object **instance** to which this attribute belongs
    # e.g. a document, a call, an article, etc.
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

    class Meta:
        abstract = True

    def __str(self):
        return '<{} % {}:{}>'.format(
            self.value,
            self.owner_content_type,
            self.owner_object_id
        )