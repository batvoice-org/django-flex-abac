from flex_abac.models import (
    BaseAttribute,
    GenericAttribute,
    CategoricalAttribute,
    NestedCategoricalAttribute,
    MaterializedNestedCategoricalAttribute,
    ModelGenericAttribute,
    ModelCategoricalAttribute,
    ModelNestedCategoricalAttribute,
    ModelMaterializedNestedCategoricalAttribute,
)

from rest_framework import serializers

from rest_polymorphic.serializers import PolymorphicSerializer

from flex_abac.serializers.utils import WritableSerializerMethodField
from flex_abac.utils.import_attributes import get_content_type_from_class_name


class BaseAttributeSerializer(serializers.HyperlinkedModelSerializer):
    class_name = WritableSerializerMethodField()
    extra_fields = serializers.JSONField(required=False)

    class Meta:
        model = BaseAttribute
        fields = ['pk', 'name', 'field_name', 'class_name', 'serializer', 'extra_fields']

    def get_class_name(self, obj):
        raise NotImplementedError


class GenericAttributeSerializer(BaseAttributeSerializer):
    class Meta(BaseAttributeSerializer.Meta):
        model = GenericAttribute

    def get_class_name(self, obj):
        owner_content_object = ModelGenericAttribute.objects.get(attribute_type=obj).owner_content_object
        return f"{owner_content_object.app_label}.{owner_content_object.model}"

    def create(self, validated_data):
        attribute_type = GenericAttribute.objects.create(
            name=validated_data["name"],
            field_name=validated_data["field_name"],
            extra_fields=validated_data["extra_fields"] if "extra_fields" in validated_data.keys() else None
        )
        if "serializer" in validated_data.keys():
            attribute_type.serializer = validated_data["serializer"]
        else:
            attribute_type.serializer = GenericAttribute._meta.get_field('serializer').default

        attribute_type.save()

        # Adding the attribute to the registry of associated attributes for the object specified by class name
        obj_content_type = get_content_type_from_class_name(class_name=validated_data["class_name"])
        ModelGenericAttribute.objects.create(attribute_type=attribute_type, owner_content_object=obj_content_type)

        return attribute_type

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.field_name = validated_data["field_name"]
        instance.extra_fields = validated_data["extra_fields"] if "extra_fields" in validated_data.keys() else None
        if "serializer" in validated_data.keys():
            instance.serializer = validated_data["serializer"]
        instance.save()

        return instance


class CategoricalAttributeSerializer(BaseAttributeSerializer):
    class Meta(BaseAttributeSerializer.Meta):
        model = CategoricalAttribute

    def get_class_name(self, obj):
        owner_content_object = ModelCategoricalAttribute.objects.filter(attribute_type=obj)
        if owner_content_object.exists():
            owner_content_object = owner_content_object[0].owner_content_object
        return f"{owner_content_object.app_label}.{owner_content_object.model}"

    def create(self, validated_data):
        attribute_type = CategoricalAttribute.objects.create(
            name=validated_data["name"],
            field_name=validated_data["field_name"],
            extra_fields=validated_data["extra_fields"] if "extra_fields" in validated_data.keys() else None
        )
        if "serializer" in validated_data.keys():
            attribute_type.serializer = validated_data["serializer"]
        else:
            attribute_type.serializer = CategoricalAttribute._meta.get_field('serializer').default

        attribute_type.save()

        # Adding the attribute to the registry of associated attributes for the object specified by class name
        obj_content_type = get_content_type_from_class_name(class_name=validated_data["class_name"])
        ModelCategoricalAttribute.objects.create(attribute_type=attribute_type, owner_content_object=obj_content_type)

        return attribute_type

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.field_name = validated_data["field_name"]
        instance.extra_fields = validated_data["extra_fields"] if "extra_fields" in validated_data.keys() else None
        if "serializer" in validated_data.keys():
            instance.serializer = validated_data["serializer"]
        instance.save()

        return instance


