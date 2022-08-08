import factory
from ..models import GenericFilter


class GenericFilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GenericFilter