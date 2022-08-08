import factory
from ..models import Policy

class PolicyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Policy
        django_get_or_create = ('name',)