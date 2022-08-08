import importlib
from rest_framework import serializers

def get_serializer_class(serializer_full_name):
    module_name = ""
    serializer_name_arr = serializer_full_name.strip().split(".")
    if len(serializer_name_arr) > 1:
        module_name = ".".join(serializer_name_arr[:-1])
    class_name = serializer_name_arr[-1]

    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)

    return class_

def serialize_from_serializer_path(serializer_full_name, data, **kwargs):
    class_ = get_serializer_class(serializer_full_name)

    return class_(data, **kwargs)


def object_from_serializer_path(serializer_full_name, data, **kwargs):
    class_ = get_serializer_class(serializer_full_name)

    serializer = class_(data=data, **kwargs)
    serializer.is_valid(raise_exception=True)
    return serializer.create(data)


class WritableSerializerMethodField(serializers.SerializerMethodField):
    def __init__(self, method_name=None, **kwargs):
        super().__init__(**kwargs)

        self.read_only = False

    def get_default(self):
        default = super().get_default()

        return {
            self.field_name: default
        }

    def to_internal_value(self, data):
        return {self.field_name: data}