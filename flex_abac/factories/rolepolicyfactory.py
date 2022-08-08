import factory
from .rolefactory import RoleFactory
from .policyfactory import PolicyFactory
from ..models import RolePolicy

class RolePolicyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RolePolicy

    role = factory.SubFactory(RoleFactory)
    policy = factory.SubFactory(PolicyFactory)
