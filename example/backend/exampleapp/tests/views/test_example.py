# from ..build_category_tree import build_category_tree
from exampleapp.models import (
    Brand, Document, Documenttopics, Desk, Topic, Region, Category, Documentregions
)
# from datetime import timedelta
from flex_abac.factories.actionfactory import ActionFactory
from flex_abac.factories.policyactionfactory import PolicyActionFactory
from flex_abac.factories.rolefactory import RoleFactory
from flex_abac.factories.policyfactory import PolicyFactory
from flex_abac.factories.userrolefactory import UserRoleFactory
from flex_abac.factories.rolepolicyfactory import RolePolicyFactory
from django.contrib.contenttypes.models import ContentType
from flex_abac.models import UserRole, Policy, \
    Action, PolicyAction, GenericFilter, GenericAttribute, \
    NestedCategoricalAttribute, MaterializedNestedCategoricalAttribute, \
    NestedCategoricalFilter, MaterializedNestedCategoricalFilter, \
    PolicyGenericFilter, ModelGenericAttribute, \
    PolicyNestedCategoricalFilter, PolicyMaterializedNestedCategoricalFilter,\
    ModelNestedCategoricalAttribute, ModelMaterializedNestedCategoricalAttribute, \
    ItemMaterializedNestedCategoricalFilter

# from ..build_category_tree import build_category_tree

import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework import serializers



