import factory
from ..models import CategoricalFilter


class CategoricalFilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoricalFilter