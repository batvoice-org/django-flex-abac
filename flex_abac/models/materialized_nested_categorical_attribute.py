from django.db.models import Subquery
from treebeard.mp_tree import MP_Node
from flex_abac.utils.treebeard import print_node
from treebeard.exceptions import NodeAlreadySaved
from .base_attribute import BaseAttribute
from .model_materialized_nested_categorical_attribute import ModelMaterializedNestedCategoricalAttribute
from .item_materialized_nested_categorical_filter import ItemMaterializedNestedCategoricalFilter
from .materialized_nested_categorical_filter import MaterializedNestedCategoricalFilter
from .policy_materialized_nested_categorical_filter import PolicyMaterializedNestedCategoricalFilter
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db.models.query import Q

from django.core.exceptions import FieldDoesNotExist

from rest_framework.exceptions import ValidationError


class MaterializedNestedCategoricalAttribute(BaseAttribute, MP_Node):
    """
    A special case of a nested categorical attribute, in which trees have a predefined structure (that is, each level in
    the tree corresponds at the same to a category). An example of this could be a location, which can be categorized
    inside a country, region, city, street, etc.

    Usage example:

    .. code-block:: python

        # Example of the nested model which we will be using
        class Region(models.Model):
            name = models.CharField(max_length=3000, default="", blank=True)
            parent = models.ForeignKey("self", on_delete=models.CASCADE, default=None, null=True, blank=True)

            ...

        # In the document model...
        class Document(models.Model):
            ...
            regions = models.ManyToManyField('region', through='documentregions')
            ...

        from django.contrib.contenttypes.models import ContentType
        from flex_abac.models import (
            MaterializedNestedCategoricalAttribute,
            MaterializedModelNestedCategoricalAttribute,
            MaterializedNestedCategoricalFilter
        )

                category_attribute = NestedCategoricalAttribute.objects.\\
                            create(name="Document Category",        # User-friendly name
                                   field_type=ContentType.objects.get_for_model(NestedCategory), # Contenttype of the nested model
                                   field_name="category",           # Field name in the base model
                                   nested_field_name="id",          # category field user-friendly name in the nested model.
                                   parent_field_name="parent",      # parent field in the nested model.
                                   extra_fields={                   # Used by the default serializer to show the fields of interest in the foreign model
                                       'id': 'id',                  # Key: field from the point of view of the base model; value: the field name after serialization which will be provided.
                                       'name': 'name',
                                   })

        # Attributes creation (one per each predefined level: country, province, city).

        # Country attribute
        region_country_attribute = MaterializedNestedCategoricalAttribute.\\
                                            add_root(                  # Adding as root node
                                                name='Country',        # User-friendly name
                                                extra_fields={         # Used by the default serializer to show the fields of interest in the foreign model
                                                    'id': 'id',        # Key: field from the point of view of the base model; value: the field name after serialization which will be provided.
                                                    'value': 'name',
                                                })

        # Province attribute
        region_province_attribute = region_country_attribute.\\
                                            add_child(                  # Adding as a child of the country
                                                name='Province',
                                                extra_fields={
                                                    'id': 'id',
                                                    'value': 'name',
                                                })

        # City attribute
        region_city_attribute = region_province_attribute.\\
                                            add_child(                  # Adding as a child of the province
                                                name='City',
                                                      extra_fields={
                                                          'id': 'id',
                                                          'value': 'name',
                                                      })

        # For convenience
        attribute_region_levels = [region_country_attribute, region_province_attribute, region_city_attribute]

        # Assigning the attributes to a model
        for tree_level in attribute_region_levels:
            ModelMaterializedNestedCategoricalAttribute.objects.create(
                attribute_type=tree_level,                  # The attribute type
                owner_content_object=document_content_type  # the content type for the Document model
            )

        # Example of creating a filter for this attribute
        # In this example, all the values in the Region table are listed and introduced as a filter, but there are many
        # other ways to insert the data. Showing this as an example of how this could be automated.

        def add_values_for_regions(attribute_region_levels):
            region_values = {}

            # attribute_region_levels is listed in depth order, just one item per level, so in this case we can take
            # advantage of this
            last_level = Region.objects.filter(parent=None)
            depth = 0

            while last_level.exists():
                for region in last_level:

                    # First level, adding a rot node
                    if not region.parent:
                        region_values[region.pk] = MaterializedNestedCategoricalFilter.add_root(
                            value=region.name,
                            attribute_type=attribute_region_levels[depth]
                        )
                    else:   # Nested level
                        region_values[region.pk] = region_values[region.parent.pk].add_child(
                            value=region.name,
                            attribute_type=attribute_region_levels[depth]
                        )

                    # We need to create an additional ItemMaterializedNestedCategoricalFilter
                    related_documents = Documentregions.objects.filter(region=region.pk)
                    for documentregion in related_documents:
                        ItemMaterializedNestedCategoricalFilter.objects.create(
                            value=region_values[region.pk],
                            owner_content_object=documentregion.document,
                        )

                last_level = Region.objects.filter(parent__in=last_level)
                depth += 1

    """

    def __init__(self, *args, **kwargs):
        self._meta.get_field('serializer').default = "flex_abac.serializers.default.MaterializedNestedCategoricalSerializer"
        super(MaterializedNestedCategoricalAttribute, self).__init__(*args, **kwargs)

    def delete(self):
        ModelMaterializedNestedCategoricalAttribute.objects.filter(attribute_type=self).delete()
        super(MaterializedNestedCategoricalAttribute, self).delete()

    @classmethod
    def print_all(cls):
        for attr in MaterializedNestedCategoricalAttribute.objects.filter(depth=1):
            print_node(attr, "name")

    @classmethod
    def import_from_dict(cls, content: dict):

        # Imported inside the function to avoid circular imports, also not needed in the rest of functions
        from flex_abac.serializers import MaterializedNestedCategoricalAttributeSerializer, MaterializedNestedCategoricalFilterSerializer

        def _import_types(nested_type, class_name=None, parent=None):
            if parent:
                nested_type.update({
                    "parent": parent,
                    "class_name": class_name
                })
            else:
                class_name = nested_type["class_name"]

            try:
                serializer = MaterializedNestedCategoricalAttributeSerializer(data=nested_type)
                serializer.is_valid(raise_exception=True)
                attribute_type = serializer.save()
            except ValidationError as ve:
                if len(ve.detail["name"]) == 1 and ve.detail["name"][0].code == "unique":
                    attribute_type = MaterializedNestedCategoricalAttribute.objects.get(name=nested_type["name"])

                    serializer = MaterializedNestedCategoricalAttributeSerializer(attribute_type, data=nested_type)
                    serializer.is_valid(raise_exception=True)
                    attribute_type = serializer.save()
                    attribute_type.save()
                else:
                    raise ve

            if "children" in nested_type.keys():
                for child in nested_type["children"]:
                    _import_types(nested_type=child,
                                  class_name=class_name,
                                  parent=attribute_type)

        def _import_values(nested_value, parent=None):
            if parent:
                nested_value.update({"parent": parent})
            nested_value.update({"attribute_type": MaterializedNestedCategoricalAttribute.objects.get(name=nested_value["type"]).id})

            serializer = MaterializedNestedCategoricalFilterSerializer(data=nested_value)
            serializer.is_valid(raise_exception=True)
            attribute_value = serializer.save()

            if "children" in nested_value.keys():
                for child in nested_value["children"]:
                    _import_values(child, parent=attribute_value)

        _import_types(content['types'])
        if "values" in content['types'].keys():
            for v in content['types']['values']:
                _import_values(v)


    @classmethod
    def get_all_to_check_for_model(cls, model):
        content_type = ContentType.objects.get_for_model(model)
        return cls.objects.filter(
            id__in=Subquery(
                ModelMaterializedNestedCategoricalAttribute.objects.filter(
                    owner_object_id=content_type.pk
                ).values('attribute_type_id')
            ),
            numchild=0  # checking leaf attributes only, non-leaf attributes will be handled by their leaf descendants
        )


    @classmethod
    def get_all_attributes_from_content_types(cls, content_types):
        return cls.objects.filter(
            id__in=Subquery(
                ModelMaterializedNestedCategoricalAttribute.objects.filter(
                    owner_object_id__in=content_types
                ).values('attribute_type_id')
            )  # checking leaf attributes only, non-leaf attributes will be handled by their leaf descendants
        )

    def is_represented_in_query_values(self, query_attribute_values):
        query_attribute_types = [v.attribute_type for v in query_attribute_values]
        is_covered = False
        for query_attribute_type in query_attribute_types:
            try:
                _ = query_attribute_type.depth
                if query_attribute_type == self or self in query_attribute_type.get_descendants():
                    is_covered = True
                    break
                else:
                    pass
            except AttributeError:
                # query attribute type is not nested, ignoring
                pass

        return is_covered

    def get_filter(self, policy):
        scope_items = policy.get_attribute_values(MaterializedNestedCategoricalFilter, PolicyMaterializedNestedCategoricalFilter).\
            filter(attribute_type__field_name=self.field_name, attribute_type=self)

        all_values_fields = []
        if not scope_items.exists():
            all_values_fields = [self.field_name]

        return Q(**{"pk__in": ItemMaterializedNestedCategoricalFilter.objects.filter(value__in=scope_items.values("id")).
                 values("owner_object_id")}), all_values_fields

    def does_match(self, obj, policy):
        MaterializedNestedCategoricalFilter = apps.get_model(
            "flex_abac",
            "materializednestedcategoricalFilter"
        )
        object_values = MaterializedNestedCategoricalFilter.objects.filter(
            attribute_type=self,
            id__in=Subquery(
                ItemMaterializedNestedCategoricalFilter.objects.filter(
                    owner_content_type=ContentType.objects.get_for_model(type(obj)),
                    owner_object_id=obj.id
                ).values('value_id')
            )
        )
        if not object_values.count():
            return False

        PolicyMaterializedNestedCategoricalFilter = apps.get_model(
            "flex_abac",
            "policymaterializednestedcategoricalFilter"
        )

        nested_categorical_values = policy.get_attribute_values(
            MaterializedNestedCategoricalFilter,
            PolicyMaterializedNestedCategoricalFilter
        )

        matching_scope_values = nested_categorical_values.filter(
            id__in=Subquery(object_values.values('id'))
        )

        direct_match = matching_scope_values.count() > 0

        ancestor_match = False

        if not direct_match:
            for object_value in object_values:
                matching_ancestor_scope_values = nested_categorical_values.filter(
                    id__in=Subquery(object_value.get_ancestors().values('id'))
                )
                if matching_ancestor_scope_values.count() > 0:
                    ancestor_match = True
                    break

        if not direct_match and not ancestor_match:
            return False

        return True

    def get_content_type(self):
        model_generic_attribute = ModelMaterializedNestedCategoricalAttribute.objects.get(attribute_type=self)
        return ContentType.objects.get(pk=model_generic_attribute.owner_content_object.id)

    def find_field_in_model(self, as_path=True):
        if as_path:
            return self.field_name
        else:
            return "MaterializedNestedCategoricalAttribute"

    def get_values(self):
        return self.get_tree().values("values").distinct().order_by("values").values_list("values", flat=True)

    def get_parent_from_id(self, node_id):
        return MaterializedNestedCategoricalFilter.objects.get(id=node_id).get_parent()

    def get_attribute_type(self, node_id):
        return MaterializedNestedCategoricalFilter.objects.get(id=node_id).attribute_type

    def get_all_values_for_user(self, user, action_name=None):
        user_policy_with_empty_scope = self.is_scope_empty_for_user(MaterializedNestedCategoricalFilter, user, action_name)

        if user_policy_with_empty_scope:
            return MaterializedNestedCategoricalFilter.objects.filter(attribute_type=self, policies=user_policy_with_empty_scope)
        elif action_name:
            return MaterializedNestedCategoricalFilter.objects.filter(policies__roles__users=user,
                                                                      policies__action__name=action_name,
                                                                      attribute_type=self)
        else:
            return MaterializedNestedCategoricalFilter.objects.filter(policies__roles__users=user, attribute_type=self)

    def __str__(self):
        return '<MaterializedNestedCategoricalAttribute:{}>'.format(self.name)

