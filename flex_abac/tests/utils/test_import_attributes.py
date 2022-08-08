from django.test import TestCase
from flex_abac.models import (
    GenericAttribute, GenericFilter,
    NestedCategoricalAttribute, NestedCategoricalFilter,
    MaterializedNestedCategoricalAttribute, MaterializedNestedCategoricalFilter,
)

from flex_abac.utils.import_attributes import import_from_yaml
import os


class ImportAttributesTestCase(TestCase):
    def setUp(self):
        self.yaml_path = os.path.join(
            os.path.dirname(__file__),
            '../data/attributes.yaml'
        )

    def test_importing_yaml_file_does_not_raise_exception(self):
        import_from_yaml(self.yaml_path)

    def test_importing_yaml_file_generates_correct_structure_in_db(self):
        import_from_yaml(self.yaml_path)
        brand_name_type = GenericAttribute.objects.get(name="Brand name")
        brand_name_values = GenericFilter.objects.filter(attribute_type=brand_name_type)
        self.assertEqual(brand_name_values.count(), 2)
        self.assertTrue(GenericFilter.objects.get(value="Brand3") in brand_name_values)

        topic_name_type = NestedCategoricalAttribute.objects.get(name="Topic name")
        topic_name_values = NestedCategoricalFilter.objects.filter(attribute_type=topic_name_type)
        self.assertEqual(topic_name_values.count(), 3)
        self.assertTrue(NestedCategoricalFilter.objects.get(value="Topic 1") in topic_name_values)

        region_country_type = MaterializedNestedCategoricalAttribute.objects.get(name="Country")
        region_province_type = MaterializedNestedCategoricalAttribute.objects.get(name="Province")
        region_city_type = MaterializedNestedCategoricalAttribute.objects.get(name="City")

        region_country_values = MaterializedNestedCategoricalFilter.objects.filter(attribute_type=region_country_type)
        region_province_values = MaterializedNestedCategoricalFilter.objects.filter(attribute_type=region_province_type)
        region_city_values = MaterializedNestedCategoricalFilter.objects.filter(attribute_type=region_city_type)

        self.assertEqual(region_country_values.count(), 2)
        self.assertEqual(region_province_values.count(), 4)
        self.assertEqual(region_city_values.count(), 9)

        self.assertTrue(MaterializedNestedCategoricalFilter.objects.get(value="Region 1") in region_country_values)
        self.assertTrue(MaterializedNestedCategoricalFilter.objects.get(value="Region 1.1") in region_province_values)
        self.assertTrue(MaterializedNestedCategoricalFilter.objects.get(value="Region 1.1.1") in region_city_values)

        region_1 = MaterializedNestedCategoricalFilter.objects.get(value="Region 1", attribute_type=region_country_type)
        region_1_1 = MaterializedNestedCategoricalFilter.objects.get(value="Region 1.1", attribute_type=region_province_type)
        region_1_1_1 = MaterializedNestedCategoricalFilter.objects.get(value="Region 1.1.1", attribute_type=region_city_type)

        self.assertTrue(region_1_1.is_child_of(region_1))
        self.assertTrue(region_1_1_1.is_descendant_of(region_1))
        self.assertTrue(region_1_1_1.is_child_of(region_1_1))
