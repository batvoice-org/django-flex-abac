from django.db import models


class RolePolicy(models.Model):
    role = models.ForeignKey(
        'flex_abac.Role',
        on_delete=models.CASCADE,
    )
    policy = models.ForeignKey(
        'flex_abac.Policy',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '<Role: {} % Policy: {}>'.format(
            self.role.name,
            self.policy.name
        )

    class Meta:
        unique_together = ('role','policy',)