from django.core.exceptions import FieldDoesNotExist


def get_attributes_per_model(object_type):
    pass

def get_roles_per_user(user):
    pass

def get_values_per_attribute(attribute_type):
    pass

def get_subclasses(cls):
    for subclass in cls.__subclasses__():
        yield from get_subclasses(subclass)
        yield subclass


def import_from(module_path):
    module, name = module_path.rsplit('.', 1)

    module = __import__(module, fromlist=[name])
    return getattr(module, name)


def get_field_from_lookup_string(obj, lookup_str):
    field_name = ""
    for name in lookup_str.split('__'):
        try:
            field = obj._meta.get_field(name)
        except FieldDoesNotExist:
            # name is probably a lookup or transform such as __contains
            break
        field_name += f"__{name}" if field_name != "" else name
        if hasattr(field, 'related_model'):
            # field is a relation
            model = field.related_model
        else:
            # field is not a relation, any name that follows is
            # probably a lookup or transform
            break

    return field_name

def get_model_and_field_from_lookup_string(obj, lookup_str):
    field_name = ""
    model = obj
    name = ""
    for name in lookup_str.split('__'):
        try:
            field = model._meta.get_field(name)
        except FieldDoesNotExist:
            name = "id"
            # name is probably a lookup or transform such as __contains
            break
        field_name += f"__{name}" if field_name != "" else name
        if hasattr(field, 'related_model'):
            # field is a relation
            new_model = field.related_model
            if not new_model:
                break
            model = new_model
            name = "id"
        else:
            # field is not a relation, any name that follows is
            # probably a lookup or transform
            break

    return model, name