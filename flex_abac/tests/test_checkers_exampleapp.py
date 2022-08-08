import os
from django.test import TestCase
from exampleapp.models import (
    Brand, Document, Documenttopics, Desk, Topic, Region, Category, Documentregions
)
from datetime import datetime, timedelta
import pytz
from django.contrib.auth.models import User
from django.core.validators import ValidationError
from flex_abac.factories.actionfactory import ActionFactory
from flex_abac.factories.policyactionfactory import PolicyActionFactory
from flex_abac.factories.rolefactory import RoleFactory
from flex_abac.factories.policyfactory import PolicyFactory
from flex_abac.factories.userrolefactory import UserRoleFactory
from flex_abac.factories.rolepolicyfactory import RolePolicyFactory
from django.contrib.contenttypes.models import ContentType
from flex_abac.models import UserRole, Policy, RolePolicy, \
    Action, PolicyAction, GenericFilter, GenericAttribute, \
    CategoricalAttribute, CategoricalFilter, ModelCategoricalAttribute, \
    Action, ActionModel, PolicyAction, GenericFilter, GenericAttribute, \
    NestedCategoricalAttribute, MaterializedNestedCategoricalAttribute, \
    NestedCategoricalFilter, MaterializedNestedCategoricalFilter, \
    PolicyGenericFilter, PolicyCategoricalFilter, ModelGenericAttribute, \
    PolicyNestedCategoricalFilter, PolicyMaterializedNestedCategoricalFilter,\
    ModelNestedCategoricalAttribute, ModelMaterializedNestedCategoricalAttribute, \
    ItemMaterializedNestedCategoricalFilter
from flex_abac.checkers import is_object_in_scope, can_user_do, \
    is_attribute_query_in_scope, list_valid_objects, get_filter_for_valid_objects
from exampleapp.tests.utils.build_category_tree import build_category_tree

