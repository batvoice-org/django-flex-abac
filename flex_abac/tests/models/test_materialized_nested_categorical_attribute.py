from django.test import TestCase
from flex_abac.models import MaterializedNestedCategoricalAttribute,\
    ModelMaterializedNestedCategoricalAttribute
from exampleapp.models import Document
from django.contrib.contenttypes.models import ContentType


class MaterializedNestedCategoricalAttributeTestCase(TestCase):
    def setUp(self):
        doc_content_type = ContentType.objects.get_for_model(Document)
        owner_content_type = ContentType.objects.get_for_model(type(doc_content_type))

        assert(owner_content_type == ContentType.objects.get(
                        app_label='contenttypes',
                        model='contenttype'
                    )
                )

        get = lambda node_id: MaterializedNestedCategoricalAttribute.objects.get(pk=node_id)

        self.region = MaterializedNestedCategoricalAttribute.add_root(
            name='Region'
        )

        self.office = get(self.region.pk).add_child(
            name='Office'
        )

        self.employee = get(self.office.pk).add_child(
            name='Employee'
        )

        for category in (self.region, self.office, self.employee):
            ModelMaterializedNestedCategoricalAttribute.objects.create(
                attribute_type=category,
                owner_content_type=owner_content_type,
                owner_object_id=doc_content_type.id,
                owner_content_object=doc_content_type
            )

    def test_nested_categorical_attribute_is_MP_Node(self):
        assert("depth" in dir(self.region))
        assert("get_children" in dir(self.region))

    def test_created_root_has_correct_structure(self):
        root_node = self.region.get_root()
        self.assertNotEqual(root_node, None)
        self.assertEqual(root_node.get_children().count(), 1)
        self.assertEqual(root_node.get_children()[0].get_children().count(), 1)

    def test_can_get_nested_attributes_from_the_owning_model(self):
        content_type = ContentType.objects.get_for_model(Document)
        nested_categories = MaterializedNestedCategoricalAttribute.objects.filter(
            id__in=ModelMaterializedNestedCategoricalAttribute.objects.filter(
                owner_object_id=content_type.id
            ).values('attribute_type_id')
        )
        self.assertEqual(nested_categories.count(), 3)
