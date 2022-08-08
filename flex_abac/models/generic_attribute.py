from django.db.models import Subquery
from django.contrib.contenttypes.models import ContentType

from .base_attribute import BaseAttribute
from .generic_filter import GenericFilter
from .model_generic_attribute import ModelGenericAttribute
from .policy_generic_filter import PolicyGenericFilter

from django.db.models.query import Q

from rest_framework.exceptions import ValidationError


class GenericAttribute(BaseAttribute):
    """
    Allows creating a model-related attribute of any kind. You will use it with almost everything that can be
    represented by a Django lookup, including the custom ones.

    Examples of valid field names are:

    - ``category__name`` --> field in a foreign model
    - ``id`` --> pk field in the current model
    - ``value`` --> field in the model
    - ``json_data`` --> complex field in the model
    - ``date__range`` --> lookup over a field in the model
    - ``value__gt`` --> lookup over a field in the model
    - ``document__owner__name`` --> field in a foreign model of a foreign model (and as many nested levels as needed)
    - etc.

    Usage example:

    .. code-block:: python

        from django.contrib.contenttypes.models import ContentType
        from flex_abac.models import GenericAttribute, ModelGenericAttribute, GenericFilter

        # Getting the content type
        document_content_type = ContentType.objects.get_for_model(Document)

        # Attribute creation
        datetime_attribute = GenericAttribute.objects.create(
            name="Document date",                                   # user-friendly name
            field_name="document_datetime__range",                  # lookup field name
            serializer="flex_abac.tests.views.test_permissionsview.DatetimeSerializer"    # In this case we are not using the default serializer
        )

        # Assigning the attribute to a model
        ModelGenericAttribute.objects.create(
            attribute_type=datetime_attribute,  # The attribute type
            owner_content_object=document_content_type  # the content type for the Document model
        )

        # Example of creating a filter for this attribute
        GenericFilter.objects.create(
            value=(datetime.now(), datetime.now() + timedelta(days=2)),         # value in the filter, a 2-days range in this case
            attribute_type=datetime_attribute,                                  # The attribute
        )
    """

    def __init__(self, *args, **kwargs):
        self._meta.get_field('serializer').default = "flex_abac.serializers.default.GenericSerializer"
        super(GenericAttribute, self).__init__(*args, **kwargs)

    def delete(self):
        ModelGenericAttribute.objects.filter(attribute_type=self).delete()
        super(GenericAttribute, self).delete()

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
        from flex_abac.serializers import GenericAttributeSerializer, GenericFilterSerializer

        try:
            serializer = GenericAttributeSerializer(data=content)
            serializer.is_valid(raise_exception=True)
            attribute_type = serializer.save()
        except ValidationError as ve:
            if len(ve.detail["name"]) == 1 and ve.detail["name"][0].code == "unique":
                attribute_type = cls.objects.get(name=content["name"])

                serializer = GenericAttributeSerializer(attribute_type, data=content)
                serializer.is_valid(raise_exception=True)
                attribute_type = serializer.save()
                attribute_type.save()
            else:
                raise ve

        if "values" in content.keys():
            for value in content['values']:
                value.update({"attribute_type": attribute_type.id})

                serializer = GenericFilterSerializer(data=value)
                serializer.is_valid(raise_exception=True)
                serializer.save()


    @classmethod
    def get_all_to_check_for_model(cls, model):
        content_type = ContentType.objects.get_for_model(model)
        return GenericAttribute.objects.filter(
            id__in=Subquery(
                ModelGenericAttribute.objects.filter(
                    owner_object_id=content_type.pk
                ).values('attribute_type_id')
            )
        )

    @classmethod
    def get_all_attributes_from_content_types(cls, content_types):
        return cls.objects.filter(
            id__in=Subquery(
                ModelGenericAttribute.objects.filter(
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
        scope_items = policy.get_attribute_values(GenericFilter, PolicyGenericFilter).\
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
        return GenericFilter(
            value=value,
            attribute_type=self,
        )

    def get_model(self):
        model_generic_attribute = ModelGenericAttribute.objects.get(attribute_type=self)

        content_type = ContentType.objects.get(pk=model_generic_attribute.owner_content_object.id)
        return content_type.model_class()

    def get_content_type(self):
        model_generic_attribute = ModelGenericAttribute.objects.get(attribute_type=self)
        return ContentType.objects.get(pk=model_generic_attribute.owner_content_object.id)

    def get_values(self):
        field = self.find_field_in_model(as_path=True)
        model = self.get_model()

        return model.objects.values(field).distinct().order_by(field).values_list(field, flat=True)

    def get_all_values_for_user(self, user, action_name=None):
        user_policy_with_empty_scope = self.is_scope_empty_for_user(GenericFilter, user, action_name)

        if user_policy_with_empty_scope:
            return GenericFilter.objects.filter(attribute_type=self, policies=user_policy_with_empty_scope)
        elif action_name:
            return GenericFilter.objects.filter(policies__roles__users=user,
                                                policies__action__name=action_name,
                                                attribute_type=self)
        else:
            return GenericFilter.objects.filter(policies__roles__users=user, attribute_type=self)

    def __str__(self):
        return '<GenericAttribute:{}>'.format(self.name)