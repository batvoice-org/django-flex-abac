import factory
from flex_abac.models import Action


class ActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Action
        django_get_or_create = ('name',)

    name = "view"