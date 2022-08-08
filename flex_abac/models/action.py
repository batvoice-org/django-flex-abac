from django.db import models


class Action(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    pretty_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    policies = models.ManyToManyField(
        'flex_abac.Policy',
        through='flex_abac.PolicyAction'
    )

    models = models.ManyToManyField(
        'contenttypes.ContentType',
        through='flex_abac.ActionModel'
    )

    def save(self, *args, **kwargs):
        if not self.pretty_name:
            self.pretty_name = self.name
        super(Action, self).save(*args, **kwargs)

    def __str__(self):
        return '<Action: {}>'.format(self.name)
