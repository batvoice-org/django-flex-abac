from exampleapp.models import (
    Brand, Document, Documenttopics, Desk, Topic, Region, Category, Documentregions
)
from datetime import datetime, timedelta
from flex_abac.factories.actionfactory import ActionFactory
from flex_abac.factories.policyactionfactory import PolicyActionFactory
from flex_abac.factories.rolefactory import RoleFactory
from flex_abac.factories.policyfactory import PolicyFactory
from flex_abac.factories.userrolefactory import UserRoleFactory
from flex_abac.factories.rolepolicyfactory import RolePolicyFactory
from django.contrib.contenttypes.models import ContentType
from flex_abac.models import UserRole, Policy, Role, \
    Action, ActionModel, PolicyAction, \
    BaseAttribute, BaseFilter, \
    GenericFilter, GenericAttribute, \
    CategoricalAttribute, CategoricalFilter, ModelCategoricalAttribute, \
    NestedCategoricalAttribute, MaterializedNestedCategoricalAttribute, \
    NestedCategoricalFilter, MaterializedNestedCategoricalFilter, \
    PolicyFilter, PolicyGenericFilter, PolicyCategoricalFilter, ModelGenericAttribute, \
    PolicyNestedCategoricalFilter, PolicyMaterializedNestedCategoricalFilter,\
    ModelNestedCategoricalAttribute, ModelMaterializedNestedCategoricalAttribute, \
    ItemMaterializedNestedCategoricalFilter

from exampleapp.tests.utils.build_category_tree import build_category_tree

from django.conf import settings

import json
from pprint import pprint

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework import serializers
from flex_abac.utils.load_flex_abac_data import load_flex_abac_data

class DatetimeSerializer(serializers.Serializer):
    DATE_TIME_FORMAT = "%Y-%m-%d"

    value = serializers.SerializerMethodField()

    class Meta:
        fields = ['value']

    @classmethod
    def possible_values(cls, attribute_obj):
        return [{
            "value": (datetime.strptime("2021-09-03", DatetimeSerializer.DATE_TIME_FORMAT),
                      datetime.strptime("2021-09-04", DatetimeSerializer.DATE_TIME_FORMAT))
        }, {
            "value": (datetime.strptime("2021-09-04", DatetimeSerializer.DATE_TIME_FORMAT),
                      datetime.strptime("2021-09-05", DatetimeSerializer.DATE_TIME_FORMAT))
        }]

    def get_value(self, obj):
        return (
            obj[0].strftime(DatetimeSerializer.DATE_TIME_FORMAT),
            obj[1].strftime(DatetimeSerializer.DATE_TIME_FORMAT),
        )

    def create(self, validated_data):
        return {"value": (
                    datetime.strptime(validated_data["value"][0], DatetimeSerializer.DATE_TIME_FORMAT),
                    datetime.strptime(validated_data["value"][1], DatetimeSerializer.DATE_TIME_FORMAT)
                )}


