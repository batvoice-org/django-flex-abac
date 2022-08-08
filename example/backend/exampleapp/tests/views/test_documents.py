from flex_abac.factories.rolefactory import RoleFactory
from flex_abac.factories.policyfactory import PolicyFactory

from flex_abac.utils.load_flex_abac_data import load_flex_abac_data

from django.conf import settings

from flex_abac.models import UserRole, Policy, \
    Action, Role, PolicyAction, GenericFilter, GenericAttribute, \
    NestedCategoricalAttribute, MaterializedNestedCategoricalAttribute, \
    NestedCategoricalFilter, MaterializedNestedCategoricalFilter, \
    PolicyGenericFilter, ModelGenericAttribute, \
    PolicyCategoricalFilter, CategoricalFilter, \
    PolicyNestedCategoricalFilter, PolicyMaterializedNestedCategoricalFilter,\
    ModelNestedCategoricalAttribute, ModelMaterializedNestedCategoricalAttribute, \
    ItemMaterializedNestedCategoricalFilter

import os

from flex_abac.utils.import_attributes import import_from_yaml

from django.apps import apps

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APIClient



class PermissionViewsTestCase(TestCase):
    fixtures = ['exampleapp']

    def setUp(self):
        # Creating users
        self.user_admin = User.objects.create_user(username="administration")
        self.user_desk_odd = User.objects.create_user(username="desk_odd")
        self.user_desk_even = User.objects.create_user(username="desk_even")
        self.user_brand3 = User.objects.create_user(username="brand3")
        self.user_just_view = User.objects.create_user(username="just_view")

        self.django_client_admin = APIClient(enforce_csrf_checks=False)
        self.django_client_admin.force_authenticate(user=self.user_admin)
        self.django_client_desk_odd = APIClient(enforce_csrf_checks=False)
        self.django_client_desk_odd.force_authenticate(user=self.user_desk_odd)
        self.django_client_desk_even = APIClient(enforce_csrf_checks=False)
        self.django_client_desk_even.force_authenticate(user=self.user_desk_even)
        self.django_client_brand3 = APIClient(enforce_csrf_checks=False)
        self.django_client_brand3.force_authenticate(user=self.user_brand3)
        self.django_client_just_view = APIClient(enforce_csrf_checks=False)
        self.django_client_just_view.force_authenticate(user=self.user_just_view)

        # Creation of roles
        self.role_admin = RoleFactory.create(name="role administration")
        self.role_desk_odd = RoleFactory.create(name="role desk_odd")
        self.role_desk_even = RoleFactory.create(name="role desk_even")
        self.role_brand3 = RoleFactory.create(name="role brand3")
        self.role_just_view = RoleFactory.create(name="role just_view")

        self.role_admin.users.add(self.user_admin)
        self.role_desk_odd.users.add(self.user_desk_odd)
        self.role_desk_even.users.add(self.user_desk_even)
        self.role_brand3.users.add(self.user_brand3)
        self.role_just_view.users.add(self.user_just_view)

        # Creation of policies
        self.policy_admin = PolicyFactory.create(name="policy administration")
        self.policy_desk_odd = PolicyFactory.create(name="policy desk_odd")
        self.policy_desk_even = PolicyFactory.create(name="policy desk_even")
        self.policy_brand3 = PolicyFactory.create(name="policy brand3")
        self.policy_just_view = PolicyFactory.create(name="policy just_view")

        self.role_admin.policies.add(self.policy_admin)
        self.role_desk_odd.policies.add(self.policy_desk_odd)
        self.role_desk_even.policies.add(self.policy_desk_even)
        self.role_brand3.policies.add(self.policy_brand3)
        self.role_just_view.policies.add(self.policy_just_view)

        # Adding actions
        methods = {}
        # for action_name in ["create", "update", "partial_update", "destroy", "list", "retrieve"]:
        for method_name in ["read", "write"]:
            methods[method_name] = Action.objects.create(name=f"document__{method_name}",
                                                         pretty_name=f"Allows the HTTP {method_name} method for a "
                                                                     f"document-related endpoint")

        for method_name in ["read", "write"]:
            self.policy_admin.actions.add(methods[method_name])
            self.policy_desk_odd.actions.add(methods[method_name])
            self.policy_desk_even.actions.add(methods[method_name])
            self.policy_brand3.actions.add(methods[method_name])

        for method_name in ["read"]:
            self.policy_just_view.actions.add(methods[method_name])

        # self.policy_desk_odd.actions.add(Action.objects.create(name=f"document__get_all_allowed_values",
        #                                                     pretty_name=f"Allows getting all allowed values from an endpoint"))

        import_from_yaml(os.path.join(apps.get_app_config('exampleapp').path, "tests/data/attributes.yaml"))

        filters_desk = CategoricalFilter.objects.filter(attribute_type__name="Desk")
        filters_brand = CategoricalFilter.objects.filter(attribute_type__name="Brand")

        PolicyCategoricalFilter.objects.create(policy=self.policy_desk_odd, value=filters_desk.get(value=1))
        PolicyCategoricalFilter.objects.create(policy=self.policy_desk_odd, value=filters_desk.get(value=3))
        PolicyCategoricalFilter.objects.create(policy=self.policy_desk_even, value=filters_desk.get(value=2))
        PolicyCategoricalFilter.objects.create(policy=self.policy_brand3, value=filters_brand.get(value=3))

    def test_documents_list(self):
        response = self.django_client_admin.get(reverse(f"exampleapp:documents-list"))
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_odd.get(reverse(f"exampleapp:documents-list"))
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_even.get(reverse(f"exampleapp:documents-list"))
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_brand3.get(reverse(f"exampleapp:documents-list"))
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_just_view.get(reverse(f"exampleapp:documents-list"))
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

    def test_documents_filter(self):
        response = self.django_client_admin.get(reverse(f"exampleapp:documents-list"),
                                                data={
                                                    "brand__id": (1, 2),
                                                    "desk__id": 2,
                                                    "id_max": 7
                                                })
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_odd.get(reverse(f"exampleapp:documents-list"),
                                                data={
                                                    "brand__id": (1, 2),
                                                    "desk__id": 2,
                                                    "id_max": 7
                                                })
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

        response = self.django_client_desk_even.get(reverse(f"exampleapp:documents-list"),
                                                data={
                                                    "brand__id": (1, 2),
                                                    "desk__id": 2,
                                                    "id_max": 7
                                                })
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_brand3.get(reverse(f"exampleapp:documents-list"),
                                                data={
                                                    "brand__id": (1, 2),
                                                    "desk__id": 2,
                                                    "id_max": 7
                                                })
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

        response = self.django_client_just_view.get(reverse(f"exampleapp:documents-list"),
                                                data={
                                                    "brand__id": (1, 2),
                                                    "desk__id": 2,
                                                    "id_max": 7
                                                })
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")


    def test_documents_retrieve(self):
        response = self.django_client_admin.get(reverse(f"exampleapp:documents-detail", args=(1,)))
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_odd.get(reverse(f"exampleapp:documents-detail", args=(1,)))
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_even.get(reverse(f"exampleapp:documents-detail", args=(1,)))
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

        response = self.django_client_brand3.get(reverse(f"exampleapp:documents-detail", args=(1,)))
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

        response = self.django_client_just_view.get(reverse(f"exampleapp:documents-detail", args=(1,)))
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

    def test_documents_create(self):
        response = self.django_client_admin.post(reverse(f"exampleapp:documents-list"), {
            "filename": "admin_filename",
            "desk": { "name": "admin_desk" },
            "brand": { "name": "admin_brand" }
        }, format="json")
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_odd.post(reverse(f"exampleapp:documents-list"), {
            "filename": "desk_odd_filename",
            "desk": { "name": "desk_odd_desk" },
            "brand": { "name": "desk_odd_brand" }
        }, format="json")
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_even.post(reverse(f"exampleapp:documents-list"), {
            "filename": "desk_even_filename",
            "desk": { "name": "desk_even_desk" },
            "brand": { "name": "desk_even_brand" }
        }, format="json")
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_brand3.post(reverse(f"exampleapp:documents-list"), {
            "filename": "brand3_filename",
            "desk": { "name": "brand3_desk" },
            "brand": { "name": "brand3_brand" }
        }, format="json")
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_just_view.post(reverse(f"exampleapp:documents-list"), {
            "filename": "just_view_filename",
            "desk": { "name": "just_view_desk" },
            "brand": { "name": "just_view_brand" }
        }, format="json")
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")


    def test_documents_update(self):
        response = self.django_client_admin.put(reverse(f"exampleapp:documents-detail", args=(1,)), {
            "filename": "filename_new",
            "desk": { "name": "desk_new" },
            "brand": { "name": "brand_new" }
        }, format="json")
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_odd.put(reverse(f"exampleapp:documents-detail", args=(1,)), {
            "filename": "filename_new",
            "desk": { "name": "desk_new" },
            "brand": { "name": "brand_new" }
        }, format="json")
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_even.put(reverse(f"exampleapp:documents-detail", args=(1,)), {
            "filename": "filename_new",
            "desk": { "name": "desk_new" },
            "brand": { "name": "brand_new" }
        }, format="json")
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

        response = self.django_client_brand3.put(reverse(f"exampleapp:documents-detail", args=(1,)), {
            "filename": "filename_new",
            "desk": { "name": "desk_new" },
            "brand": { "name": "brand_new" }
        }, format="json")
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

        response = self.django_client_just_view.put(reverse(f"exampleapp:documents-detail", args=(1,)), {
            "filename": "filename_new",
            "desk": { "name": "desk_new" },
            "brand": { "name": "brand_new" }
        }, format="json")
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

    def test_user_switch(self):
        response = self.django_client_admin.get(reverse(f"exampleapp:documents-list"),
                                                data={
                                                    "as_user": self.user_brand3
                                                })
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        response = self.django_client_desk_odd.get(reverse(f"exampleapp:documents-list"),
                                                data={
                                                    "brand__id": (1, 2),
                                                    "desk__id": 2,
                                                    "id_max": 7
                                                })
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

        response = self.django_client_desk_odd.get(reverse(f"exampleapp:documents-list"),
                                                   data={
                                                       "brand": (1, 2),
                                                       "desk": 2,
                                                       "id_max": 7,
                                                       "as_user": self.user_admin.username
                                                   })
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

    def test_get_all_allowed_values(self):
        if getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False):
            load_flex_abac_data()

            flex_abac_admin_role = Role.objects.get(name="flex-abac Admin Role")

            flex_abac_admin_role.users.add(self.user_admin)
            flex_abac_admin_role.users.add(self.user_desk_odd)
            flex_abac_admin_role.users.add(self.user_desk_even)
            flex_abac_admin_role.users.add(self.user_brand3)
            flex_abac_admin_role.users.add(self.user_just_view)

        response = self.django_client_desk_odd.get(reverse("exampleapp:documents-get-all-allowed-values", args=(1,)),
                                                data={ "as_user": self.user_desk_odd.username })
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        PolicyAction.objects.filter(action__name="document__read").delete()

        response = self.django_client_desk_odd.get(reverse("exampleapp:documents-get-all-allowed-values", args=(1,)),
                                                data={"as_user": self.user_brand3.username})
        self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

        response = self.django_client_desk_odd.get(reverse("exampleapp:exampleapp-get-all-allowed-values-per-user"),
                                                   data={"as_user": self.user_desk_odd.username,
                                                         "models": "exampleapp.document"})
        self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")
