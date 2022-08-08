import factory
from ..models import MaterializedNestedCategoricalFilter


class MaterializedNestedCategoricalFilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaterializedNestedCategoricalFilter