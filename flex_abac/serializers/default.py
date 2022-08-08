import django.db.models

from flex_abac.models import MaterializedNestedCategoricalAttribute, MaterializedNestedCategoricalFilter
from treebeard.models import Node as TreebeardNode

from flex_abac.utils.helpers import get_field_from_lookup_string
from django.db.models import F

from rest_framework import serializers


class BaseValuesSerializer(serializers.Serializer):
    value = serializers.SerializerMethodField()

    class Meta:
        fields = ['value']

    def get_value(self, obj):
        return obj

    @classmethod
    def possible_values(cls, attribute_obj):
        field_name = get_field_from_lookup_string(attribute_obj.get_model(), attribute_obj.field_name)
        return attribute_obj.get_model().objects.annotate(value=F(field_name)).values("value").distinct()

    def get_extra(self, extra_info=None):
        raise NotImplementedError

    def create(self, validated_data):
        return validated_data


class GenericSerializer(BaseValuesSerializer):
    def get_extra(self, extra_info=None):
        attribute_obj = self.context["attribute_obj"]
        extra_fields = attribute_obj.extra_fields
        field_name = attribute_obj.field_name
        if extra_fields:
            annotations = {}
            for name_in_model, pretty_name in extra_fields.items():
                annotations[pretty_name] = F(name_in_model)
            response = attribute_obj.get_model().objects.filter(**{field_name: extra_info}).distinct().values(*extra_fields).annotate(**annotations).values(*annotations.keys())
            if response.exists():
                return response[0]
            else:
                return {}
        else:
            return {}


class CategoricalSerializer(GenericSerializer):
    pass


class NestedCategoricalSerializer(BaseValuesSerializer):
    @classmethod
    def possible_values(cls, attribute_obj):
        return attribute_obj.get_model().objects.annotate(value=F(attribute_obj.field_name)).values("value").distinct()

    def get_extra(self, extra_info=None):
        attribute_obj = self.context["attribute_obj"]
        extra_fields = attribute_obj.extra_fields

        if issubclass(attribute_obj.field_type.model_class(), TreebeardNode):
            node = attribute_obj.field_type.model_class().objects.get(pk=extra_info)
            parent = node.get_parent()

            if extra_fields:
                extra = {}
                for name_in_model, pretty_name in extra_fields.items():
                    extra[f"{pretty_name}"] = getattr(node, name_in_model, None)
                    extra[f"parent__{pretty_name}"] = getattr(parent, name_in_model, None) if parent else None
                return extra
            else:
                return {}
        else:
            field_name = attribute_obj.field_name

            if extra_fields:
                annotations = {}
                value_names = []
                for name_in_model, pretty_name in extra_fields.items():
                    annotations[f"{pretty_name}"] = F(f"{attribute_obj.field_name}__{name_in_model}")
                    annotations[f"{attribute_obj.parent_field_name}__{pretty_name}"] = F(f"{attribute_obj.field_name}__{attribute_obj.parent_field_name}__{name_in_model}")
                    value_names += [
                        f"{attribute_obj.field_name}__{name_in_model}",
                        f"{attribute_obj.field_name}__{attribute_obj.parent_field_name}__{name_in_model}"
                    ]

                response = attribute_obj.get_model().objects.filter(**{field_name: extra_info}).distinct().values(*value_names).annotate(**annotations).values(*annotations.keys())
                if response.exists():
                    return response[0]
                else:
                    return {}
            else:
                return {}


class MaterializedNestedCategoricalSerializer(BaseValuesSerializer):
    @classmethod
    def possible_values(cls, attribute_obj):
        return MaterializedNestedCategoricalFilter.objects.filter(attribute_type=attribute_obj).values("id").annotate(value=F("id")).values("value")

    def get_extra(self, extra_info=None):
        attribute_obj = self.context["attribute_obj"]
        extra_fields = attribute_obj.extra_fields
        node = MaterializedNestedCategoricalFilter.objects.get(id=extra_info)
        parent = node.get_parent()

        if extra_fields:
            extra = {}
            for name_in_model, pretty_name in extra_fields.items():
                extra[f"{pretty_name}"] = getattr(node, name_in_model, None)
                extra[f"parent__{pretty_name}"] = getattr(parent, name_in_model, None) if parent else None

            return extra
        else:
            return {}

