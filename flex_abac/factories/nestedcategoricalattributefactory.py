import factory
from ..models import NestedCategoricalAttribute, ModelNestedCategoricalAttribute

from django.contrib.contenttypes.models import ContentType

class CategoricalAttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NestedCategoricalAttribute


class ModelCategoricalAttributeFactory(factory.django.DjangoModelFactory):
    owner_content_object = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object))
    attribute_type = factory.SubFactory(CategoricalAttributeFactory)

    class Meta:
        model = ModelNestedCategoricalAttribute

    class Params:
        content_object = None