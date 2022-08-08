from django.db import models

from polymorphic.models import PolymorphicModel

class BaseFilter(PolymorphicModel):
    name = models.CharField(max_length=100, blank=True)

    @classmethod
    def print_all(cls):
        raise NotImplementedError

    def is_in_policy_scope(self, policy):
        """
        Indicates whether the attribute value matches the policy's scope
        """
        raise NotImplementedError

    def add_to_policy(self, policy):
        """
        TODO: Comment
        """
        raise NotImplementedError