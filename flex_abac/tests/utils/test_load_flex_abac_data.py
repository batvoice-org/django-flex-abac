from django.test import TestCase
from flex_abac.utils.load_flex_abac_data import load_flex_abac_data
from django.contrib.auth.models import User
from flex_abac.models import (
    UserRole, Role, Policy, PolicyAction,
    GenericAttribute, GenericFilter,
    NestedCategoricalAttribute, NestedCategoricalFilter,
    MaterializedNestedCategoricalAttribute, MaterializedNestedCategoricalFilter,
)

from flex_abac.constants import SUPERADMIN_ROLE

class LoadFlexAbacDataTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="test_superuser", is_superuser=True)

        self.admin_user_names = []
        self.viewer_user_names = []
        for idx in range(3):
            admin_user_name = f"test_admin_{idx}"
            viewer_user_name = f"test_viewer_{idx}"

            User.objects.create(username=admin_user_name)
            User.objects.create(username=viewer_user_name)

            self.admin_user_names.append(admin_user_name)
            self.viewer_user_names.append(viewer_user_name)


    def test_load_flex_abac_data_no_user_info(self):
        UserRole.objects.filter(user__username="test_superuser").delete()

        load_flex_abac_data()

        self.assertTrue(Role.objects.filter(name=SUPERADMIN_ROLE).exists(), "Error with roles creation!")
        self.assertTrue(Role.objects.filter(name="flex-abac Viewer Role").exists(), "Error with roles creation!")

        self.assertTrue(Policy.objects.filter(name="flex-abac Admin Policy").exists(), "Error with policies creation!")
        self.assertTrue(Policy.objects.filter(name="flex-abac Viewer Policy").exists(), "Error with policies creation!")

        self.assertTrue(PolicyAction.objects.filter(policy__name="flex-abac Admin Policy").exists(),
                        "There are no actions associated to admin policies!")
        self.assertTrue(PolicyAction.objects.filter(policy__name="flex-abac Viewer Policy").exists(),
                        "There are no actions associated to viewer policies!")

        # Check superusers were added
        self.assertTrue(UserRole.objects.filter(user__username="test_superuser").exists(),
                        "Superuser was not automatically added to roles!")

    def tests_superuser_signal_works(self):
        load_flex_abac_data()

        User.objects.create(username="test_superuser2", is_superuser=True)

        self.assertTrue(UserRole.objects.filter(user__username="test_superuser").exists(),
                        "Superuser was not automatically added to roles!")


    def test_load_flex_abac_data_adding_users(self):
        load_flex_abac_data(admin_users=self.admin_user_names, viewer_users=self.viewer_user_names)

        self.assertTrue(Role.objects.filter(name=SUPERADMIN_ROLE).exists(), "Error with roles creation!")
        self.assertTrue(Role.objects.filter(name="flex-abac Viewer Role").exists(), "Error with roles creation!")

        self.assertTrue(Policy.objects.filter(name="flex-abac Admin Policy").exists(), "Error with policies creation!")
        self.assertTrue(Policy.objects.filter(name="flex-abac Viewer Policy").exists(), "Error with policies creation!")

        self.assertTrue(PolicyAction.objects.filter(policy__name="flex-abac Admin Policy").exists(),
                        "There are no actions associated to admin policies!")
        self.assertTrue(PolicyAction.objects.filter(policy__name="flex-abac Viewer Policy").exists(),
                        "There are no actions associated to viewer policies!")

        self.assertEqual(UserRole.objects.filter(user__username__in=self.admin_user_names,
                                                 role__name=SUPERADMIN_ROLE).count(),
                         3, "Wrong number of admin users!")

        self.assertEqual(UserRole.objects.filter(user__username__in=self.viewer_user_names,
                                                 role__name="flex-abac Viewer Role").count(),
                         3, "Wrong number of viewer users!")

        # Checking the previous user clearing is working
        load_flex_abac_data(clean_users=True)

        self.assertEqual(UserRole.objects.filter(user__username__in=self.admin_user_names,
                                                 role__name=SUPERADMIN_ROLE).count(),
                         0, "Wrong number of admin users!")

        self.assertEqual(UserRole.objects.filter(user__username__in=self.viewer_user_names,
                                                 role__name="flex-abac Viewer Role").count(),
                         0, "Wrong number of viewer users!")


