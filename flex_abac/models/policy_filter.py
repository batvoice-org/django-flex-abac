from django.db import models


class PolicyFilter(models.Model):
    policy = models.ForeignKey(
        'flex_abac.Policy',
        on_delete=models.CASCADE,
    )
    value = models.ForeignKey(
        'flex_abac.BaseFilter',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '< PolicyFilter {} % {} >'.format(
            self.policy,
            self.value
        )

    class Meta:
        unique_together = ('value', 'policy',)
        abstract = True