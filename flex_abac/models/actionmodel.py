from django.db import models
from django.contrib.contenttypes.models import ContentType

class ActionModel(models.Model):
    action = models.ForeignKey(
        'flex_abac.Action',
        on_delete=models.CASCADE,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return '<Action: {} % Model: {}.{}>'.format(
            self.action.pretty_name,
            self.content_type.app_label,
            self.content_type.model,
        )

    class Meta:
        unique_together = ('action', 'content_type', )

