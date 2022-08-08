import factory
from ..models import GenericAttribute, ModelGenericAttribute

from django.contrib.contenttypes.models import ContentType

class CategoricalAttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GenericAttribute


class ModelCategoricalAttributeFactory(factory.django.DjangoModelFactory):
    owner_content_object = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object))
    attribute_type = factory.SubFactory(CategoricalAttributeFactory)

    class Meta:
        model = ModelGenericAttribute

    class Params:
        content_object = None