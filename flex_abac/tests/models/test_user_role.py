from django.test import TestCase
from flex_abac.factories.rolefactory import RoleFactory
from flex_abac.factories.userfactory import UserFactory
from flex_abac.factories.userrolefactory import UserRoleFactory
from django.contrib.auth.models import User
from flex_abac.models import Role, UserRole


class UserRoleTestCase(TestCase):
    def setUp(self):
        user = UserFactory.create(
            first_name='Ali',
            last_name='Baba',
            pk=1
        )

        role = RoleFactory.create(
            name='teamlead',
            pk=1
        )

        UserRoleFactory.create(
            user=user,
            role=role,
            pk=1
        )

    def test_userrole(self):
        user = User.objects.get(pk=1)
        self.assertEqual(user.first_name, 'Ali')
        role = Role.objects.get(pk=1)
        self.assertEqual(role.name, 'teamlead')
        user_role = UserRole.objects.get(
            user=user,
            role=role
        )
        self.assertEqual(user_role.role.pk, role.pk)


