from django.db import models

class PolicyAction(models.Model):
    policy = models.ForeignKey(
        'flex_abac.Policy',
        on_delete=models.CASCADE,
    )
    action = models.ForeignKey(
        'flex_abac.Action',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '< {} % {} >'.format(
            self.policy,
            self.action
        )

    class Meta:
        unique_together = ('policy', 'action')