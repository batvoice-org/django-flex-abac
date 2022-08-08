import yaml

from django.contrib.contenttypes.models import ContentType

def get_content_type_from_class_name(class_name):
    content_type_path = class_name.split(".")
    if len(content_type_path) == 1:
        app_label = ""
        model = class_name
    else:
        app_label = content_type_path[0]
        model = ".".join(content_type_path[1:])

    return ContentType.objects.get_by_natural_key(app_label, model)

def import_from_yaml(path):
    """
    Imports attributes from a given yaml file. Example of a yaml file:

    .. code-block:: yaml

        types:
          CategoricalAttribute:
            - name: "Category"
              field_name: "category_id"
              class_name: "exampleapp.document"
            ...

          GenericAttribute:
            - name: "Brand name"
              field_name: "brand__name"
              class_name: "exampleapp.document"
              extra_fields:
                "id": "brand__id"
                "name": "brand__name"
              values:
                - value: "Brand3"
                - value: "Brand4"
            ...

          NestedCategoricalAttribute:
            - name: "Topic id"
              field_name: "topics"
              class_name: "exampleapp.document"
              nested_field_name: "id"
              parent_field_name: "parent__id"
              field_type: "exampleapp.topic"
              values:
                - value: 3
                - value: 8
            ...

          MaterializedNestedCategoricalAttribute:
            - types:
                name: Country
                class_name: "exampleapp.document"
                extra_fields:
                  "id": "id"
                  "name": "name"
                children:
                  - name: Province
                    extra_fields:
                      "id": "id"
                      "name": "name"
                    children:
                      - name: City
                        extra_fields:
                          "id": "id"
                          "name": "name"
                values:
                  - value: "Region 1"
                    type: Country
                    children:
                      - value: "Region 1.1"
                        type: Province
                        children:
                          - value: "Region 1.1.1"
                            type: City
                          ...
                      - value: "Region 1.2"
                        type: Province
                        children:
                          - value: "Region 1.2.1"
                            type: City
                          ...
                  ...

    :param path: Path to yaml containing data to load.
    :type path: str
    """

    with open(path) as file:
        attrs = yaml.load(file, Loader=yaml.FullLoader)

        for type_model_name in attrs['types'].keys():
            attr_type_model = ContentType.objects.get(
                app_label='flex_abac',
                model=type_model_name.lower()
            )
            for type_dict in attrs['types'][type_model_name]:
                attr_type_model.model_class().import_from_dict(type_dict)
