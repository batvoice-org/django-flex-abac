import factory
from .userfactory import UserFactory
from .rolefactory import RoleFactory
from ..models import UserRole

class UserRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserRole

    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)