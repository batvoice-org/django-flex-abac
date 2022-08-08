from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Subquery
from django.db.models.query import Q
from flex_abac.utils.treebeard import print_node
from rest_framework.exceptions import ValidationError
from treebeard.models import Node as TreebeardNode

from .base_attribute import BaseAttribute
from .model_nested_categorical_attribute import ModelNestedCategoricalAttribute
from .nested_categorical_filter import NestedCategoricalFilter
from .policy_nested_categorical_filter import PolicyNestedCategoricalFilter


class NestedCategoricalAttribute(BaseAttribute):
    """
    A special case of a categorical attribute in which values are nested in a tree. That means that if the filter is
    applied over a value that is in the upper levels of the tree, any value which is nested from that value will be
    also allowed by the policy. This kind of attribute corresponds to a foreign table which is a field that contains the
    name of the category, and another one indicating the parent (adjacency list representation of a tree).

    Usage example:

    .. code-block:: python

        # Example of the nested model which we will be using
        class NestedCategory(models.Model):
            name = models.CharField(max_length=3000, default="", blank=True)
            parent = models.ForeignKey("self", on_delete=models.CASCADE, default=None, null=True, blank=True)

            ...


        from django.contrib.contenttypes.models import ContentType
        from flex_abac.models import NestedCategoricalAttribute, ModelNestedCategoricalAttribute, NestedCategoricalFilter

        # Attribute creation
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

        # Assigning the attribute to a model
        ModelNestedCategoricalAttribute.objects.create(
            attribute_type=category_attribute,          # The attribute type
            owner_content_object=document_content_type  # the content type for the Document model
        )

        # Example of creating a filter for this attribute
        NestedCategoricalFilter.objects.create(
            value=NestedCategory.objects.get(name="NestedCategory1.2.1").id,
            attribute_type=category_attribute,
        )

    **Special case: TreeBeard-based nested fields**

    For the sake of performance in models with a big number of elements in the tree, it is also possible to use models
    which are represented through the Treebeard library.

    For instance, if we wanted to create a Materialized Path Tree
    (https://django-treebeard.readthedocs.io/en/latest/mp_tree.html), the ``NestedCategory`` model we created before
    will be defined as follows:

    .. code-block:: python

        from treebeard.mp_tree import MP_Node

        class NestedCategory(MP_Node):
                name = models.CharField(max_length=3000, default="", blank=True)
                parent = models.ForeignKey("self", on_delete=models.CASCADE, default=None, null=True, blank=True)

                ...

    Attribute definition and filters creation will remain the same. You can create your categories are explained in the
    Treebeard library documentation without any additional considerations.

        .. code-block:: python

            cat1 = NestedCategory.add_root(name='Cat1')    # Adding as root node
            cat1_1 = cat1.add_child(name='Cat1.1')    # Adding as a child of Cat1
            cat1_2 = cat1.add_child(name='Cat1.2')    # Adding as a child of Cat1

            cat1_1_1 = cat1_1.add_child(name='Cat1.1.1')    # Adding as a child of Cat1.1
    """
    nested_field_name = models.CharField(max_length=512, null=False)
    parent_field_name = models.CharField(max_length=512, null=False)
    field_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        self._meta.get_field('serializer').default = "flex_abac.serializers.default.NestedCategoricalSerializer"
        super(NestedCategoricalAttribute, self).__init__(*args, **kwargs)

    def delete(self):
        ModelNestedCategoricalAttribute.objects.filter(attribute_type=self).delete()
        super(NestedCategoricalAttribute, self).delete()

    @classmethod
    def print_all(cls):
        for attr in NestedCategoricalAttribute.objects.filter(depth=1):
            print_node(attr, "name")

    @classmethod
    def import_from_dict(cls, content: dict):
        # Imported inside the function to avoid circular imports, also not needed in the rest of functions
        from flex_abac.serializers import NestedCategoricalAttributeSerializer, NestedCategoricalFilterSerializer

        try:
            serializer = NestedCategoricalAttributeSerializer(data=content)
            serializer.is_valid(raise_exception=True)
            attribute_type = serializer.save()
        except ValidationError as ve:
            if len(ve.detail["name"]) == 1 and ve.detail["name"][0].code == "unique":
                attribute_type = NestedCategoricalAttribute.objects.get(name=content["name"])

                serializer = NestedCategoricalAttributeSerializer(attribute_type, data=content)
                serializer.is_valid(raise_exception=True)
                attribute_type = serializer.save()
                attribute_type.save()
            else:
                raise ve

        if "values" in content.keys():
            for value in content['values']:
                value.update({"attribute_type": attribute_type.id})

                serializer = NestedCategoricalFilterSerializer(data=value)
                serializer.is_valid(raise_exception=True)
                serializer.save()


    @classmethod
    def get_all_to_check_for_model(cls, model):
        content_type = ContentType.objects.get_for_model(model)
        return cls.objects.filter(
            id__in=Subquery(
                ModelNestedCategoricalAttribute.objects.filter(
                    owner_object_id=content_type.pk
                ).values('attribute_type_id')
            )
        )

    @classmethod
    def get_all_attributes_from_content_types(cls, content_types):
        return cls.objects.filter(
            id__in=Subquery(
                ModelNestedCategoricalAttribute.objects.filter(
                    owner_object_id__in=content_types
                ).values('attribute_type_id')
            )
        )

    def is_represented_in_query_values(self, query_attribute_values):
        query_attribute_types = [v.attribute_type for v in query_attribute_values]
        is_covered = False
        for query_attribute_type in query_attribute_types:
            if query_attribute_type == self:
                is_covered = True
                break
        return is_covered

    def get_filter(self, policy):
        scope_items = policy.get_attribute_values(NestedCategoricalFilter, PolicyNestedCategoricalFilter).\
                filter(attribute_type__field_name=self.field_name,
                       attribute_type__nested_field_name=self.nested_field_name,
                       attribute_type__parent_field_name=self.parent_field_name,
                       attribute_type=self
                       )

        all_values_fields = []
        if not scope_items.exists():
            all_values_fields = [self.field_name]

        # Special case: Treebeard node (including Materialized path, nested sets of adjacency lists)
        if issubclass(self.field_type.model_class(), TreebeardNode):
            or_filter = Q()
            for item in scope_items.values_list("value", flat=True):
                item_obj = self.field_type.model_class().objects.filter(**{self.nested_field_name: item}).first()
                or_filter |= Q(**{f"{self.field_name}__in": self.field_type.model_class().get_tree(item_obj)})

            return or_filter, all_values_fields
        else:
            queryset = self.field_type.model_class().objects

            last_level = queryset.filter(**{f"{self.nested_field_name}__in": list(scope_items.values_list("value", flat=True))})

            # Caution: If more than one field with the same field name (including lookup) is provided, it will perform as
            # an OR (that is, if it is accepted by one of them, it will be accepted even if it is not fulfilled for others)
            or_filter = Q()
            while last_level.exists():
                or_filter |= Q(**{f"{self.field_name}__pk__in": last_level})
                last_level = queryset.filter(**{f"{self.parent_field_name}__in": last_level})

        return or_filter, all_values_fields

    def does_match(self, obj, policy):
        queryset = type(obj).objects.filter(pk=obj.pk)

        or_filter, _ = self.get_filter(policy)

        return queryset.filter(or_filter).exists()

    def get_attribute_value(self, value):
        return NestedCategoricalFilter(
            value=value,
            attribute_type=self,
        )

    def get_content_type(self):
        model_generic_attribute = ModelNestedCategoricalAttribute.objects.get(attribute_type=self)
        return ContentType.objects.get(pk=model_generic_attribute.owner_content_object.id)


    def get_values(self):
        field_path = self.find_field_in_model(as_path=True)
        model = self.get_model()

        return model.objects.values(field_path).distinct().order_by(field_path).values_list(field_path, flat=True)

    def get_all_values_for_user(self, user, action_name=None):
        user_policy_with_empty_scope = self.is_scope_empty_for_user(NestedCategoricalFilter, user,
                                                                    action_name)

        if user_policy_with_empty_scope:
            return NestedCategoricalFilter.objects.filter(attribute_type=self,
                                                                      policies=user_policy_with_empty_scope)
        elif action_name:
            return NestedCategoricalFilter.objects.filter(policies__roles__users=user,
                                                          policies__action__name=action_name,
                                                          attribute_type=self)
        else:
            return NestedCategoricalFilter.objects.filter(policies__roles__users=user, attribute_type=self)

    def __str__(self):
        return '<NestedCategoricalAttribute:{}>'.format(self.name)
