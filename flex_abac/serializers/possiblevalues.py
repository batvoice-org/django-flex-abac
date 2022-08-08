from rest_polymorphic.serializers import PolymorphicSerializer

from flex_abac.models import (
    BaseAttribute,
    GenericAttribute,
    CategoricalAttribute,
    ModelGenericAttribute,
    NestedCategoricalAttribute,
    MaterializedNestedCategoricalAttribute
)

from flex_abac.serializers.utils import (
    serialize_from_serializer_path, object_from_serializer_path, WritableSerializerMethodField
)

from flex_abac.serializers import GenericFilterSerializer, PolymorphicAttributeTypeSerializer


from rest_framework import serializers

from flex_abac.serializers.utils import serialize_from_serializer_path, get_serializer_class


class AttributePossibleValuesSerializer(serializers.Serializer):
    possible_values = serializers.SerializerMethodField()
    field_type = serializers.SerializerMethodField()

    class Meta:
        model = BaseAttribute
        fields = ['id', 'name', 'field_type', 'possible_values']

    def get_field_type(self, value_obj, **kwargs):
        internal_type = value_obj.find_field_in_model(as_path=False)
        return internal_type

    def get_possible_values(self, attribute_obj, resource_type, look_for_parent=False, **kwargs):
        values = attribute_obj.get_values()
        if attribute_obj.serializer:
            serializer_class = get_serializer_class(attribute_obj.serializer)
            if hasattr(serializer_class, "possible_values"):
                values = serializer_class.possible_values(attribute_obj)

        filter_values = []
        for value in values:
            extra = None
            parent = None
            if attribute_obj.serializer:
                serializer = serialize_from_serializer_path(attribute_obj.serializer, value["value"], many=False)
                serializer.context["attribute_obj"] = attribute_obj
                if hasattr(serializer_class, "get_extra"):
                    serializer.fields.update({"extra": serializers.SerializerMethodField()})

                processed_value = serializer.data

                if "extra" in processed_value.keys():
                    extra = processed_value.pop("extra")
                elif hasattr(serializer_class, "get_extra") and not value["value"]:
                    # In case the value is None, the get_extra field won't be called automatically
                    extra = serializer.get_extra(extra_info=None)

                if "parent" in value.keys():
                    parent = value["parent"]

                processed_value = processed_value["value"] if processed_value else None
            else:
                processed_value = value

            if isinstance(attribute_obj, MaterializedNestedCategoricalAttribute):
                parent = attribute_obj.get_parent_from_id(processed_value)
                parent = parent.id if parent else None

                attribute_type = attribute_obj.get_attribute_type(processed_value)
                attribute_type = PolymorphicAttributeTypeSerializer(attribute_type, many=False).data
            else:
                attribute_type = PolymorphicAttributeTypeSerializer(attribute_obj, many=False).data

            filter_value = {
                "value": processed_value,
                "extra": extra,
                "attribute_type": dict(attribute_type),
                "resourcetype": resource_type,
            }

            if parent:
                filter_value.update({"parent": parent})

            filter_values.append(filter_value)

        return filter_values


class GenericPossibleValuesSerializer(AttributePossibleValuesSerializer):
    class Meta(AttributePossibleValuesSerializer.Meta):
        model = GenericAttribute

    def get_possible_values(self, attribute_obj, **kwargs):
        return super().get_possible_values(attribute_obj, resource_type="GenericFilter", **kwargs)


class CategoricalPossibleValuesSerializer(AttributePossibleValuesSerializer):
    class Meta(AttributePossibleValuesSerializer.Meta):
        model = CategoricalAttribute

    def get_possible_values(self, attribute_obj, **kwargs):
        return super().get_possible_values(attribute_obj, resource_type="CategoricalFilter", **kwargs)


class NestedCategoricalPossibleValuesSerializer(AttributePossibleValuesSerializer):
    class Meta(AttributePossibleValuesSerializer.Meta):
        model = GenericAttribute

    def get_possible_values(self, attribute_obj, **kwargs):
        return super().get_possible_values(attribute_obj, resource_type="NestedCategoricalFilter", **kwargs)



class MaterializedNestedCategoricalPossibleValuesSerializer(AttributePossibleValuesSerializer):
    class Meta(AttributePossibleValuesSerializer.Meta):
        model = GenericAttribute

    def get_possible_values(self, attribute_obj, **kwargs):
        return super().get_possible_values(attribute_obj,
                                           resource_type="MaterializedNestedCategoricalFilter",
                                           look_for_parent=True,
                                           **kwargs)


class PolymorphicPossibleValuesSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        GenericAttribute: GenericPossibleValuesSerializer,
        CategoricalAttribute: CategoricalPossibleValuesSerializer,
        NestedCategoricalAttribute: NestedCategoricalPossibleValuesSerializer,
        MaterializedNestedCategoricalAttribute: MaterializedNestedCategoricalPossibleValuesSerializer
    }
