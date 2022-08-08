import factory
from .policyfactory import PolicyFactory
from .genericfilterfactory import GenericFilterFactory
from flex_abac.models import PolicyGenericFilter


class PolicyCategoricalFilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PolicyGenericFilter

    value = factory.SubFactory(GenericFilterFactory)
    policy = factory.SubFactory(PolicyFactory)