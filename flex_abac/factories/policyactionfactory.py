import factory
from .policyfactory import PolicyFactory
from .actionfactory import ActionFactory
from flex_abac.models import PolicyAction


class PolicyActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PolicyAction

    action = factory.SubFactory(ActionFactory)
    policy = factory.SubFactory(PolicyFactory)