class NestedCategoricalAttributeSerializer(BaseAttributeSerializer):
    field_type = WritableSerializerMethodField()

    class Meta(BaseAttributeSerializer.Meta):
        model = NestedCategoricalAttribute
        fields = ['pk', 'name', 'field_name', 'nested_field_name', 'parent_field_name', 'field_type', 'class_name', 'serializer', 'extra_fields']

    def get_field_type(self, obj):
        return f"{obj.field_type.app_label}.{obj.field_type.model}"

    def get_class_name(self, obj):
        owner_content_object = ModelNestedCategoricalAttribute.objects.get(attribute_type=obj).owner_content_object
        return f"{owner_content_object.app_label}.{owner_content_object.model}"

    def create(self, validated_data):
        attribute_type = NestedCategoricalAttribute.objects.create(
            name=validated_data["name"],
            field_name=validated_data["field_name"],
            nested_field_name=validated_data["nested_field_name"],
            parent_field_name=validated_data["parent_field_name"],
            field_type=get_content_type_from_class_name(class_name=validated_data["field_type"]),
            extra_fields=validated_data["extra_fields"] if "extra_fields" in validated_data.keys() else None
        )
        if "serializer" in validated_data.keys():
            attribute_type.serializer = validated_data["serializer"]
        else:
            attribute_type.serializer = NestedCategoricalAttribute._meta.get_field('serializer').default

        attribute_type.save()

        # Adding the attribute to the registry of associated attributes for the object specified by class name
        obj_content_type = get_content_type_from_class_name(class_name=validated_data["class_name"])
        ModelNestedCategoricalAttribute.objects.create(attribute_type=attribute_type,
                                                       owner_content_object=obj_content_type)

        return attribute_type

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.field_name = validated_data["field_name"]
        instance.nested_field_name = validated_data["nested_field_name"]
        instance.parent_field_name = validated_data["parent_field_name"]
        instance.extra_fields = validated_data["extra_fields"] if "extra_fields" in validated_data.keys() else None
        if "serializer" in validated_data.keys():
            instance.serializer = validated_data["serializer"]
        instance.save()

        return instance


class MaterializedNestedCategoricalAttributeSerializer(BaseAttributeSerializer):
    parent = WritableSerializerMethodField()

    class Meta(BaseAttributeSerializer.Meta):
        model = MaterializedNestedCategoricalAttribute
        fields = ['pk', 'name', 'parent', 'serializer', 'class_name', 'extra_fields']

    def get_parent(self, obj):
        parent = obj.get_parent()
        return parent.id if parent else None

    def get_class_name(self, obj):
        owner_content_object = ModelMaterializedNestedCategoricalAttribute.objects.get(attribute_type=obj).owner_content_object
        return f"{owner_content_object.app_label}.{owner_content_object.model}"

    def create(self, validated_data):
        if "parent" in validated_data.keys():
            attribute_type = MaterializedNestedCategoricalAttribute.objects.get(pk=validated_data["parent"]).\
                add_child(name=validated_data["name"],
                          extra_fields=validated_data["extra_fields"] if "extra_fields" in validated_data.keys() else None)
        else:
            attribute_type = MaterializedNestedCategoricalAttribute.add_root(name=validated_data["name"],
                                                                             extra_fields=validated_data["extra_fields"] if "extra_fields" in validated_data.keys() else None)

        if "serializer" in validated_data.keys():
            attribute_type.serializer = validated_data["serializer"]
        else:
            attribute_type.serializer = MaterializedNestedCategoricalAttribute._meta.get_field('serializer').default

        attribute_type.save()

        # Adding the attribute to the registry of associated attributes for the object specified by class name
        obj_content_type = get_content_type_from_class_name(class_name=validated_data["class_name"])
        ModelMaterializedNestedCategoricalAttribute.objects.create(attribute_type=attribute_type,
                                                                   owner_content_object=obj_content_type)

        return attribute_type

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.extra_fields = validated_data["extra_fields"] if "extra_fields" in validated_data.keys() else None

        if "serializer" in validated_data.keys():
            instance.serializer = validated_data["serializer"]

        if "parent" in validated_data.keys():
            parent_node = MaterializedNestedCategoricalAttribute.objects.get(pk=validated_data["parent"])
            instance.move(parent_node, 'last-child')
            instance.refresh_from_db()

        instance.save()

        return instance


class PolymorphicAttributeTypeSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        GenericAttribute: GenericAttributeSerializer,
        CategoricalAttribute: CategoricalAttributeSerializer,
        NestedCategoricalAttribute: NestedCategoricalAttributeSerializer,
        MaterializedNestedCategoricalAttribute: MaterializedNestedCategoricalAttributeSerializer
    }

