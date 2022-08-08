from exampleapp.models import Document, Desk, Brand

from rest_framework import serializers


class DeskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desk
        fields = ['pk', 'name']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['pk', 'name']


class DocumentSerializer(serializers.ModelSerializer):
    desk = DeskSerializer()
    brand = BrandSerializer()

    class Meta:
        model = Document
        fields = ['pk', 'filename', 'desk', 'brand']

    # TODO
    def create(self, validated_data):
        desk_serializer = DeskSerializer(data=validated_data["desk"], many=False)
        desk_serializer.is_valid(raise_exception=True)
        desk_serializer.save()
        desk = desk_serializer.instance

        brand_serializer = BrandSerializer(data=validated_data["brand"], many=False)
        brand_serializer.is_valid(raise_exception=True)
        brand_serializer.save()
        brand = brand_serializer.instance

        document, _ = Document.objects.get_or_create(
            filename=validated_data["filename"],
            desk=desk,
            brand=brand
        )

        return document

    def update(self, instance, validated_data):
        instance.filename = validated_data["filename"]

        if 'desk' in validated_data:
            desk_serializer = self.fields['desk']
            desk_serializer.update(instance.desk, validated_data["desk"])

        if 'brand' in validated_data:
            brand_serializer = self.fields['brand']
            brand_serializer.update(instance.brand, validated_data["brand"])

        instance.save()

        return instance



