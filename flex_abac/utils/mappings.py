import re
import functools

from django.db import connection

from django.core.exceptions import ValidationError, SuspiciousOperation

from flex_abac.models import BaseAttribute
from flex_abac.utils.helpers import get_model_and_field_from_lookup_string
from flex_abac.utils.action_names import get_action_name
from flex_abac.checkers import get_filter_for_valid_objects

class AttributeMappingGenerator(object):
    @classmethod
    def get_attribute_mapping(cls, view):
        raise NotImplementedError

class DefaultAttributeMappingGenerator(AttributeMappingGenerator):

    aliases = {}

    @classmethod
    def get_attribute_mapping(cls, view):

        action_name = get_action_name(view)
        valid_objects_filter = get_filter_for_valid_objects(view.request.user, BaseAttribute,
                                                            action_name=action_name)
        attribute_types = BaseAttribute.objects.filter(valid_objects_filter)

        mappings = []
        for attribute_type in attribute_types:
            base_model_name = attribute_type.get_model()
            model_name, field_name = get_model_and_field_from_lookup_string(base_model_name, attribute_type.field_name)

            cast_function = model_name._meta.get_field(field_name).to_python

            current_field_name = attribute_type.field_name
            if current_field_name in cls.aliases.keys():
                current_field_name = cls.aliases[current_field_name]

            if view.request.GET.getlist(current_field_name):
                mappings.append(MappingItem(obj_type=base_model_name, field_name=attribute_type.field_name,
                                            values_type=cast_function,
                                            function_value=functools.partial(
                                                    lambda view, field_name: view.request.GET.getlist(field_name),
                                                field_name=current_field_name)))

        return mappings

class MappingItem:
    def __init__(self, obj_type, field_name, values_type, function_value):
        self.obj_type = obj_type
        self.field_name = field_name
        self.values_type = values_type
        self.function_value = function_value

    def get_item_value(self, view):
        try:
            return list(map(self.values_type, self.function_value(view)))
        except ValidationError as ve:
            raise SuspiciousOperation(repr(ve))

    def __str__(self):
        return f"{self.obj_type} {self.field_name} {self.function_value}"


def get_mapping_from_viewset(view):
    # Checks the get_attribute_mapping has been defined
    get_attribute_mapping_func = getattr(view, "get_attribute_mapping", None)

    if "attribute_mapping" in view.kwargs.keys():
        attribute_mapping_items = view.kwargs["attribute_mapping"]
    elif getattr(view, "attribute_mapping", None):
        attribute_mapping_items = view.attribute_mapping
    elif callable(get_attribute_mapping_func):
        attribute_mapping_items = view.get_attribute_mapping()
    else:
        attribute_mapping_items = DefaultAttributeMappingGenerator()

    if isinstance(attribute_mapping_items, AttributeMappingGenerator):
        attribute_mapping_items = attribute_mapping_items.get_attribute_mapping(view)

    if not attribute_mapping_items:
        return None

    # Renders items into values
    attribute_mapping = {}
    for item in attribute_mapping_items:
        if not item.obj_type in attribute_mapping.keys():
            attribute_mapping[item.obj_type] = {}

        attribute_mapping[item.obj_type][item.field_name] = item.get_item_value(view)

    return attribute_mapping