class PermissionViewsTestCase(TestCase):
    fixtures = ['exampleapp']

    def setUp(self):
        # Retrieving users
        self.user_default = User.objects.get(id=1)

        self.django_client = APIClient(enforce_csrf_checks=False)

        # Token creation
        self.django_client.force_authenticate(user=self.user_default)

        # Permissions creation

        # Creation of user, role, policy
        self.role_default = RoleFactory.create(name="role default")
        UserRoleFactory.create(user=self.user_default, role=self.role_default)
        self.policy_default = PolicyFactory.create(name="policy default")
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default)

        # Adding list and detail actions
        PolicyActionFactory.create(policy=self.policy_default, action=ActionFactory.create(name="document__read"))
        # PolicyActionFactory.create(policy=self.policy_default, action=ActionFactory.create(name="document__read"))

        self.document_content_type = ContentType.objects.get_for_model(Document)

        # Attribute creation
        document_id_attribute = GenericAttribute.objects.create(name="Id", field_name="id")
        ModelGenericAttribute.objects.create(attribute_type=document_id_attribute, owner_content_object=self.document_content_type)

        for value in range(1, 6):
            PolicyGenericFilter.objects.create(
                policy=self.policy_default,
                value=GenericFilter.objects.create(value=value, attribute_type=document_id_attribute)
            )


    def test_document_ids(self):
        # Check permissions for document detail and generic list (positive)
        for value in range(1, 6):
            user_detail = self.django_client.get(reverse("exampleapp:simple-example-detail", args=(value,)))
            self.assertEqual(user_detail.status_code, 200, f"You should have permissions to do that.")

        user_list = self.django_client.get(reverse("exampleapp:simple-example-list"))
        self.assertEqual(user_list.status_code, 200, f"You should have permissions to do that.")

        # Check permissions for document detail and generic list (negative)
        for value in range(6, 7):
            user_detail = self.django_client.get(reverse("exampleapp:simple-example-detail", args=(value,)))
            self.assertEqual(user_detail.status_code, 403, f"You shouldn't have permissions to do that")

        PolicyAction.objects.filter(action__name="document__read").delete()

        user_list = self.django_client.get(reverse("exampleapp:simple-example-filter"))
        self.assertEqual(user_list.status_code, 403, f"You shouldn't have permissions to do that")


    def test_filtering_params(self):
        # Additional atributes and values
        # Adding additional actions
        PolicyActionFactory.create(policy=self.policy_default, action=ActionFactory.create(name="document__filter"))

        # Brand name
        brand_name_attribute = GenericAttribute.objects.create(name="brand name", field_name="brand__name")
        ModelGenericAttribute.objects.create(attribute_type=brand_name_attribute, owner_content_object=self.document_content_type)
        PolicyGenericFilter.objects.create(
            policy=self.policy_default,
            value=GenericFilter.objects.create(value=Brand.objects.get(id=1).name, attribute_type=brand_name_attribute)
        )
        PolicyGenericFilter.objects.create(
            policy=self.policy_default,
            value=GenericFilter.objects.create(value=Brand.objects.get(id=2).name, attribute_type=brand_name_attribute)
        )

        # Desk name
        desk_name_attribute = GenericAttribute.objects.create(name="desk name", field_name="desk__name")
        ModelGenericAttribute.objects.create(attribute_type=desk_name_attribute, owner_content_object=self.document_content_type)
        PolicyGenericFilter.objects.create(
            policy=self.policy_default,
            value=GenericFilter.objects.create(value=Desk.objects.get(id=2).name, attribute_type=desk_name_attribute)
        )

        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-filter"),
                                                data={"brand": ("Brand1", "Brand2"), "desk": "Desk2", "id": 1})

        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-filter"),
                                                data={"brand": ("Brand1dgda", "Brand2sdgsdgds"), "desk": "Desk2sdsdgs", "id": 10})
        self.assertEqual(documents_filtered.status_code, 403, f"You shouldn't have permissions to do that")

    def test_filtering(self):
        # Tests filtering
        documents_filtered = self.django_client.get(reverse("exampleapp:retrieve-all-list"), format="json")
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")
        self.assertEqual(len(documents_filtered.data), 5, f"Invalid number of retrieved values")

        documents_filtered = self.django_client.get(reverse("exampleapp:retrieve-all-list"), data={
                                                    "id": (1,2),
                                                }, format="json")
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")
        self.assertEqual(len(documents_filtered.data), 2, f"Invalid number of retrieved values")

    def test_action_name(self):
        # Tests action naming

        # Static
        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-checker-static-name"))
        self.assertEqual(documents_filtered.status_code, 403, f"You shouldn't have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default, action=ActionFactory.create(name="action_name_static"))
        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-checker-static-name"))
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

        # Custom generator
        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-checker-custom-generated-name"))
        self.assertEqual(documents_filtered.status_code, 403, f"You shouldn't have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default, action=ActionFactory.create(name="custom_name_generator"))
        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-checker-custom-generated-name"))
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

        # Method and http type generator
        PolicyActionFactory.create(policy=self.policy_default,
                                   action=ActionFactory.create(name="document__checker_method_and_type__get"))

        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-checker-method-and-type"))
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

        documents_filtered = self.django_client.post(reverse("exampleapp:complex-example-checker-method-and-type"))
        self.assertEqual(documents_filtered.status_code, 403, f"You shouldn't have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default,
                                   action=ActionFactory.create(name="checker_method_and_type_post"))

        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-checker-method-and-type"))
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

    def test_indirect_permissions(self):
        # Check that permissions are applied to the proper objects, even if not in the queryset
        PolicyActionFactory.create(policy=self.policy_default, action=ActionFactory.create(name="evaluation__read"))
        # PolicyActionFactory.create(policy=self.policy_default, action=ActionFactory.create(name="evaluation__filter2"))

        user_list = self.django_client.get(reverse("exampleapp:indirect-permissions-filter"))
        self.assertNotEqual(user_list.status_code, 403, f"You should have permissions to do that")

        documents_filtered = self.django_client.get(reverse("exampleapp:indirect-permissions-filter"),
                                                data={"brand": ("Brand1", "Brand2"), "desk": "Desk2", "id": 1})

        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

        documents_filtered = self.django_client.get(reverse("exampleapp:indirect-permissions-filter"),
                                                data={"brand": ("Brand1dgda", "Brand2sdgsdgds"), "desk": "Desk2sdsdgs", "id": 10})
        self.assertEqual(documents_filtered.status_code, 403, f"You shouldn't have permissions to do that")

        documents_filtered = self.django_client.get(reverse("exampleapp:indirect-permissions-filter2"),
                                                data={"brand": ("Brand1", "Brand2"), "desk": "Desk2", "id": 1}, format="json")

        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")
        self.assertEqual(len(documents_filtered.data), 5, f"Invalid number of retrieved values")

    def test_view_as_function(self):
        document_filtered = self.django_client.get(reverse("exampleapp:example_detail_as_function", args=(1,)))
        self.assertEqual(document_filtered.status_code, 403, f"You shouldn't have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default,
                                   action=ActionFactory.create(name="example_detail_as_function"))

        document_filtered = self.django_client.get(reverse("exampleapp:example_detail_as_function", args=(1,)))
        self.assertEqual(document_filtered.status_code, 200, f"You should have permissions to do that")

        document_filtered = self.django_client.get(reverse("exampleapp:example_detail_as_function", args=(10,)))
        self.assertEqual(document_filtered.status_code, 403, f"You should have permissions to do that")

        documents_filtered = self.django_client.get(reverse("exampleapp:example_view_as_function_simple"))
        self.assertEqual(documents_filtered.status_code, 403, f"You should have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default, action=ActionFactory.create(name="example_view_as_function_simple"))

        documents_filtered = self.django_client.get(reverse("exampleapp:example_view_as_function_simple"))
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

        documents_filtered = self.django_client.get(reverse("exampleapp:example_view_as_function"))
        self.assertEqual(documents_filtered.status_code, 403, f"You should have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default,
                                   action=ActionFactory.create(name="example_view_as_function"))

        documents_filtered = self.django_client.get(reverse("exampleapp:example_view_as_function"),
                                                data={"brand": ("Brand1", "Brand2"),
                                                      "desk": ("Desk1", "Desk2"),
                                                      "id": (1, 2, 3, 4, 5)}
                                                )
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")
        self.assertEqual(len(documents_filtered.data), 4, f"Invalid number of retrieved values")

        documents_filtered = self.django_client.get(reverse("exampleapp:example_view_as_function"),
                                                data={"brand": ("Brand1dgda", "Brand2sdgsdgds"),
                                                      "desk": "Desk2sdsdgs", "id": 10})
        self.assertEqual(documents_filtered.status_code, 403, f"You should have permissions to do that")

    def test_api_view(self):
        document_filtered = self.django_client.get(reverse("exampleapp:example_api_view_detail", args=(1,)))
        self.assertEqual(document_filtered.status_code, 403, f"You shouldn't have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default,
                                   action=ActionFactory.create(name="example_api_view_detail"))

        document_filtered = self.django_client.get(reverse("exampleapp:example_api_view_detail", args=(1,)))
        self.assertEqual(document_filtered.status_code, 200, f"You should have permissions to do that")

        document_filtered = self.django_client.get(reverse("exampleapp:example_api_view_detail", args=(10,)))
        self.assertEqual(document_filtered.status_code, 403, f"You should have permissions to do that")


        self.assertRaises(AttributeError, self.django_client.get, reverse("exampleapp:example_api_view_simple"))

        documents_filtered = self.django_client.get(reverse("exampleapp:example_api_view_complex"))
        self.assertEqual(documents_filtered.status_code, 403, f"You shouldn't have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default,
                                   action=ActionFactory.create(name="exampleapiviewcomplex__get"))


        documents_filtered = self.django_client.get(reverse("exampleapp:example_api_view_complex"))
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default,
                                   action=ActionFactory.create(name="example_filtered"))

        documents_filtered = self.django_client.get(reverse("exampleapp:example_api_view_complex_filtered"),
                                                data={"brand": ("Brand1", "Brand2"),
                                                      "desk": ("Desk1", "Desk2"),
                                                      "id": (1, 2, 3, 4, 5)}
                                                )
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")
        self.assertEqual(len(documents_filtered.data), 4, f"Invalid number of retrieved values")

        documents_filtered = self.django_client.get(reverse("exampleapp:example_api_view_complex_filtered"),
                                                data={"brand": ("Brand1dgda", "Brand2sdgsdgds"),
                                                      "desk": "Desk2sdsdgs", "id": 10})
        self.assertEqual(documents_filtered.status_code, 403, f"You should have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default,
                                   action=ActionFactory.create(name="document__filter"))

        documents_filtered = self.django_client.get(reverse("exampleapp:mapping-example1-filter"),
                                                data={"brand__name": ("Brand1", "Brand2"),
                                                      "desk__name": ("Desk1", "Desk2"),
                                                      "id": (1, 2, 3, 4, 5)}
                                                )
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

        documents_filtered = self.django_client.get(reverse("exampleapp:mapping-example1-filter"),
                                                data={"brand__id": ("Brand1dgda", "Brand2sdgsdgds"),
                                                      "desk__id": "Desk2sdsdgs", "id": 10})
        self.assertEqual(documents_filtered.status_code, 403, f"You should have permissions to do that")

        documents_filtered = self.django_client.get(reverse("exampleapp:mapping-example2-filter"),
                                                data={"brand__name": ("Brand1", "Brand2"),
                                                      "desk__name": ("Desk1", "Desk2"),
                                                      "id": (1, 2, 3, 4, 5)}
                                                )
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")

        documents_filtered = self.django_client.get(reverse("exampleapp:mapping-example2-filter"),
                                                data={"brand__id": ("Brand1dgda", "Brand2sdgsdgds"),
                                                      "desk__id": "Desk2sdsdgs", "id": 10})
        self.assertEqual(documents_filtered.status_code, 403, f"You should have permissions to do that")



class PermissionViewsNoScopeTestCase(TestCase):
    fixtures = ['exampleapp']

    def setUp(self):
        # Retrieving users
        self.user_default = User.objects.get(id=1)

        self.django_client = APIClient(enforce_csrf_checks=False)

        # Token creation
        self.django_client.force_authenticate(user=self.user_default)

        # Permissions creation

        # Creation of user, role, policy
        self.role_default = RoleFactory.create(name="role default")
        UserRoleFactory.create(user=self.user_default, role=self.role_default)
        self.policy_default = PolicyFactory.create(name="policy default")
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default)

    def test_can_access_no_scope(self):
        # Tests actions can be used without considering scope

        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-checker-no-scope"))
        self.assertEqual(documents_filtered.status_code, 403, f"You shouldn't have permissions to do that")

        PolicyActionFactory.create(policy=self.policy_default,
                                   action=ActionFactory.create(name="document__read"))

        documents_filtered = self.django_client.get(reverse("exampleapp:complex-example-checker-no-scope"))
        self.assertEqual(documents_filtered.status_code, 200, f"You should have permissions to do that")