class CheckersTestCase(TestCase):
    fixtures = ['exampleapp']

    def setUp(self):
        # Retrieving users
        self.user_default = User.objects.get(id=1)
        self.user_admin = User.objects.get(id=2)

        # Just creates the categories by using treebeard, since it is not possible to do so directly from fixtures
        build_category_tree()

        # We create several roles (In the end, collections of policies).
        self.role_default = RoleFactory.create(name="default")
        self.role_default2 = RoleFactory.create(name="default2")
        self.role_admin = RoleFactory.create(name="admin")

        UserRoleFactory.create(user=self.user_default, role=self.role_default)
        UserRoleFactory.create(user=self.user_default, role=self.role_default2)
        UserRoleFactory.create(user=self.user_admin, role=self.role_admin)

        # We create several policies (In the end, collections of actions and the associated scopes)
        self.policy_default = PolicyFactory.create(name="default")
        self.policy_default11 = PolicyFactory.create(name="default1.1")
        self.policy_default12 = PolicyFactory.create(name="default1.2")
        self.policy_default21 = PolicyFactory.create(name="default2.1")
        self.policy_default22 = PolicyFactory.create(name="default2.2")
        self.policy_admin = PolicyFactory.create(name="admin")

        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default)
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default11)
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default12)
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default21)
        RolePolicyFactory.create(role=self.role_default, policy=self.policy_default22)
        RolePolicyFactory.create(role=self.role_admin, policy=self.policy_admin)

        # Actions (defines which can be done by the user associated to a policy)
        self.action_view = ActionFactory.create(name="view")
        self.action_edit = ActionFactory.create(name="edit")

        # Default policy can view; admin policy can view and edit
        PolicyActionFactory.create(policy=self.policy_default, action=self.action_view)
        PolicyActionFactory.create(policy=self.policy_admin, action=self.action_view)
        PolicyActionFactory.create(policy=self.policy_admin, action=self.action_edit)

        # Attributes. One per each class we will be using for checking (in our case, just the documents model)
        self.brand_attribute = CategoricalAttribute.objects.create(name="Brand name", field_name="brand__name")
        self.desk_attribute = GenericAttribute.objects.create(name="Desk name", field_name="desk__name")
        self.datetime_attribute = GenericAttribute.objects.create(name="Document date", field_name="document_datetime__range")
        # TODO: Try adding name__contains
        self.topic_attribute = NestedCategoricalAttribute.objects.create(name="Topic name",
                                                                         field_type=ContentType.objects.get_for_model(Topic),
                                                                         field_name="topics",
                                                                         nested_field_name="name",
                                                                         parent_field_name="parent")
        #  For materialized trees maintained by user:
        self.category_attribute = NestedCategoricalAttribute.objects.create(name="Category name",
                                                                             field_type=ContentType.objects.get_for_model(Category),
                                                                             field_name="categories",
                                                                             nested_field_name="name",
                                                                             parent_field_name="parent")


        # # For materialized trees things are slightly different. First, we need to define the relation between different levels
        # get_subtree_attr = lambda node_id: MaterializedNestedCategoricalAttribute.objects.get(pk=node_id)
        #
        # region_country = MaterializedNestedCategoricalAttribute.add_root(name='Country')
        # region_province = get_subtree_attr(region_country.pk).add_child(name='Province')
        # region_city = get_subtree_attr(region_province.pk).add_child(name='City')
        #
        # self.attribute_region_levels = [region_country, region_province, region_city]



        # Document content type
        document_content_type = ContentType.objects.get_for_model(Document)

        # We need to register the new attribute so it can be found later by the checkers
        ModelCategoricalAttribute.objects.create(
            attribute_type=self.brand_attribute,  # The attribute type (brand__name field in this case)
            owner_content_object=document_content_type  # the content type for the Document model
        )
        ModelGenericAttribute.objects.create(
            attribute_type=self.desk_attribute,  # The attribute type (desk__name field in this case)
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
        # for tree_level in self.attribute_region_levels:
        #     ModelMaterializedNestedCategoricalAttribute.objects.create(
        #         attribute_type=tree_level,  # The attribute type (tree_levl field in this case)
        #         owner_content_object=document_content_type  # the content type for the Document model
        #     )

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
        for desk in Desk.objects.all():
            self.desk_values[desk.id] = GenericFilter.objects.create(
                value=desk.name,
                attribute_type=self.desk_attribute,
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
                value=topic.name,
                attribute_type=self.topic_attribute,
            )

        # Values for categories (one per each of the categories in database)
        # We are using nested categorical values for this
        self.category_values = {}
        for category in Category.objects.all():
            self.category_values[category.name] = NestedCategoricalFilter.objects.create(
                value=category.name,
                attribute_type=self.category_attribute,
            )

        # Values for regions (one per each of the regions in database)
        # We are using materialized nested categorical values for this
        # First, we need to create the materialized tree on treebeard (which we will need to maintain when
        # an update occurs)
        # self.add_values_for_regions()


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
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_default, value=self.category_values["Category 1.1"])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_default, value=self.category_values["Category 1.2.1"])
        # TODO: Recover these after checking the get_attribute_value function
        # PolicyMaterializedNestedCategoricalFilter.objects.create(policy=self.policy_default, value=self.region_values[2])
        # PolicyMaterializedNestedCategoricalFilter.objects.create(policy=self.policy_default, value=self.region_values[6])

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
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_admin, value=self.category_values["Category 1.1.2"])
        PolicyNestedCategoricalFilter.objects.create(policy=self.policy_admin, value=self.category_values["Category 1.2.2"])
        # PolicyMaterializedNestedCategoricalFilter.objects.create(policy=self.policy_admin, value=self.region_values[5])
        # PolicyMaterializedNestedCategoricalFilter.objects.create(policy=self.policy_admin, value=self.region_values[7])

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

    def test_data_created(self):

        print("Brand:")
        print("------")
        for brand in Brand.objects.all():
            print(" - " + brand.name)

        print("\nDesk:")
        print("------")
        for desk in Desk.objects.all():
            print(" - " + desk.name)

        print("\nTopic:")
        print("------")
        for topic in Topic.objects.all():
            print(f" - {topic.name} <= {topic.parent.name if topic.parent else None}")

        print("\nDocument:")
        print("------")
        for document in Document.objects.all():
            print(f" - {document.filename}, {document.document_datetime}, {document.desk.name}, {document.brand.name}")

        print("\nDocumenttopics:")
        print("------")
        for documenttopic in Documenttopics.objects.all():
            print(f" - {documenttopic.document.filename}, {documenttopic.topic.name}")

        self.assertTrue(True)

    def test_documents_are_in_policy_default_scope(self):
        documents = Document.objects.filter(
            brand_id__in=(1, 3),
            desk_id__in=(1,),
            document_datetime__range=(pytz.UTC.localize(datetime(2021, 8, 4)), pytz.UTC.localize(datetime(2021, 8, 6))),
            topics__name__in=("Topic 1.1", "Topic 1.1.1", "Topic 1.1.2", "Topic 1.2.1"),
            categories__name__in=("Category 1.1", "Category 1.1.1", "Category 1.1.2", "Category 1.2.1"),
            regions__name__in=("Region 1.1", "Region 1.1.1", "Region 1.1.2", "Region 1.2.1")
        )

        for document in documents:
            self.assertEqual(is_object_in_scope(self.policy_default, document), True)

    def test_documents_are_not_in_policy_default_scope(self):
        document_lists = [
            Document.objects.exclude(brand_id__in=(1, 3)),
            Document.objects.exclude(desk_id__in=(1,)),
            Document.objects.exclude(document_datetime__range=(pytz.UTC.localize(datetime(2021, 8, 4)),
                                                       pytz.UTC.localize(datetime(2021, 8, 6)))),
            Document.objects.exclude(topics__name__in=("Topic 1.1", "Topic 1.1.1", "Topic 1.1.2", "Topic 1.2.1")),
            Document.objects.exclude(categories__name__in=("Category 1.1", "Category 1.1.1", "Category 1.1.2", "Category 1.2.1")),
            Document.objects.exclude(regions__name__in=("Region 1.1", "Region 1.1.1", "Region 1.1.2", "Region 1.2.1"))
        ]

        for document_list in document_lists:
            for document in document_list:
                self.assertEqual(is_object_in_scope(self.policy_default, document), False)

    def test_documents_filtered_by_user_default(self):
        UserRole.objects.filter(role=self.role_default2).delete()
        RolePolicy.objects.exclude(policy=self.policy_default).delete()

        valid_documents_filter = get_filter_for_valid_objects(self.user_default, Document)
        valid_documents = Document.objects.filter(valid_documents_filter)

        total_valid_documents = valid_documents.count()
        remaining_valid_documents = valid_documents.filter(
            brand_id__in=(1, 3),
            desk_id__in=(1,),
            document_datetime__range=(pytz.UTC.localize(datetime(2021, 8, 4)), pytz.UTC.localize(datetime(2021, 8, 6))),
            topics__name__in=("Topic 1.1", "Topic 1.1.1", "Topic 1.1.2", "Topic 1.2.1"),
            regions__name__in=("Region 1.1", "Region 1.1.1", "Region 1.1.2", "Region 1.2.1")
        ).count()

        self.assertEqual(total_valid_documents, remaining_valid_documents,
                         f"Obtained valid documents ({total_valid_documents}) differs from actual valid documents ({remaining_valid_documents}).")

    def test_documents_listed_by_user_default(self):
        UserRole.objects.filter(role=self.role_default2).delete()
        RolePolicy.objects.exclude(policy=self.policy_default).delete()

        valid_documents = list_valid_objects(self.user_default, Document)

        total_valid_documents = valid_documents.count()
        remaining_valid_documents = valid_documents.filter(
            brand_id__in=(1, 3),
            desk_id__in=(1,),
            document_datetime__range=(pytz.UTC.localize(datetime(2021, 8, 4)), pytz.UTC.localize(datetime(2021, 8, 6))),
            topics__name__in=("Topic 1.1", "Topic 1.1.1", "Topic 1.1.2", "Topic 1.2.1"),
            regions__name__in=("Region 1.1", "Region 1.1.1", "Region 1.1.2", "Region 1.2.1")
        ).count()

        self.assertEqual(total_valid_documents, remaining_valid_documents,
                         f"Obtained valid documents ({total_valid_documents}) differs from actual valid documents ({remaining_valid_documents}).")

    def test_documents_are_in_policy_admin_scope(self):
        documents = Document.objects.filter(
            brand_id__in=(2, 3),
            desk_id__in=(2, 3),
            document_datetime=(pytz.UTC.localize(datetime(2021, 8, 7))),
            topics__name__in=("Topic 1.1.2", "Topic 1.2.2"),
            regions__name__in=("Region 1.1.2", "Region 1.2.2")
        )

        for document in documents:
            self.assertEqual(is_object_in_scope(self.policy_admin, document), True)

    def test_documents_are_not_in_policy_admin_scope(self):
        document_lists = [
            Document.objects.exclude(brand_id__in=(2, 3)),
            Document.objects.exclude(desk_id__in=(2, 3)),
            Document.objects.exclude(document_datetime=(pytz.UTC.localize(datetime(2021, 8, 7)))),
            Document.objects.exclude(topics__name__in=("Topic 1.1.2", "Topic 1.2.2")),
            Document.objects.exclude(regions__name__in=("Region 1.1.2", "Region 1.2.2"))
        ]

        for document_list in document_lists:
            for document in document_list:
                self.assertEqual(is_object_in_scope(self.policy_admin, document), False)

    def test_documents_filtered_by_user_admin(self):
        valid_documents_filter = get_filter_for_valid_objects(self.user_admin, Document)
        valid_documents = Document.objects.filter(valid_documents_filter)

        total_valid_documents = valid_documents.count()
        remaining_valid_documents = valid_documents.filter(
            brand_id__in=(2, 3),
            desk_id__in=(2, 3),
            document_datetime=(pytz.UTC.localize(datetime(2021, 8, 7))),
            topics__name__in=("Topic 1.1.2", "Topic 1.2.2"),
            regions__name__in=("Region 1.1.2", "Region 1.2.2")
        ).count()

        self.assertEqual(total_valid_documents, remaining_valid_documents,
                         f"Obtained valid documents ({total_valid_documents}) differs from actual valid documents ({remaining_valid_documents}).")

    def test_documents_listed_by_user_admin(self):
        valid_documents = list_valid_objects(self.user_admin, Document)

        total_valid_documents = valid_documents.count()
        remaining_valid_documents = valid_documents.filter(
            brand_id__in=(2, 3),
            desk_id__in=(2, 3),
            document_datetime=(pytz.UTC.localize(datetime(2021, 8, 7))),
            topics__name__in=("Topic 1.1.2", "Topic 1.2.2"),
            regions__name__in=("Region 1.1.2", "Region 1.2.2")
        ).count()

        self.assertEqual(total_valid_documents, remaining_valid_documents,
                         f"Obtained valid documents ({total_valid_documents}) differs from actual valid documents ({remaining_valid_documents}).")


    def test_user_default_can_view_brand_1(self):
        self.assertEqual(
            can_user_do(
                "view",
                obj=Brand.objects.get(id=1),
                user=self.user_default
            ),
            True
        )

    def test_user_default_cannot_edit_brand_1(self):
        self.assertEqual(
            can_user_do(
                "edit",
                obj=Brand.objects.get(id=1),
                user=self.user_default
            ),
            False
        )

    def test_user_admin_can_view_brand_2(self):
        self.assertEqual(
            can_user_do(
                "view",
                obj=Brand.objects.get(id=2),
                user=self.user_admin
            ),
            True
        )

    def test_user_admin_can_edit_brand_2(self):
        self.assertEqual(
            can_user_do(
                "edit",
                obj=Brand.objects.get(id=2),
                user=self.user_admin
            ),
            True
        )

    # NOTE: Left for reference, but this is not the desired behaviour anymore
    # def test_incomplete_attribute_query_raises_missing_attributes_validation_error(self):
    #     # consider making the exception more specific
    #     with self.assertRaises(
    #             ValidationError
    #     ):
    #         is_attribute_query_in_scope([], Document, user=self.user_default)

    def test_complete_attribute_query_does_not_raise_missing_attributes_validation_error(self):
        try:
            is_attribute_query_in_scope(
                [
                    self.brand_attribute.get_attribute_value(self.brand_values[1].value),
                    self.brand_attribute.get_attribute_value(self.brand_values[3].value),
                    self.desk_attribute.get_attribute_value(self.desk_values[1].value),
                    self.datetime_attribute.get_attribute_value(self.datetime_values[0].value),
                    self.topic_attribute.get_attribute_value(self.topic_values[2].value),
                    self.topic_attribute.get_attribute_value(self.topic_values[6].value),
                    self.category_attribute.get_attribute_value(self.category_values["Category 1.1"].value),
                    self.category_attribute.get_attribute_value(self.category_values["Category 1.2.1"].value),
                    # self.region_values[2],
                    # self.region_values[6],
                ],
                Document,
                user=self.user_default
            )
            assert True
        except ValidationError: # how to be more specific, we only want to check for missing_attrs validationerror
            assert False