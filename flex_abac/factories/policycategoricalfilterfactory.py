import factory
from .policyfactory import PolicyFactory
from .categoricalfilterfactory import CategoricalFilterFactory
from flex_abac.models import PolicyCategoricalFilter


class PolicyCategoricalFilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PolicyCategoricalFilter
        django_get_or_create = ('policy', 'value',)

    value = factory.SubFactory(CategoricalFilterFactory)
    policy = factory.SubFactory(PolicyFactory)