class PermissionViewsTestCase(TestCase):
    fixtures = ['exampleapp']

    def setUp(self):
        load_flex_abac_data()

        # Retrieving users
        self.user_default = User.objects.get(id=1)
        self.user_admin = User.objects.get(id=2)

        flex_abac_admin_role = Role.objects.get(name=flex_abac.constants.SUPERADMIN_ROLE)
        flex_abac_admin_role.users.add(self.user_admin)
        flex_abac_admin_role.users.add(self.user_default)

        # Just creates the categories by using treebeard, since it is not possible to do so directly from fixtures
        build_category_tree()

        # We create several roles (In the end, collections of policies).
        self.role_default = RoleFactory.create(name="role default")
        self.role_default2 = RoleFactory.create(name="role default2")
        self.role_admin = RoleFactory.create(name="role admin")

        UserRoleFactory.create(user=self.user_default, role=self.role_default)
        UserRoleFactory.create(user=self.user_default, role=self.role_default2)
        UserRoleFactory.create(user=self.user_admin, role=self.role_admin)

        # We create several policies (In the end, collections of actions and the associated scopes)
        self.policy_default = PolicyFactory.create(name="policy default")
        self.policy_default11 = PolicyFactory.create(name="policy default1.1")
        self.policy_default12 = PolicyFactory.create(name="policy default1.2")
        self.policy_default21 = PolicyFactory.create(name="policy default2.1")
        self.policy_default22 = PolicyFactory.create(name="policy default2.2")
        self.policy_admin = PolicyFactory.create(name="policy admin")

        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default)
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default11)
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default12)
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default21)
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default22)
        RolePolicyFactory.create(role=self.role_admin, policy=self.policy_admin)

        # Content types
        document_content_type = ContentType.objects.get_for_model(Document)
        brand_content_type = ContentType.objects.get_for_model(Brand)
        desk_content_type = ContentType.objects.get_for_model(Desk)

        # Actions (defines which can be done by the user associated to a policy)
        self.action_view = ActionFactory.create(name="view", pretty_name="The user can view")
        self.action_edit = ActionFactory.create(name="edit", pretty_name="The user can edit")

        ActionModel.objects.create(action=self.action_view, content_type=document_content_type)
        ActionModel.objects.create(action=self.action_view, content_type=brand_content_type)
        ActionModel.objects.create(action=self.action_edit, content_type=desk_content_type)

        # Default policy can view; admin policy can view and edit
        PolicyActionFactory.create(policy=self.policy_default, action=self.action_view)
        PolicyActionFactory.create(policy=self.policy_admin, action=self.action_view)
        PolicyActionFactory.create(policy=self.policy_admin, action=self.action_edit)

        # Attributes. One per each class we will be using for checking (in our case, just the documents model)
        self.brand_attribute = CategoricalAttribute.objects.create(name="Brand name", field_name="brand__name")
        self.desk_attribute = GenericAttribute.objects.create(
            name="Desk name",
            field_name="desk__name",
        )
        self.desk_fk_attribute = CategoricalAttribute.objects.create(
            name="Desk id",
            field_name="desk",
            extra_fields={
                "desk__id": "id",
                "desk__name": "desk"
            }
        )
        self.datetime_attribute = GenericAttribute.objects.create(
            name="Document date",
            field_name="document_datetime__range",
            serializer="flex_abac.tests.views.test_permissionsview.DatetimeSerializer"
        )

        self.topic_attribute = NestedCategoricalAttribute.objects.create(name="Topic name",
                                                                         field_type=ContentType.objects.get_for_model(Topic),
                                                                         field_name="topics",
                                                                         nested_field_name="name",
                                                                         parent_field_name="parent",
                                                                         extra_fields={
                                                                             'id': 'id',
                                                                             'name': 'name',
                                                                         })

        #  For materialized trees maintained by user:
        self.category_attribute = NestedCategoricalAttribute.objects.create(name="Category name",
                                                                            field_type=ContentType.objects.get_for_model(Category),
                                                                            field_name="categories",
                                                                            nested_field_name="name",
                                                                            parent_field_name="parent",
                                                                            extra_fields={
                                                                                'id': 'id',
                                                                                'name': 'name',
                                                                            })

        # For materialized trees things are slightly different. First, we need to define the relation between different levels
        get_subtree_attr = lambda node_id: MaterializedNestedCategoricalAttribute.objects.get(pk=node_id)

        self.region_country_attribute = MaterializedNestedCategoricalAttribute.add_root(name='Country',
                                                                                        extra_fields={
                                                                                            'id': 'id',
                                                                                            'value': 'name',
                                                                                        })
        self.region_province_attribute = get_subtree_attr(self.region_country_attribute.pk).add_child(name='Province',
                                                                                                      extra_fields={
                                                                                                          'id': 'id',
                                                                                                          'value': 'name',
                                                                                                      })
        self.region_city_attribute = get_subtree_attr(self.region_province_attribute.pk).add_child(name='City',
                                                                                                   extra_fields={
                                                                                                       'id': 'id',
                                                                                                       'value': 'name',
                                                                                                   })

        self.attribute_region_levels = [self.region_country_attribute, self.region_province_attribute, self.region_city_attribute]

        # We need to register the new attribute so it can be found later by the checkers
        ModelCategoricalAttribute.objects.create(
            attribute_type=self.brand_attribute,  # The attribute type (brand__name field in this case)
            owner_content_object=document_content_type  # the content type for the Document model
        )
        ModelGenericAttribute.objects.create(
            attribute_type=self.desk_attribute,  # The attribute type (desk__name field in this case)
            owner_content_object=document_content_type  # the content type for the Document model
        )
        ModelCategoricalAttribute.objects.create(
            attribute_type=self.desk_fk_attribute,  # The attribute type (desk__name field in this case)
            owner_content_object=document_content_type  # the content type for the Document model
        )
        ModelGenericAttribute.objects.create(
            attribute_type=self.datetime_attribute,  # The attribute type (document_date field in this case)
            owner_content_object=document_content_type  # the content type for the Document model
        )
        ModelNestedCategoricalAttribute.objects.create(
            attribute_type=self.topic_attribute,  # The attribute type (topic field in this case)
            owner_content_object=document_content_type  # the content type for the Document model
        )
        ModelNestedCategoricalAttribute.objects.create(
            attribute_type=self.category_attribute,  # The attribute type (category field in this case)
            owner_content_object=document_content_type  # the content type for the Document model
        )
        for tree_level in self.attribute_region_levels:
            ModelMaterializedNestedCategoricalAttribute.objects.create(
                attribute_type=tree_level,  # The attribute type (tree_levl field in this case)
                owner_content_object=document_content_type  # the content type for the Document model
            )

        ##############################
        # Attribute values definition
        ##############################

        # Values for brands (one per each of the brands we want to store)
        # Since brands are categories without a hierarchy we are using generic values
        # Then, there will be as many items as documents with this brand
        self.brand_values = {}
        for brand in Brand.objects.all():
            self.brand_values[brand.id] = CategoricalFilter.objects.create(
                value=brand.name,
                attribute_type=self.brand_attribute,
            )

        # Values for desks (one per each of the desks we want to store)
        # Since desk are categories without a hierarchy we are using generic values
        # Then, there will be as many items as documents with this desk
        self.desk_values = {}
        self.desk_fk_values = {}
        for desk in Desk.objects.all():
            self.desk_values[desk.id] = GenericFilter.objects.create(
                value=desk.name,
                attribute_type=self.desk_attribute,
            )
            self.desk_fk_values[desk.id] = CategoricalFilter.objects.create(
                value=desk.pk,
                attribute_type=self.desk_fk_attribute,
            )

        # Values for document_datetime (one per each unique value on documents)
        # We are using generic values for this
        self.datetime_values = {}
        for idx, document_datetime in enumerate(Document.objects.values("document_datetime").order_by("document_datetime").distinct()):
            self.datetime_values[idx] = GenericFilter.objects.create(
                value=(document_datetime["document_datetime"], document_datetime["document_datetime"] + timedelta(days=2)),
                attribute_type=self.datetime_attribute,
            )

        # Values for topics (one per each of the topics in database)
        # We are using nested categorical values for this
        self.topic_values = {}
        for topic in Topic.objects.all():
            self.topic_values[topic.id] = NestedCategoricalFilter.objects.create(
                value=topic.id,
                attribute_type=self.topic_attribute,
            )

        # Values for categories (one per each of the categories in database)
        # We are using nested categorical values for this
        self.category_values = {}
        for category in Category.objects.all():
            self.category_values[category.name] = NestedCategoricalFilter.objects.create(
                value=category.id,
                attribute_type=self.category_attribute,
            )

        # Values for regions (one per each of the regions in database)
        # We are using materialized nested categorical values for this
        # First, we need to create the materialized tree on treebeard (which we will need to maintain when
        # an update occurs)
        self.add_values_for_regions()

        # We want default policy to have access to:
        # - brands (1,3)
        # - desk: 1
        # - datetime: 0 (2021-08-04, 2021-08-06)
        # - topics: (1.1 [2], 1.2.1 [6]) and descendants
        # - categories: (1.1 [2], 1.2.1 [6]) and descendants
        # - regions: (1.1 [2], 1.2.1 [6]) and descendants
        PolicyCategoricalFilter.objects.create(policy=self.policy_default, value=self.brand_values[1])
        PolicyCategoricalFilter.objects.create(policy=self.policy_default, value=self.brand_values[3])
        PolicyGenericFilter.objects.create(policy=self.policy_default, value=self.desk_values[1])
        PolicyGenericFilter.objects.create(policy=self.policy_default, value=self.datetime_values[0])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_default, value=self.topic_values[2])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_default, value=self.topic_values[6])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_default,
                                                    value=self.category_values["Category 1.1"])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_default,
                                                    value=self.category_values["Category 1.2.1"])
        PolicyMaterializedNestedCategoricalFilter.objects.create(policy=self.policy_default, value=self.region_values[2])
        PolicyMaterializedNestedCategoricalFilter.objects.create(policy=self.policy_default, value=self.region_values[6])

        # We want admin policy to have access to:
        # - brands (2,3)
        # - desks (2,3)
        # - datetime: 3 (2021-08-07 - 2021-08-09)
        # - topics: (1.2 [5], 2.2 [7]) and descendants
        # - categories(1.2 [5], 2.2 [7]) and descendants
        # - regions: (1.1.2 [5], 1.2.2 [7]) and descendants
        PolicyCategoricalFilter.objects.create(policy=self.policy_admin, value=self.brand_values[2])
        PolicyCategoricalFilter.objects.create(policy=self.policy_admin, value=self.brand_values[3])
        PolicyGenericFilter.objects.create(policy=self.policy_admin, value=self.desk_values[2])
        PolicyGenericFilter.objects.create(policy=self.policy_admin, value=self.desk_values[3])
        PolicyGenericFilter.objects.create(policy=self.policy_admin, value=self.datetime_values[3])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_admin, value=self.topic_values[5])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_admin, value=self.topic_values[7])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_admin,
                                                    value=self.category_values["Category 1.1.2"])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_admin,
                                                    value=self.category_values["Category 1.2.2"])
        PolicyMaterializedNestedCategoricalFilter.objects.create(policy=self.policy_admin, value=self.region_values[5])
        PolicyMaterializedNestedCategoricalFilter.objects.create(policy=self.policy_admin, value=self.region_values[7])

        self.django_client = APIClient(enforce_csrf_checks=False)

        # Token creation
        self.django_client.force_authenticate(user=self.user_default)

    def tearDown(self):
        return super().tearDown()

    def add_values_for_regions(self):
        """
        Constructs the list of values per region from the TreeBeard table (materialized)
        """

        get_subtree_val = lambda node_id: MaterializedNestedCategoricalFilter.objects.get(pk=node_id)

        self.region_values = {}
        last_level = Region.objects.filter(parent=None)
        depth = 0
        while last_level.exists():
            for region in last_level:
                if not region.parent:
                    self.region_values[region.pk] = MaterializedNestedCategoricalFilter.add_root(
                        value=region.name,
                        attribute_type=self.attribute_region_levels[depth]
                    )
                else:
                    self.region_values[region.pk] = get_subtree_val(self.region_values[region.parent.pk].pk).add_child(
                        value=region.name,
                        attribute_type=self.attribute_region_levels[depth]
                    )

                # Adding created values to the list of existing items
                related_documents = Documentregions.objects.filter(region=region.pk)
                for documentregion in related_documents:
                    ItemMaterializedNestedCategoricalFilter.objects.create(
                        value=self.region_values[region.pk],
                        owner_content_object=documentregion.document,
                    )

            last_level = Region.objects.filter(parent__in=last_level)
            depth += 1


    def test_users(self):
        try:
            users_list = self.django_client.get(reverse("flex-abac:user-list"))
            print(json.dumps(users_list.data, indent=4))

            user_detail = self.django_client.get(reverse("flex-abac:user-detail", args=(self.user_default.id,)))
            print(json.dumps(user_detail.data, indent=4))
            self.assertNotEqual(user_detail.data, {"detail": "Not found."}, "The detail should be there!")

            user_update = self.django_client.put(
                reverse("flex-abac:user-detail", args=(self.user_admin.id,)),
                {
                    "roles": [
                      self.role_admin.id,
                      self.role_default.id,
                   ]
                }, format="json")
            print(json.dumps(user_update.data, indent=4))

            user_update = self.django_client.put(
                reverse("flex-abac:user-detail", args=(self.user_admin.id,)),
                {
                    "roles": [
                        {
                            "name": "RoleCreate2",
                            "policies": [
                                {
                                    "name": "PolicyA",
                                    "actions": [
                                        {"name": "edit"},
                                        {"name": "view"},
                                    ],
                                    "scopes": [
                                        {
                                            "resourcetype": "CategoricalFilter",
                                            "value": "Brand1",
                                            "attribute_type": self.brand_attribute.id
                                        },
                                        {
                                            "resourcetype": "NestedCategoricalFilter",
                                            "value": 1,
                                            "attribute_type": self.topic_attribute.id
                                        },
                                        {
                                            "resourcetype": "MaterializedNestedCategoricalFilter",
                                            "value": 1,
                                            "attribute_type": self.attribute_region_levels[
                                                0].id
                                        }
                                    ]
                                },
                                {
                                    "name": "PolicyB",
                                    "actions": [
                                        self.action_view.id,
                                        self.action_edit.id
                                    ],
                                    "scopes": [
                                        self.brand_values[1].id,
                                        self.desk_values[1].id,
                                        self.topic_values[1].id,
                                        self.region_values[1].id
                                    ]
                                },
                                self.policy_default21.id,
                            ]
                        },
                      self.role_default.id,
                   ]
                }, format="json")
            print(json.dumps(user_update.data, indent=4))

            user_update = self.django_client.put(
                reverse("flex-abac:user-detail", args=(self.user_admin.id,)),
                {
                    "roles": []
                }, format="json")
            print(json.dumps(user_update.data, indent=4))

            user_add_role = self.django_client.put(
                reverse("flex-abac:user-add-roles", args=(user_update.data["pk"],)),
                {
                    "roles": [
                      self.role_admin.id,
                      self.role_default.id,
                   ],
                })
            print(json.dumps(user_add_role.data, indent=4))

            user_delete_role = self.django_client.delete(
                reverse("flex-abac:user-delete-roles", args=(user_add_role.data["pk"],)),
                {
                    "roles": [
                      self.role_admin.id,
                      self.role_default.id,
                   ],
                })
            print(json.dumps(user_delete_role.data, indent=4))

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_roles(self):
        try:
            roles_list = self.django_client.get(reverse("flex-abac:role-list"))
            print(json.dumps(roles_list.data, indent=4))

            role_detail = self.django_client.get(reverse("flex-abac:role-detail", args=(self.role_default.id,)))
            print(json.dumps(role_detail.data, indent=4))
            self.assertNotEqual(role_detail.data, {"detail": "Not found."}, "The detail should be there!")

            role_create = self.django_client.post(reverse("flex-abac:role-list"),
                                                    {
                                                        "name": "RoleCreate",
                                                        "policies": [
                                                            self.policy_admin.id,
                                                            self.policy_default12.id,
                                                            self.policy_default21.id,
                                                        ]
                                                    }, format="json")
            print(json.dumps(role_create.data, indent=4))

            role_create = self.django_client.post(reverse("flex-abac:role-list"),
                                                    {
                                                        "name": "RoleCreate2",
                                                        "policies": [
                                                            {
                                                                "name": "PolicyA",
                                                                "actions": [
                                                                    { "name": "edit",
                                                                      "pretty_name": "The user can edit - test",
                                                                      "models": [ 9 ],
                                                                     },
                                                                    { "name": "view",
                                                                      "pretty_name": "The user can view - test",
                                                                      "models": [ 7, 10 ],
                                                                    },
                                                                ],
                                                                "scopes": [
                                                                    {
                                                                        "resourcetype": "CategoricalFilter",
                                                                        "value": "Brand1",
                                                                        "attribute_type": self.brand_attribute.id
                                                                    },
                                                                    {
                                                                        "resourcetype": "NestedCategoricalFilter",
                                                                        "value": 1,
                                                                        "attribute_type": self.topic_attribute.id
                                                                    },
                                                                    {
                                                                        "resourcetype": "MaterializedNestedCategoricalFilter",
                                                                        "value": 1,
                                                                        "attribute_type": self.attribute_region_levels[
                                                                            0].id
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "name": "PolicyB",
                                                                "actions": [
                                                                    self.action_view.id,
                                                                    self.action_edit.id
                                                                ],
                                                                "scopes": [
                                                                    self.brand_values[1].id,
                                                                    self.desk_values[1].id,
                                                                    self.topic_values[1].id,
                                                                    self.region_values[1].id
                                                                ]
                                                            },
                                                            self.policy_default21.id,
                                                        ]
                                                    }, format="json")
            print(json.dumps(role_create.data, indent=4))



            role_update = self.django_client.put(
                reverse("flex-abac:role-detail", args=(self.role_default.id,)),
                {
                    "name": "RoleUpdate",
                    "policies": [
                        self.policy_admin.id,
                        self.policy_default21.id,
                        self.policy_default22.id
                    ]
                }, format="json")
            print(json.dumps(role_update.data, indent=4))

            role_create = self.django_client.post(reverse("flex-abac:role-list"),
                                                    {
                                                        "name": "RoleDummy",
                                                        "policies": [],
                                                    }, format="json")
            print(json.dumps(role_create.data, indent=4))

            role_add_policy = self.django_client.put(
                reverse("flex-abac:role-add-policies", args=(role_create.data["pk"],)),
                {
                    "policies": [
                        self.policy_admin.id,
                        self.policy_default.id
                    ],
                })
            print(json.dumps(role_add_policy.data, indent=4))

            role_delete_policy = self.django_client.delete(
                reverse("flex-abac:role-delete-policies", args=(role_add_policy.data["pk"],)),
                {
                    "policies": [
                        self.policy_admin.id,
                        self.policy_default.id
                    ],
                })
            print(json.dumps(role_delete_policy.data, indent=4))

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_policies(self):
        try:
            policies_list = self.django_client.get(reverse("flex-abac:policy-list"))
            print(json.dumps(policies_list.data, indent=4))

            policy_detail = self.django_client.get(reverse("flex-abac:policy-detail", args=(self.policy_default.id,)))
            print(json.dumps(policy_detail.data, indent=4))
            self.assertNotEqual(policy_detail.data, {"detail": "Not found."}, "The detail should be there!")

            policy_create = self.django_client.post(reverse("flex-abac:policy-list"),
                                                    {
                                                        "name": "Policy1",
                                                        "actions": [
                                                            self.action_view.id,
                                                            self.action_edit.id
                                                        ],
                                                        "scopes": [
                                                            self.brand_values[1].id,
                                                            self.desk_values[1].id,
                                                            self.topic_values[1].id,
                                                            self.region_values[1].id
                                                        ]
                                                    }, format="json")
            print(json.dumps(policy_create.data, indent=4))

            policy_create = self.django_client.post(reverse("flex-abac:policy-list"),
            {
                "name": "Policy2",
                "actions": [
                    { "name": "edit",
                      "pretty_name": "The user can edit - test",
                      "models": [ 9 ],
                     },
                    { "name": "view",
                      "pretty_name": "The user can view - test",
                      "models": [ 7, 10 ],
                    },
                ],
                "scopes": [
                    {
                        "resourcetype": "CategoricalFilter",
                        "value": "Brand1",
                        "attribute_type": self.brand_attribute.id
                    },
                    {
                        "resourcetype": "NestedCategoricalFilter",
                        "value": 1,
                        "attribute_type": self.topic_attribute.id
                    },
                    {
                        "resourcetype": "MaterializedNestedCategoricalFilter",
                        "value": 1,
                        "attribute_type": self.attribute_region_levels[0].id
                    }
                ]
            }, format="json")
            print(json.dumps(policy_create.data, indent=4))

            policy_update = self.django_client.put(
                reverse("flex-abac:policy-detail", args=(policy_create.data["pk"],)),
                {
                    "name": "Action2",
                    "actions": [
                        self.action_edit.id,
                    ],
                    "scopes": [
                        self.brand_values[2].id,
                        self.desk_values[2].id,
                        self.topic_values[2].id,
                        self.region_values[2].id
                    ]
                })
            print(json.dumps(policy_update.data, indent=4))

            policy_create = self.django_client.post(reverse("flex-abac:policy-list"),
                                                    {
                                                        "name": "PolicyDummy",
                                                        "actions": [],
                                                        "scopes": []
                                                    }, format="json")
            print(json.dumps(policy_create.data, indent=4))

            policy_add_action = self.django_client.put(
                reverse("flex-abac:policy-add-actions", args=(policy_create.data["pk"],)),
                {
                    "actions": [
                        self.action_edit.id,
                        self.action_view.id,
                    ],
                })
            print(json.dumps(policy_add_action.data, indent=4))

            policy_delete_action = self.django_client.delete(
                reverse("flex-abac:policy-delete-actions", args=(policy_create.data["pk"],)),
                {
                    "actions": [
                        self.action_edit.id,
                        self.action_view.id,
                    ],
                })
            print(json.dumps(policy_delete_action.data, indent=4))

            policy_add_scopes = self.django_client.put(
                reverse("flex-abac:policy-add-scopes", args=(policy_create.data["pk"],)),
                {
                    "scopes": [
                        self.brand_values[2].id,
                        self.desk_values[2].id,
                        self.topic_values[2].id,
                        self.region_values[2].id
                    ]
                })
            print(json.dumps(policy_add_scopes.data, indent=4))

            all_active_attributes = self.django_client.get(reverse("flex-abac:policy-get-all-active-attributes", args=(self.policy_default.id,)))
            print(json.dumps(all_active_attributes.data, indent=4))
            self.assertNotEqual(all_active_attributes.data, {"detail": "Not found."}, "The detail should be there!")

            policy_delete_scopes = self.django_client.delete(
                reverse("flex-abac:policy-delete-scopes", args=(policy_create.data["pk"],)),
                {
                    "scopes": [
                        self.brand_values[2].id,
                        self.desk_values[2].id,
                        self.topic_values[2].id,
                        self.region_values[2].id
                    ]
                })
            print(json.dumps(policy_delete_scopes.data, indent=4))

            self.django_client.delete(reverse("flex-abac:policy-detail", args=(self.policy_default.id,)))
            self.assertFalse(Policy.objects.filter(id=self.policy_default.id).exists(),
                             "Object has not been properly removed!")
            self.assertFalse(PolicyAction.objects.filter(policy=self.policy_default.id).exists(),
                             "Object has not been properly removed!")
            for policy_value_type in PolicyFilter.__subclasses__():
                self.assertFalse(policy_value_type.objects.filter(policy=self.policy_default.id).exists(),
                                 "Object has not been properly removed!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_actions(self):
        try:
            actions_list = self.django_client.get(reverse("flex-abac:action-list"))
            print(json.dumps(actions_list.data, indent=4))

            action_detail = self.django_client.get(reverse("flex-abac:action-detail", args=(self.action_view.id,)))
            print(json.dumps(action_detail.data, indent=4))
            self.assertNotEqual(action_detail.data, {"detail": "Not found."}, "The detail should be there!")

            action_create = self.django_client.post(reverse("flex-abac:action-list"),
                                                             {
                                                                 "name": "Action1",
                                                             })
            print(json.dumps(action_create.data, indent=4))

            action_update = self.django_client.put(
                reverse("flex-abac:action-detail", args=(self.action_view.id,)),
                {
                    "name": "Action2",
                })
            print(json.dumps(action_update.data, indent=4))

            self.django_client.delete(reverse("flex-abac:action-detail", args=(self.action_view.id,)))
            self.assertFalse(Action.objects.filter(id=self.action_view.id).exists(),
                             "Object has not been properly removed!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_attribute_filters(self):
        try:
            attribute_filters_list = self.django_client.get(reverse("flex-abac:basefilter-list"))
            print(json.dumps(attribute_filters_list.data, indent=4))

            attribute_filter_detail = self.django_client.get(reverse("flex-abac:basefilter-detail", args=(self.brand_values[1].id,)))
            print(json.dumps(attribute_filter_detail.data, indent=4))
            self.assertNotEqual(attribute_filter_detail.data, {"detail": "Not found."}, "The detail should be there!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_generic_attribute_filters(self):
        try:
            actions_list = self.django_client.get(reverse("flex-abac:basefilter-list"))
            print(json.dumps(actions_list.data, indent=4))

            attribute_filter_detail = self.django_client.get(reverse("flex-abac:basefilter-detail", args=(self.brand_values[1].id,)))
            print(json.dumps(attribute_filter_detail.data, indent=4))
            self.assertNotEqual(attribute_filter_detail.data, {"detail": "Not found."}, "The detail should be there!")

            attribute_filter_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                             {
                                                                 "resourcetype": "CategoricalFilter",
                                                                 "value": "Brand1",
                                                                 "attribute_type": self.brand_attribute.id
                                                             })
            print(json.dumps(attribute_filter_create.data, indent=4))

            attribute_filter_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                             {
                                                                 "resourcetype": "GenericFilter",
                                                                 "value": ("2020-04-05", "2020-04-06"),
                                                                 "attribute_type": {
                                                                    "pk": GenericAttribute.objects.get(field_name="document_datetime__range").id,
                                                                    "name": "Document date",
                                                                    "field_name": "document_datetime__range",
                                                                    "class_name": "exampleapp.document",
                                                                    "resourcetype": "GenericAttribute"
                                                                }
                                                             }, format="json")
            print(json.dumps(attribute_filter_create.data, indent=4))


            attribute_filter_update = self.django_client.put(reverse("flex-abac:basefilter-detail", args=(self.desk_values[1].id,)),
                                                             {
                                                                 "resourcetype": "GenericFilter",
                                                                 "value": "Desk1",
                                                                 "attribute_type": self.desk_attribute.id
                                                             }, format="json")
            print(json.dumps(attribute_filter_update.data, indent=4))

            attribute_filter_update = self.django_client.put(
                reverse("flex-abac:basefilter-detail", args=(self.desk_values[1].id,)),
                {
                    "resourcetype": "GenericFilter",
                    "value": "Desk1",
                    "attribute_type": self.desk_attribute.id
                }, format="json")
            print(json.dumps(attribute_filter_update.data, indent=4))

            attribute_filter_update = self.django_client.put(reverse("flex-abac:basefilter-detail", args=(self.desk_values[1].id,)),
                                                             {
                                                                 "resourcetype": "GenericFilter",
                                                                 "value": "Desk1",
                                                                 "attribute_type": self.desk_attribute.id
                                                             }, format="json")
            print(json.dumps(attribute_filter_update.data, indent=4))

            self.django_client.delete(reverse("flex-abac:basefilter-detail", args=(self.brand_values[1].id,)))
            self.assertFalse(GenericFilter.objects.filter(id=self.brand_values[1].id).exists(),
                             "Object has not been properly removed!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_nested_categorical_attribute_filters(self):
        try:
            attribute_filter_detail = self.django_client.get(reverse("flex-abac:basefilter-detail", args=(self.topic_values[1].id,)))
            print(json.dumps(attribute_filter_detail.data, indent=4))
            self.assertNotEqual(attribute_filter_detail.data, {"detail": "Not found."}, "The detail should be there!")

            attribute_filter_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                             {
                                                                 "resourcetype": "NestedCategoricalFilter",
                                                                 "value": 1,
                                                                 "extra": {},
                                                                 "attribute_type": self.topic_attribute.id
                                                             }, format="json")
            print(json.dumps(attribute_filter_create.data, indent=4))

            attribute_filter_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                             {
                                                                 "resourcetype": "NestedCategoricalFilter",
                                                                 "value": 2,
                                                                 "extra": {},
                                                                 "attribute_type": {
                                                                    "pk": NestedCategoricalAttribute.objects.get(field_name="topics").id,
                                                                    "name": "Topic name",
                                                                    "field_name": "topics",
                                                                    "nested_field_name": "name",
                                                                    "parent_field_name": "parent",
                                                                    "field_type": "exampleapp.topic",
                                                                    "class_name": "exampleapp.document",
                                                                    "resourcetype": "NestedCategoricalAttribute"
                                                                }
                                                             }, format="json")
            print(json.dumps(attribute_filter_create.data, indent=4))

            attribute_filter_update  = self.django_client.put(reverse("flex-abac:basefilter-detail", args=(self.topic_values[1].id,)),
                                                             {
                                                                 "resourcetype": "NestedCategoricalFilter",
                                                                 "value": 9999,
                                                                 "attribute_type": self.topic_attribute.id
                                                             }, format="json")
            print(json.dumps(attribute_filter_update.data, indent=4))

            attribute_filter_update = self.django_client.put(reverse("flex-abac:basefilter-detail", args=(self.topic_values[2].id,)),
                                                             {
                                                                 "resourcetype": "NestedCategoricalFilter",
                                                                 "value": 9998,
                                                                 "extra": {},
                                                                 "attribute_type": {
                                                                    "pk": NestedCategoricalAttribute.objects.get(field_name="topics").id,
                                                                    "name": "Topic name",
                                                                    "field_name": "topics",
                                                                    "nested_field_name": "name",
                                                                    "parent_field_name": "parent",
                                                                    "field_type": "exampleapp.topic",
                                                                    "class_name": "exampleapp.document",
                                                                    "resourcetype": "NestedCategoricalAttribute"
                                                                }
                                                             }, format="json")
            print(json.dumps(attribute_filter_update.data, indent=4))

            self.django_client.delete(reverse("flex-abac:basefilter-detail", args=(self.topic_values[1].id,)))
            self.assertFalse(NestedCategoricalFilter.objects.filter(id=self.topic_values[1].id).exists(),
                             "Object has not been properly removed!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_materialized_nested_categorical_attribute_filters(self):
        try:
            attribute_filter_detail = self.django_client.get(reverse("flex-abac:basefilter-detail", args=(self.region_values[1].id,)))
            print(json.dumps(attribute_filter_detail.data, indent=4))
            self.assertNotEqual(attribute_filter_detail.data, {"detail": "Not found."}, "The detail should be there!")

            attribute_filter_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                             {
                                                                 "resourcetype": "MaterializedNestedCategoricalFilter",
                                                                 "value": "Province1",
                                                                 "attribute_type": self.region_province_attribute.id
                                                             }, format="json")
            print(json.dumps(attribute_filter_create.data, indent=4))

            attribute_filter_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                             {
                                                                 "resourcetype": "MaterializedNestedCategoricalFilter",
                                                                 "value": "Province2",
                                                                 "attribute_type": {
                                                                    "pk": MaterializedNestedCategoricalAttribute.objects.get(name="Province").id,
                                                                    "name": "Province",
                                                                    "parent": 6,
                                                                    "class_name": "exampleapp.document",
                                                                    "resourcetype": "MaterializedNestedCategoricalAttribute"
                                                                }
                                                             }, format="json")
            print(json.dumps(attribute_filter_create.data, indent=4))

            attribute_filter_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                             {
                                                                 "resourcetype": "MaterializedNestedCategoricalFilter",
                                                                 "value": "Province3",
                                                                 "parent": self.region_values[1].id,
                                                                 "attribute_type": self.region_province_attribute.id
                                                             }, format="json")
            print(json.dumps(attribute_filter_create.data, indent=4))

            attribute_value_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                             {
                                                                 "resourcetype": "MaterializedNestedCategoricalFilter",
                                                                 "value": "Province4",
                                                                 "parent": self.region_values[1].id,
                                                                 "attribute_type": {
                                                                    "pk": MaterializedNestedCategoricalAttribute.objects.get(name="Province").id,
                                                                    "name": "Province",
                                                                    "parent": 6,
                                                                    "class_name": "exampleapp.document",
                                                                    "resourcetype": "MaterializedNestedCategoricalAttribute"
                                                                },
                                                             }, format="json")
            print(json.dumps(attribute_filter_create.data, indent=4))

            attribute_filter_update = self.django_client.put(reverse("flex-abac:basefilter-detail", args=(self.region_values[1].id,)),
                                                             {
                                                                 "resourcetype": "MaterializedNestedCategoricalFilter",
                                                                 "value": "Country1",
                                                                 "attribute_type": self.region_country_attribute.id
                                                             }, format="json")
            print(json.dumps(attribute_filter_update.data, indent=4))

            attribute_filter_update = self.django_client.put(reverse("flex-abac:basefilter-detail", args=(self.region_values[1].id,)),
                                                             {
                                                                 "resourcetype": "MaterializedNestedCategoricalFilter",
                                                                 "value": "Country2",
                                                                 "attribute_type": {
                                                                    "pk": MaterializedNestedCategoricalAttribute.objects.get(name="Country").id,
                                                                    "name": "Country",
                                                                    "parent": None,
                                                                    "class_name": "exampleapp.document",
                                                                    "resourcetype": "MaterializedNestedCategoricalAttribute"
                                                                }
                                                             }, format="json")
            print(json.dumps(attribute_filter_update.data, indent=4))

            attribute_filter_update = self.django_client.put(
                reverse("flex-abac:basefilter-detail", args=(self.region_values[3].id,)),
                {
                    "resourcetype": "MaterializedNestedCategoricalFilter",
                    "value": "Province5",
                    "parent": self.region_values[1].id,
                    "attribute_type": self.region_province_attribute.id
                }, format="json")
            print(json.dumps(attribute_filter_update.data, indent=4))

            attribute_filter_update = self.django_client.put(
                reverse("flex-abac:basefilter-detail", args=(self.region_values[3].id,)),
                {
                    "resourcetype": "MaterializedNestedCategoricalFilter",
                    "value": "Province6",
                    "parent": self.region_values[1].id,
                    "attribute_type": {
                        "pk": MaterializedNestedCategoricalAttribute.objects.get(name="Province").id,
                        "name": "Province",
                        "parent": 6,
                        "class_name": "exampleapp.document",
                        "resourcetype": "MaterializedNestedCategoricalAttribute"
                    }
                }, format="json")
            print(json.dumps(attribute_filter_update.data, indent=4))

            self.django_client.delete(reverse("flex-abac:basefilter-detail", args=(self.region_values[1].id,)))
            self.assertFalse(MaterializedNestedCategoricalFilter.objects.filter(id=self.region_values[1].id).exists(),
                             "Object has not been properly removed!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_attribute_types(self):
        try:
            attribute_filters_list = self.django_client.get(reverse("flex-abac:baseattribute-list"))
            print(json.dumps(attribute_filters_list.data, indent=4))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_generic_attribute_types(self):
        try:
            attribute_type_detail = self.django_client.get(reverse("flex-abac:baseattribute-detail", args=(self.brand_attribute.id,)))
            print(json.dumps(attribute_type_detail.data, indent=4))
            self.assertNotEqual(attribute_type_detail.data, {"detail": "Not found."}, "The detail should be there!")

            attribute_type_create = self.django_client.post(reverse("flex-abac:baseattribute-list"),
                                                             {
                                                                 "resourcetype": "GenericAttribute",
                                                                 "name": "Brand id",
                                                                 "field_name": "brand__id",
                                                                 "class_name": "exampleapp.document",
                                                             })
            print(json.dumps(attribute_type_create.data, indent=4))

            attribute_type_update = self.django_client.put(reverse("flex-abac:baseattribute-detail", args=(self.brand_attribute.id,)),
                                                             {
                                                                 "resourcetype": "GenericAttribute",
                                                                 "name": "Brand id2",
                                                                 "field_name": "brand__id2",
                                                             })
            print(json.dumps(attribute_type_update.data, indent=4))

            self.django_client.delete(reverse("flex-abac:baseattribute-detail", args=(self.brand_attribute.id,)))
            self.assertFalse(GenericAttribute.objects.filter(id=self.brand_attribute.id).exists(),
                             "Object has not been properly removed!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_nested_categorical_attribute_types(self):
        try:
            attribute_value_detail = self.django_client.get(reverse("flex-abac:baseattribute-detail", args=(self.topic_attribute.id,)))
            print(json.dumps(attribute_value_detail.data, indent=4))
            self.assertNotEqual(attribute_value_detail.data, {"detail": "Not found."}, "The detail should be there!")

            attribute_type_create = self.django_client.post(reverse("flex-abac:baseattribute-list"),
                                                             {
                                                                 "resourcetype": "NestedCategoricalAttribute",
                                                                 "name": "Topic id",
                                                                 "field_name": "topics",
                                                                 "nested_field_name": "id",
                                                                 "parent_field_name": "parent__id",
                                                                 "field_type": "exampleapp.topic",
                                                                 "class_name": "exampleapp.document",
                                                             })
            print(json.dumps(attribute_type_create.data, indent=4))

            attribute_type_update = self.django_client.put(reverse("flex-abac:baseattribute-detail", args=(self.topic_attribute.id,)),
                                                             {
                                                                 "resourcetype": "NestedCategoricalAttribute",
                                                                 "name": "Topic id2",
                                                                 "field_name": "topics2",
                                                                 "nested_field_name": "id2",
                                                                 "parent_field_name": "parent__id2",
                                                             })
            print(json.dumps(attribute_type_update.data, indent=4))

            self.django_client.delete(reverse("flex-abac:baseattribute-detail", args=(self.topic_attribute.id,)))
            self.assertFalse(NestedCategoricalAttribute.objects.filter(id=self.topic_attribute.id).exists(),
                             "Object has not been properly removed!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_materialized_nested_categorical_attribute_types(self):
        try:
            attribute_value_detail = self.django_client.get(reverse("flex-abac:baseattribute-detail", args=(self.region_country_attribute.id,)))
            print(json.dumps(attribute_value_detail.data, indent=4))
            self.assertNotEqual(attribute_value_detail.data, {"detail": "Not found."}, "The detail should be there!")

            attribute_value_detail = self.django_client.get(
                reverse("flex-abac:baseattribute-detail", args=(self.region_province_attribute.id,)))
            print(json.dumps(attribute_value_detail.data, indent=4))
            self.assertNotEqual(attribute_value_detail.data, {"detail": "Not found."}, "The detail should be there!")

            attribute_type_create = self.django_client.post(reverse("flex-abac:baseattribute-list"),
                                                             {
                                                                 "resourcetype": "MaterializedNestedCategoricalAttribute",
                                                                 "name": "Planet",
                                                                 "class_name": "exampleapp.document"
                                                             })
            print(json.dumps(attribute_type_create.data, indent=4))

            attribute_type_create = self.django_client.post(reverse("flex-abac:baseattribute-list"),
                                                             {
                                                                 "resourcetype": "MaterializedNestedCategoricalAttribute",
                                                                 "name": "Continent",
                                                                 "parent": MaterializedNestedCategoricalAttribute.objects.get(name="Planet").id,
                                                                 "class_name": "exampleapp.document"
                                                             })
            print(json.dumps(attribute_type_create.data, indent=4))

            attribute_type_update = self.django_client.put(reverse("flex-abac:baseattribute-detail", args=(self.region_province_attribute.id,)),
                 {
                     "resourcetype": "MaterializedNestedCategoricalAttribute",
                     "name": "Province2",
                 })
            print(json.dumps(attribute_type_update.data, indent=4))

            attribute_type_update = self.django_client.put(reverse("flex-abac:baseattribute-detail", args=(self.region_province_attribute.id,)),
                {
                    "resourcetype": "MaterializedNestedCategoricalAttribute",
                    "name": "Province2",
                    "parent": MaterializedNestedCategoricalAttribute.objects.get(name="Planet").id,
                })
            print(json.dumps(attribute_type_update.data, indent=4))

            self.django_client.delete(reverse("flex-abac:baseattribute-detail", args=(self.region_province_attribute.id,)))
            self.assertFalse(
                MaterializedNestedCategoricalAttribute.objects.filter(id=self.region_province_attribute.id).exists(),
                "Object has not been properly removed!"
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_possible_values_for_attribute(self):
        try:
            attribute_values_list = self.django_client.get(reverse("flex-abac:possible-values-list"))
            print(json.dumps(attribute_values_list.data, indent=4))

            attribute_values_categorical = self.django_client.get(reverse("flex-abac:possible-values-detail", args=(self.brand_attribute.id,)))
            print(json.dumps(attribute_values_categorical.data, indent=4))

            for attribute_value in attribute_values_categorical.data["possible_values"]:
                attribute_value_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                                 attribute_value, format="json")
                print(json.dumps(attribute_value_create.data, indent=4))

            attribute_values_categorical = self.django_client.get(reverse("flex-abac:possible-values-detail", args=(self.datetime_attribute.id,)))
            print(json.dumps(attribute_values_categorical.data, indent=4))

            for attribute_value in attribute_values_categorical.data["possible_values"]:
                attribute_value_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                                 attribute_value, format="json")
                print(json.dumps(attribute_value_create.data, indent=4))


            attribute_values_categorical = self.django_client.get(reverse("flex-abac:possible-values-detail", args=(self.desk_attribute.id,)))
            print(json.dumps(attribute_values_categorical.data, indent=4))

            for attribute_value in attribute_values_categorical.data["possible_values"]:
                pprint(attribute_value)
                attribute_value_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                                 attribute_value, format="json")
                print(json.dumps(attribute_value_create.data, indent=4))

            PolicyCategoricalFilter.objects.create(policy=self.policy_default, value=self.desk_fk_values[1])

            attribute_values_categorical = self.django_client.get(
                reverse("flex-abac:possible-values-detail", args=(self.desk_fk_attribute.id,)))
            print(json.dumps(attribute_values_categorical.data, indent=4))

            for attribute_value in attribute_values_categorical.data["possible_values"]:
                pprint(attribute_value)
                attribute_value_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                                 attribute_value, format="json")
                print(json.dumps(attribute_value_create.data, indent=4))

            attribute_values_nested = self.django_client.get(reverse("flex-abac:possible-values-detail", args=(self.topic_attribute.id,)))
            print(json.dumps(attribute_values_nested.data, indent=4))

            for attribute_value in attribute_values_nested.data["possible_values"]:
                attribute_value_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                                 attribute_value, format="json")
                print(json.dumps(attribute_value_create.data, indent=4))

            attribute_values_nested = self.django_client.get(reverse("flex-abac:possible-values-detail", args=(self.category_attribute.id,)))
            print(json.dumps(attribute_values_nested.data, indent=4))

            for attribute_value in attribute_values_nested.data["possible_values"]:
                attribute_value_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                                 attribute_value, format="json")
                print(json.dumps(attribute_value_create.data, indent=4))


            attribute_values_materialized_nested = self.django_client.get(reverse("flex-abac:possible-values-detail", args=(self.region_country_attribute.id,)))
            print(json.dumps(attribute_values_materialized_nested.data, indent=4))

            for attribute_value in attribute_values_materialized_nested.data["possible_values"]:
                attribute_value_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                                 attribute_value, format="json")
                print(json.dumps(attribute_value_create.data, indent=4))

            attribute_values_materialized_nested = self.django_client.get(reverse("flex-abac:possible-values-detail", args=(self.region_province_attribute.id,)))
            print(json.dumps(attribute_values_materialized_nested.data, indent=4))

            for attribute_value in attribute_values_materialized_nested.data["possible_values"]:
                attribute_value_create = self.django_client.post(reverse("flex-abac:basefilter-list"),
                                                                 attribute_value, format="json")
                print(json.dumps(attribute_value_create.data, indent=4))

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_get_allowed_values_per_user_and_attribute(self):
        try:
            PolicyCategoricalFilter.objects.create(policy=self.policy_default, value=self.desk_fk_values[1])
            for attribute_type in [self.brand_attribute, self.desk_attribute, self.datetime_attribute,
                                   self.topic_attribute, self.category_attribute, self.region_country_attribute,
                                   self.region_province_attribute, self.region_city_attribute]:

                attribute_value_detail = self.django_client.get(reverse("flex-abac:baseattribute-get-all-allowed-values",
                                                                        args=(attribute_type.id,)))
                print(json.dumps(attribute_value_detail.data, indent=4))
                self.assertNotEqual(attribute_value_detail.data, {"detail": "Not found."}, "The detail should be there!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_get_allowed_values_per_user(self):
        try:
            all_allowed_values = self.django_client.get(reverse("flex-abac:user-get-all-allowed-values"),
                                                        { "models": "exampleapp.document,exampleapp.desk"})
            print(json.dumps(all_allowed_values.data, indent=4))

            all_allowed_values = self.django_client.get(reverse("flex-abac:user-get-all-allowed-values"),
                                                        {"models": "exampleappunknown"})
            print(all_allowed_values.data, all_allowed_values.status_code)
            self.assertEqual(all_allowed_values.status_code, 400, "A 400 error should have been triggered!")

            all_allowed_values = self.django_client.get(reverse("flex-abac:user-get-all-allowed-values"),
                                                        {"models": "exampleapp.unknown"})
            print(all_allowed_values.data, all_allowed_values.status_code)
            self.assertEqual(all_allowed_values.status_code, 400, "A 400 error should have been triggered!")

            all_allowed_values = self.django_client.get(reverse("flex-abac:user-get-all-allowed-values"))
            print(json.dumps(all_allowed_values.data, indent=4))
            self.assertEqual(all_allowed_values.status_code, 400, "A 400 error should have been triggered!")

        except Exception as e:
                import traceback
                traceback.print_exc()
                self.fail(repr(e))

    def test_applied_permisssions_on_views(self):
        if not getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False):
            return

        try:
            admin_client = APIClient(enforce_csrf_checks=False)
            admin_client.force_authenticate(user=self.user_admin)

            viewer_client = APIClient(enforce_csrf_checks=False)
            viewer_client.force_authenticate(user=self.user_default)

            UserRole.objects.filter(user=self.user_admin).delete()
            UserRole.objects.filter(user=self.user_default).delete()

            flex_abac_admin_role = Role.objects.get(name=flex_abac.constants.SUPERADMIN_ROLE)
            flex_abac_viewer_role = Role.objects.get(name="flex-abac Viewer Role")

            # UserRoleFactory.create(user=self.user_admin, role=flex_abac_admin_role)
            flex_abac_admin_role.users.add(self.user_admin)
            flex_abac_viewer_role.users.add(self.user_default)

            model_names = ["user", "role", "policy", "action", "basefilter", "baseattribute"]
            for model_name in model_names:
                # List
                response = admin_client.get(reverse(f"flex-abac:{model_name}-list"))
                self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

                response = viewer_client.get(reverse(f"flex-abac:{model_name}-list"))
                self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

                # Retrieve
                response = admin_client.get(reverse(f"flex-abac:{model_name}-detail", args=(-1,)))
                self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

                response = viewer_client.get(reverse(f"flex-abac:{model_name}-detail", args=(-1,)))
                self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

                # Create
                response = admin_client.post(reverse(f"flex-abac:{model_name}-list"), {})
                self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

                response = viewer_client.post(reverse(f"flex-abac:{model_name}-list"), {})
                self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

                # Update
                response = admin_client.put(reverse(f"flex-abac:{model_name}-detail", args=(-1,)), {})
                self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

                response = viewer_client.put(reverse(f"flex-abac:{model_name}-detail", args=(-1,)), {})
                self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

                # Delete
                response = admin_client.delete(reverse(f"flex-abac:{model_name}-detail", args=(-1,)))
                self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

                response = viewer_client.delete(reverse(f"flex-abac:{model_name}-detail", args=(-1,)))
                self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            # User extra actions
            ## add_roles
            response = admin_client.put(reverse("flex-abac:user-add-roles", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

            response = viewer_client.put(reverse("flex-abac:user-add-roles", args=(-1,)), {})
            self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            ## delete_roles
            response = admin_client.delete(reverse("flex-abac:user-delete-roles", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

            response = viewer_client.delete(reverse("flex-abac:user-delete-roles", args=(-1,)), {})
            self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            # Role extra actions
            ## add_policy
            response = admin_client.put(reverse("flex-abac:role-add-policies", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

            response = viewer_client.put(reverse("flex-abac:role-add-policies", args=(-1,)), {})
            self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            ## delete_policy
            response = admin_client.delete(reverse("flex-abac:role-delete-policies", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

            response = viewer_client.delete(reverse("flex-abac:role-delete-policies", args=(-1,)), {})
            self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            # Policy extra actions
            ## add_actions
            response = admin_client.put(reverse("flex-abac:policy-add-actions", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

            response = viewer_client.put(reverse("flex-abac:policy-add-actions", args=(-1,)), {})
            self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            ## delete_actions
            response = admin_client.delete(reverse("flex-abac:policy-delete-actions", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

            response = viewer_client.delete(reverse("flex-abac:policy-delete-actions", args=(-1,)), {})
            self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            ## add_scopes
            response = admin_client.put(reverse("flex-abac:policy-add-scopes", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

            response = viewer_client.put(reverse("flex-abac:policy-add-scopes", args=(-1,)), {})
            self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            ## delete_scopes
            response = admin_client.delete(reverse("flex-abac:policy-delete-scopes", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

            response = viewer_client.delete(reverse("flex-abac:policy-delete-scopes", args=(-1,)), {})
            self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            ## get_all_active_attributes
            response = admin_client.get(reverse("flex-abac:policy-get-all-active-attributes", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

            response = viewer_client.get(reverse("flex-abac:policy-get-all-active-attributes", args=(-1,)), {})
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

    def test_anonymous_user(self):
        CHECK_PERMISSIONS = getattr(settings, "USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS", False)

        try:
            flex_abac_admin_role = Role.objects.get(name=flex_abac.constants.SUPERADMIN_ROLE)

            anon_client = APIClient(enforce_csrf_checks=False)

            response = anon_client.get(reverse("flex-abac:role-list"))
            if CHECK_PERMISSIONS:
                self.assertEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")
            else:
                self.assertNotEqual(response.status_code, 403, "You shouldn't have permissions to access the endpoint!")

            # Adding Anonymous user as flex_abac admin
            UserRole.objects.create(user=None, role=flex_abac_admin_role)

            response = anon_client.get(reverse("flex-abac:role-list"))
            self.assertNotEqual(response.status_code, 403, "You should have permissions to access the endpoint!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(repr(e))

