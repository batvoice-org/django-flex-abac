from django.db.models import Subquery
from django.contrib.contenttypes.models import ContentType

from .base_attribute import BaseAttribute
from .categorical_filter import CategoricalFilter
from .model_categorical_attribute import ModelCategoricalAttribute
from .policy_categorical_filter import PolicyCategoricalFilter

from django.db.models.query import Q

from rest_framework.exceptions import ValidationError


class CategoricalAttribute(BaseAttribute):
    """
    A special case of the ``GenericAttribute`` meant for foreign keys to  categories. Usually, the referenced foreign
    model will have at least a field which is the name of the category.

    Usage example:

    .. code-block:: python

        from django.contrib.contenttypes.models import ContentType
        from flex_abac.models import CategoricalAttribute, ModelCategoricalAttribute, CategoricalFilter

        # Attribute creation
        category_attribute = CategoricalAttribute.objects.create(
            name="Document Category",       # User-friendly name
            field_name="category",          # Field name in the base model
            extra_fields={                  # Used by the default serializer to show the fields of interest in the foreign model
                "category__id": "id",           # Key: field from the point of view of the base model; value: the field name after serialization which will be provided.
                "category__name": "category"
            }
        )

        # Assigning the attribute to a model
        ModelCategoricalAttribute.objects.create(
            attribute_type=category_attribute,          # The attribute type
            owner_content_object=document_content_type  # the content type for the Document model
        )

        # Example of creating a filter for this attribute
        CategoricalFilter.objects.create(
            value=Category.objects.get(name="Category1").id,    # The value, in this case the pk of a Category instance
            attribute_type=category_attribute,                  # The attribute type
        )
    """

    def __init__(self, *args, **kwargs):
        self._meta.get_field('serializer').default = "flex_abac.serializers.default.CategoricalSerializer"
        super(CategoricalAttribute, self).__init__(*args, **kwargs)

    def delete(self):
        ModelCategoricalAttribute.objects.filter(attribute_type=self).delete()
        super(CategoricalAttribute, self).delete()

    @classmethod
    def print_all(cls):
        for attr in cls.objects.all():
            print("-", attr.name)

    @classmethod
    def import_from_dict(cls, content: dict):
        """
        i.e.:
         content = {
            'name': 'Brand name',
            'field_name': 'brand__name',
            'class_name': 'exampleapp.document',
            'values': [
                {'value': 'Brand1'},
                {'value': 'Brand2'}]
         }
        """

        # Imported inside the function to avoid circular imports, also not needed in the rest of functions
        from flex_abac.serializers import CategoricalAttributeSerializer, CategoricalFilterSerializer

        try:
            serializer = CategoricalAttributeSerializer(data=content)
            serializer.is_valid(raise_exception=True)
            attribute_type = serializer.save()
        except ValidationError as ve:
            if len(ve.detail["name"]) == 1 and ve.detail["name"][0].code == "unique":
                attribute_type = cls.objects.get(name=content["name"])

                serializer = CategoricalAttributeSerializer(attribute_type, data=content)
                serializer.is_valid(raise_exception=True)
                attribute_type = serializer.save()
                attribute_type.save()
            else:
                raise ve

        if "values" in content.keys():
            for value in content['values']:
                value.update({"attribute_type": attribute_type.id})

                serializer = CategoricalFilterSerializer(data=value)
                serializer.is_valid(raise_exception=True)
                serializer.save()


    @classmethod
    def get_all_to_check_for_model(cls, model):
        content_type = ContentType.objects.get_for_model(model)
        return CategoricalAttribute.objects.filter(
            id__in=Subquery(
                ModelCategoricalAttribute.objects.filter(
                    owner_object_id=content_type.pk
                ).values('attribute_type_id')
            )
        )

    @classmethod
    def get_all_attributes_from_content_types(cls, content_types):
        return cls.objects.filter(
            id__in=Subquery(
                ModelCategoricalAttribute.objects.filter(
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
        scope_items = policy.get_attribute_values(CategoricalFilter, PolicyCategoricalFilter).\
            filter(attribute_type__field_name=self.field_name, attribute_type=self)

        all_values_fields = []
        if not scope_items.exists():
            all_values_fields = [self.field_name]

        # Caution: If more than one field with the same field name (including lookup) is provided, it will perform as
        # an OR (that is, if it is accepted by one of them, it will be accepted even if it is not fulfilled for others)
        or_filter = Q()

        for scope in scope_items.values_list("value", flat=True):
            match_filter = {
                self.field_name: scope
            }
            or_filter |= Q(**match_filter)

        return or_filter, all_values_fields

    def does_match(self, obj, policy):
        queryset = type(obj).objects.filter(pk=obj.pk)

        or_filter, _ = self.get_filter(policy)

        return queryset.filter(or_filter).exists()

    def get_attribute_value(self, value):
        return CategoricalFilter(
            value=value,
            attribute_type=self,
        )

    def get_model(self):
        model_categorical_attribute = ModelCategoricalAttribute.objects.get(attribute_type=self)

        content_type = ContentType.objects.get(pk=model_categorical_attribute.owner_content_object.id)
        return content_type.model_class()

    def get_content_type(self):
        model_categorical_attribute = ModelCategoricalAttribute.objects.get(attribute_type=self)
        return ContentType.objects.get(pk=model_categorical_attribute.owner_content_object.id)

    def get_values(self):
        field = self.find_field_in_model(as_path=True)
        model = self.get_model()

        return model.objects.values(field).distinct().order_by(field).values_list(field, flat=True)

    def get_all_values_for_user(self, user, action_name=None):
        user_policy_with_empty_scope = self.is_scope_empty_for_user(CategoricalFilter, user, action_name)

        if user_policy_with_empty_scope:
            return CategoricalFilter.objects.filter(attribute_type=self, policies=user_policy_with_empty_scope)
        elif action_name:
            return CategoricalFilter.objects.filter(policies__roles__users=user,
                                                    policies__action__name=action_name,
                                                    attribute_type=self)
        else:
            return CategoricalFilter.objects.filter(policies__roles__users=user, attribute_type=self)

    def __str__(self):
        return '<CategoricalAttribute:{}>'.format(self.name)