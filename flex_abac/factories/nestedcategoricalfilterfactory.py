import factory
from ..models import NestedCategoricalFilter


class NestedCategoricalFilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NestedCategoricalFilter