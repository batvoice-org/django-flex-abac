from django.test import TestCase
from flex_abac.models import MaterializedNestedCategoricalFilter,\
    MaterializedNestedCategoricalAttribute, ModelMaterializedNestedCategoricalAttribute,\
    ItemMaterializedNestedCategoricalFilter
from exampleapp.models import Document, Brand, Desk
# from flex_abac.factories.documentfactory import DocumentFactory
from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError

from django.db.models import Subquery


class MaterializedNestedCategoricalFilterTestCase(TestCase):
    def setUp(self):
        brand = Brand.objects.create(name="brand1")
        desk = Desk.objects.create(name="desk1")
        self.doc1 = Document.objects.create(filename="doc1",
                                            brand=brand,
                                            desk=desk)
        doc_content_type = ContentType.objects.get_for_model(Document)
        owner_content_type = ContentType.objects.get_for_model(type(doc_content_type))

        assert (doc_content_type == ContentType.objects.get(
            app_label='exampleapp',
            model='document'
        )
                )

        assert (owner_content_type == ContentType.objects.get(
            app_label='contenttypes',
            model='contenttype'
        )
                )

        get = lambda node_id: MaterializedNestedCategoricalAttribute.objects.get(pk=node_id)

        self.country = MaterializedNestedCategoricalAttribute.add_root(
            name='Country'
        )

        self.office = get(self.country.pk).add_child(
            name='Office'
        )

        self.employee = get(self.office.pk).add_child(
            name='Employee'
        )

        for category in (self.country, self.office, self.employee):
            ModelMaterializedNestedCategoricalAttribute.objects.create(
                attribute_type=category,
                owner_content_type=owner_content_type,
                owner_object_id=doc_content_type.id,
                owner_content_object=doc_content_type
            )

        get = lambda node_id: MaterializedNestedCategoricalFilter.objects.get(pk=node_id)
        self.portugal = MaterializedNestedCategoricalFilter.add_root(
            value="Portugal",
            attribute_type=self.country
        )

        self.france = MaterializedNestedCategoricalFilter.add_root(
            value="France",
            attribute_type=self.country
        )

        self.paris_office = get(self.france.pk).add_child(
            value="Paris office",
            attribute_type=self.office
        )

        self.employee_1_paris = get(self.paris_office.pk).add_child(
            value="Employee 1 (Paris)",
            attribute_type=self.employee
        )

        self.employee_2_paris = get(self.paris_office.pk).add_child(
            value="Employee 2 (Paris)",
            attribute_type=self.employee
        )

        self.lyon_office = get(self.france.pk).add_child(
            value="Lyon office",
            attribute_type=self.office
        )

    def test_employee_1_is_a_descendant_of_france(self):
        self.employee_1_paris.is_descendant_of(self.france)

    def test_creating_a_child_value_that_breaks_the_attribute_structure_raises_validation_error(self):
        with self.assertRaises(
                ValidationError,
                msg='value hierarchy does not match attribute hierarchy'
        ):
            self.paris_office.add_child(
                value="Employee 3 (Paris)",
                attribute_type=self.office
            )




