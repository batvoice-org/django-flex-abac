import importlib

from rest_polymorphic.serializers import PolymorphicSerializer

from flex_abac.models import (
    BaseFilter,
    GenericFilter,
    CategoricalFilter,
    NestedCategoricalFilter,
    MaterializedNestedCategoricalFilter,
    GenericAttribute,
    CategoricalAttribute,
    NestedCategoricalAttribute,
    MaterializedNestedCategoricalAttribute
)
from rest_framework import serializers
from flex_abac.serializers.attributes import (
    PolymorphicAttributeTypeSerializer,
    GenericAttributeSerializer,
    NestedCategoricalAttributeSerializer,
    MaterializedNestedCategoricalAttributeSerializer,
)

from flex_abac.serializers.utils import (
    serialize_from_serializer_path, object_from_serializer_path, WritableSerializerMethodField
)
from flex_abac.serializers.utils import get_serializer_class



class FilterSerializer(serializers.HyperlinkedModelSerializer):
    attribute_type = WritableSerializerMethodField()
    value = WritableSerializerMethodField()
    extra = WritableSerializerMethodField()

    class Meta:
        model = BaseFilter
        fields = ['pk', 'value', 'attribute_type', 'extra']

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(FilterSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    @classmethod
    def _process_validated_data(cls, attribute_class, validated_data):
        attribute_type_data = validated_data["attribute_type"]

        if type(attribute_type_data) == dict:
            attribute_type = attribute_class.objects.get(id=validated_data["attribute_type"]["pk"])
        else:
            attribute_type = attribute_class.objects.get(id=validated_data["attribute_type"])

        value = validated_data["value"]
        if attribute_type.serializer:
            value = object_from_serializer_path(attribute_type.serializer, {"value": value})["value"]

        return attribute_type, value

    def get_extra(self, value_obj):
        extra = None
        attr_serializer = value_obj.attribute_type.serializer
        if attr_serializer:
            serializer_class = get_serializer_class(attr_serializer)
            serializer = serialize_from_serializer_path(attr_serializer, value_obj.value, many=False)
            serializer.context["attribute_obj"] = value_obj.attribute_type
            if hasattr(serializer_class, "get_extra"):
                serializer.fields.update({"extra": serializers.SerializerMethodField()})

            processed_value = serializer.data

            if "extra" in processed_value.keys():
                extra = processed_value.pop("extra")

        return extra




    def get_value(self, value_obj, **kwargs):
        # Since the field is generic, we provide the possibility of adding additional serializers
        if value_obj.attribute_type.serializer:
            return serialize_from_serializer_path(value_obj.attribute_type.serializer, value_obj.value).data["value"]
        else:
            return value_obj.value

    def get_attribute_type(self, value_obj, **kwargs):
        return PolymorphicAttributeTypeSerializer(value_obj.attribute_type, many=False).data



class GenericFilterSerializer(FilterSerializer):

    class Meta(FilterSerializer.Meta):
        model = GenericFilter

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(GenericFilterSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        attribute_type, value = FilterSerializer._process_validated_data(GenericAttribute, validated_data)

        attribute_value, _ = GenericFilter.objects.get_or_create(
            value=value,
            attribute_type=attribute_type
        )

        return attribute_value

    def update(self, instance, validated_data):
        attribute_type, value = FilterSerializer._process_validated_data(GenericAttribute, validated_data)

        instance.value = value
        instance.attribute_type = attribute_type

        instance.save()

        return instance


class CategoricalFilterSerializer(FilterSerializer):

    class Meta(FilterSerializer.Meta):
        model = CategoricalFilter


    def create(self, validated_data):
        attribute_type, value = FilterSerializer._process_validated_data(CategoricalAttribute, validated_data)

        attribute_value, _ = CategoricalFilter.objects.get_or_create(
            value=value,
            attribute_type=attribute_type
        )

        return attribute_value

    def update(self, instance, validated_data):
        attribute_type, value = FilterSerializer._process_validated_data(CategoricalAttribute, validated_data)

        instance.value = value
        instance.attribute_type = attribute_type

        instance.save()

        return instance


class NestedCategoricalFilterSerializer(FilterSerializer):

    class Meta(FilterSerializer.Meta):
        model = NestedCategoricalFilter

    def create(self, validated_data):
        attribute_type, value = FilterSerializer._process_validated_data(NestedCategoricalAttribute, validated_data)

        attribute_value, _ = NestedCategoricalFilter.objects.get_or_create(
            value=value,
            attribute_type=attribute_type
        )

        return attribute_value

    def update(self, instance, validated_data):
        attribute_type, value = FilterSerializer._process_validated_data(NestedCategoricalAttribute, validated_data)

        instance.value = value
        instance.attribute_type = attribute_type

        instance.save()

        return instance


class MaterializedNestedCategoricalFilterSerializer(FilterSerializer):
    parent = WritableSerializerMethodField()

    class Meta(FilterSerializer.Meta):
        model = MaterializedNestedCategoricalFilter
        fields = ['pk', 'value', 'attribute_type', 'parent']

    def get_parent(self, obj):
        parent = obj.get_parent()
        return parent.id if parent else None

    def create(self, validated_data):
        attribute_type, value = FilterSerializer._process_validated_data(MaterializedNestedCategoricalAttribute, validated_data)


        if "parent" in validated_data.keys():
            return MaterializedNestedCategoricalFilter.objects.get(pk=validated_data["parent"]).add_child(
                value=value,
                attribute_type=attribute_type
            )
        else:
            return MaterializedNestedCategoricalFilter.add_root(
                value=value,
                attribute_type=attribute_type
            )

    def update(self, instance, validated_data):
        attribute_type, value = FilterSerializer._process_validated_data(MaterializedNestedCategoricalAttribute,
                                                                         validated_data)
        instance.value = value
        instance.attribute_type = attribute_type

        if "parent" in validated_data.keys():
            parent_node = MaterializedNestedCategoricalFilter.objects.get(pk=validated_data["parent"])
            instance.move(parent_node, 'sorted-child')
            instance.refresh_from_db()

        instance.save()

        return instance


class PolymorphicFilterSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        model_serializer_mapping = self.model_serializer_mapping

        super(PolymorphicFilterSerializer, self).__init__(*args, **kwargs)

        self.model_serializer_mapping = {}

        kwargs['fields'] = fields
        for model, serializer in model_serializer_mapping.items():
            if callable(serializer):
                serializer = serializer(*args, **kwargs)
                serializer.parent = self

            self.model_serializer_mapping[model] = serializer

    model_serializer_mapping = {
        GenericFilter: GenericFilterSerializer,
        CategoricalFilter: CategoricalFilterSerializer,
        NestedCategoricalFilter: NestedCategoricalFilterSerializer,
        MaterializedNestedCategoricalFilter: MaterializedNestedCategoricalFilterSerializer
    }
