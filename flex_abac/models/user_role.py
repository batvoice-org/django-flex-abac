from django.db import models

from flex_abac.models import Role
from flex_abac.constants import SUPERADMIN_ROLE

class UserRole(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True
    )
    role = models.ForeignKey(
        'flex_abac.Role',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '<User: {} % Role: {}>'.format(
            self.user,
            self.role.name
        )

    class Meta:
        unique_together = ('user', 'role',)

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if instance.is_superuser:
        if Role.objects.filter(name=SUPERADMIN_ROLE).exists():
            Role.objects.get(name=SUPERADMIN_ROLE).users.add(instance)
