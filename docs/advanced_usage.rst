.. _advanced_usage:

Advanced Usage
================

In this section, we will show additional modifications that can be done on the Views, ViewSets, and other parts of the
code to achieve any special need we could have.

Filters precedence
------------------

One thing to keep in mind when configuring the permissions using this library, if the effective permissions a user will
have when applying the combination of different attributes, actions, policies, or roles.

In general, if several actions and filters are applied to a user through a set of roles and policies, the effective
permissions will be:

- For different actions, only the filters associated to each action through a policy will be applied.
- For the same action, the least restrictive access will be provided. Let's assume the same action for the policies
  ``Policy1`` and ``Policy2``, both attached to the ``Role1`` associated to a user. In that case, we can observe some examples:

  + No filters in ``Policy1``, and filters for ``Value1`` and ``Value2`` on ``Policy2`` --> Full access (since no filter
    means no filtering restrictions)
  + Filters for ``Value1`` in ``Policy1`; filters for ``Value2`` on ``Policy2`` --> Access allowed for both ``Value1`` and ``Value2``.

- If different filters are effective for a user through different attributes, the generated filter takes the form of
  an ``AND`` condition. Filters for the same attribute are considered as an ``OR`` condition. This way, for the following
  policies (pseudocode):

.. code-block:: yaml

    role1:
        policy1:
            actions:
                - action1
            scopes:
                - a1.1: attribute1
                - a1.2: attribute1
                - a2.2: attribute2
        policy2:
            actions:
                - action1
            scopes:
                - a1.3: attribute1

, we will get the following filter:

.. code-block:: python

    AND (
        OR (
            attribute1 == a1.1,  # From policy1
            attribute1 == a1.2,  # From policy1
            attribute1 == a1.3,  # From policy2
        ),
        attribute2 == a2.2       # From policy1
    )


Custom Filtering
-----------------

In its most basic form, once we have configured our attributes for the permissions, we will create a ViewSet that
would look like this:

.. code-block:: python

    from flex_abac.mixins import ApplyFilterMixin
    from flex_abac.permissions import CanExecuteMethodPermission

    class DocumentsViewSet(ApplyFilterMixin, viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, CanExecuteMethodPermission]
        serializer_class = DocumentSerializer
        queryset = Document.objects

Internally, each time we access for instance the ``list()`` action, the following happens:

- First, we check the action and the attributes through the ``CanExecuteMethodPermission`` class (as well as other permission
  classes which would be necessary, for instance, the ``IsAuthenticated`` class).
- Additionally, if we have passed parameters to the function, the default behavior is to check these parameters
  are among the values allowed by the configured filters, using the ``filter_name`` field of the attribute model as the
  default parameter name.

Using filters in other parts of the code
########################################

It is usual to need to filter objects in different parts of the code. This can be done as follows:

.. code-block:: python

    from flex_abac.checkers import get_filter_for_valid_objects

    queryset = Document.objects                               # Using the Folder model for this example

    queryset = self.filter_queryset(self.get_queryset())    # The original queryset you want to filter

    valid_filter = get_filter_for_valid_objects(self.request.user,  # The user for which the permissions are being applied
                                                Document            # The model for which attributes will be applied
                                                )

More information about the base_lookup_name

Changing the default attributes mapping
---------------------------------------

Attributes mapping relate user query parameters with the existing attributes. They are created automatically and are used
in two aspects of the permissions system:

#. Check that you can filter by an specific value.
#. Applying the filters directly from the query parameters.

In many cases we don't want to use the same field name used in the attribute model as the query parameter in the url,
which is the default behavior. By default, these parameters and field types are automatically extracted from the from
the ``flex_abac.utils.mappings.DefaultAttributeMappingGenerator`` class. It is possible to extend that class so it uses
the desired parameters as depicted in the following example:

.. code-block:: python

    class CustomAttributeMappingGenerator(DefaultAttributeMappingGenerator):
        aliases = {
            "department_id": "department",
            "category_id": "category"
        }

The keys of the aliases dictionary contain the field_name as used in the attributes; the values are the names of the
desired query parameters.

Then, we do:

.. code-block:: python

    class DocumentsViewSet(ApplyFilterMixin, viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, CanExecuteMethodPermission]
        serializer_class = DocumentSerializer
        queryset = Document.objects

        # We override the attribute_mapping field to indicate we want to use a different attribute_mapping object-
        attribute_mapping = CustomAttributeMappingGenerator()

Getting all the allowed values for an attribute
-----------------------------------------------

Sometimes we need to know all the values a user has access to. There are many ways to do so. For instance, check the
following function:

.. code-block:: python
    :linenos:

    from flex_abac.models import CategoricalAttribute

    def get_authorized_categories(user_id, action_name):
        values = CategoricalAttribute.objects.get(field_name="category_id").\
                    get_all_values_for_user(user_id, action_name)

        if values.exists():
            return list(values.values_list("value", flat=True))
        else:
            return list(Category.objects.values_list("id", flat=True))

Please note that by default just the filtered values will be considered. If no values are provided, this means that
all values are valid and in this case we would like to do something like shown in line 10, where we go directly to
the foreign-referenced model Category, to provide the entire list of values.

Indirect permissions
--------------------

You may need to control access to, say, model A based on attributes of model B, with A and B being linked via
foreign keys.

Let's imagine that we have created attributes for our documents, based on the department they belong to, and also by
their categories.

Let's imagine also that we have the ``Folder`` model, which relates to several models through a foreign key and has a
one-to-many relationship with Document.

This Folder model is as follows:

.. code-block:: python

    class Folder(models.Model):
        document = models.ForeignKey(
            "documents.Document",
            on_delete=models.CASCADE,
            null=False
        )

For our application, we only want to show folders containing at least one accessible document.

Here's a solution:

.. code-block:: python

    from flex_abac.mixins import ApplyFilterMixin
    from flex_abac.permissions import CanExecuteMethodPermission

    class FolderViewSet(ApplyFilterMixin, viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, CanExecuteMethodPermission]
        serializer_class = FolderSerializer
        queryset = Folder.objects

        base_lookup = "document"        # The name of the field in the Folder model.


Adding indirect permissions while filtering
###########################################

We can also use the indirect permissions while filtering. An example is shown next:

.. code-block:: python

    from flex_abac.checkers import get_filter_for_valid_objects

    queryset = Folder.objects                               # Using the Folder model for this example

    queryset = self.filter_queryset(self.get_queryset())    # The original queryset you want to filter

    valid_filter = get_filter_for_valid_objects(self.request.user,  # The user for which the permissions are being applied
                                                Document,           # The model for which attributes will be applied
                                                base_lookup_name="document"    # We want to filter based on the document field of the Folder model
                                                )

.. _custom_serializers:

Custom filter serializers
-------------------------

By default, all attribute types come with a default serializer covering most needs.

Default serializers are:

- ``flex_abac.serializers.default.GenericSerializer`` for the ``GenericAttribute``
- ``flex_abac.serializers.default.CategoricalSerializer`` for the ``CategoricalAttribute``
- ``flex_abac.serializers.default.NestedCategoricalSerializer`` for the ``NestedCategoricalAttribute``
- ``flex_abac.serializers.default.MaterializedNestedCategoricalSerializer`` for the ``MaterializedNestedCategoricalAttribute``

These are used as the default serializers when we create a new attribute of each of these types.

If you need to create a new serializer:

#. Write your serializer as described next.
#. Override the default value of the field ``serializer`` of the instance of the attributes which will be using that
   serializer on the database.

.. warning::

    In general, we recommend overwriting the ``possible_values`` and ``get_extra`` methods of the default serializers, using
    the means described next.

Creating a new serializer from scratch
######################################

Your custom serializer should inherit from the serializer for the corresponding attribute type.
For instance:

.. code-block:: python

    class CategorySerializer(CategoricalSerializer):

.. _optimizing_valid_filters:

Optimizing the listing of valid filters
#######################################

The endpoint :ref:`attribute_possible_values_endpoint` provides the list of possible values for a given attribute to be
used for instance in a permissions management UI to select the proper filter. In general, the library does the job
for this part by checking the base model.

However, let's imagine that we want to know all the possible categories a document can belong to. In a ``CategoricalAttribute``
which uses the foreign key stored in the ``Document`` instances, we can know the valid categories by checking all the
categories referenced by the Document model. This is what is done by the library since with the provided information
this is as far as it can reach, but it comes with two potential issues:

#. It is impossible to know if there are categories that were never referenced by a document, but we might want to have
   these in our filters in the provision of future documents which could be using them.
#. In practice, the number of categories might be manageable (tens of categories, for example), but if
   the number of documents is high (for instance, in the order of thousands or millions), this makes very
   inefficient to know all the possible category values by using the references in documents, since it implies checking
   all the existing documents.

For these reasons, in general, we recommend rewriting the possible_values method to become something like this:

.. code-block:: python

    class CategorySerializer(CategoricalSerializer):
        @classmethod
        def possible_values(cls, attribute_obj):
            return Category.objects.annotate(value=F("id")).values("value")

In the end, what we need is a list of possible values, each inside a ``value`` field.

Extra information
#################

The serializers also provide extra information to be used by the frontend.

The fields provided will be inside a dictionary nested under the ``extra`` field.
An example of how to do so is shown next:

.. code-block:: python

    class CategorySerializer(CategoricalSerializer):
        @classmethod
        def possible_values(cls, attribute_obj):
            return Category.objects.annotate(value=F("id")).values("value")

        def get_extra(self, extra_info=None):
            response = Category.objects.filter(id=extra_info).values("id", "category_pretty_name").annotate(name=F("category_pretty_name"))
            if response.exists():
                return response.first()
            else:
                return {}

Since we are using a categorical attribute, we expect an id in the extra_info, but it can change depending on the type
of attribute. We use it to get the particular document category we are looking for, and we provide the ``id`` and the
``category_pretty_name`` fields in the model, but we could provide even more.

If the requested id exists, it is returned as an annotated dict.

Advanced example
################

It is possible to get even more complex serializers, which can be needed when we use complex lookups as a generic attribute.

For instance, let's imagine we create this datetime_attribute:

.. code-block:: python

        datetime_attribute = GenericAttribute.objects.create(
            name="Document date",
            field_name="document_datetime__range",
            serializer="path.to.test_permissionsview.DatetimeSerializer"
        )

We can then create the serializer defined in the ``serializer`` field as follows:

.. code-block:: python

    class DatetimeSerializer(serializers.Serializer):
        DATE_TIME_FORMAT = "%Y-%m-%d"

        value = serializers.SerializerMethodField()

        class Meta:
            fields = ['value']

        @classmethod
        def possible_values(cls, attribute_obj):
            return [{
                "value": (datetime.strptime("2021-09-03", DatetimeSerializer.DATE_TIME_FORMAT),
                          datetime.strptime("2021-09-04", DatetimeSerializer.DATE_TIME_FORMAT))
            }, {
                "value": (datetime.strptime("2021-09-04", DatetimeSerializer.DATE_TIME_FORMAT),
                          datetime.strptime("2021-09-05", DatetimeSerializer.DATE_TIME_FORMAT))
            }]

        def get_value(self, obj):
            return (
                obj[0].strftime(DatetimeSerializer.DATE_TIME_FORMAT),
                obj[1].strftime(DatetimeSerializer.DATE_TIME_FORMAT),
            )

        def create(self, validated_data):
            return {"value": (
                        datetime.strptime(validated_data["value"][0], DatetimeSerializer.DATE_TIME_FORMAT),
                        datetime.strptime(validated_data["value"][1], DatetimeSerializer.DATE_TIME_FORMAT)
                    )}


.. _custom_action_names:

Custom Action names
--------------------------

Each time we want to check for permissions, we need to know which action is applicable in each case. For instance, inside
a view, we can pass the action name through the ``flex_abac_action_name`` field using a fixed string or a generator.

Fixed action name
#################

If we want a fixed action name for a view, it is as easy as doing it as follows:

.. code-block:: python

    class ExampleViewSet(viewsets.ModelViewSet):
        permission_classes = [CanExecuteMethodPermission]
        serializer_class = DocumentSerializer
        queryset = Document.objects
        flex_abac_action_name = "action_name"

Action name generators
######################

It is possible to use action name generators instead of fixed ones. Some use cases for that are:

- Being able to use different action names for different actions inside a ViewSet.
- Using different action names based on the HTTP method. So it is possible to distinguish between ``read`` and ``write``
  operations.
- etc.

By default, if no action name is indicated, the ``flex_abac.utils.action_names.GroupedMethodActionNameGenerator`` is used.

Some default action name generators are provided:

- **ModelActionNameGenerator** generates action names in the shape ``<model_name>__<view_action_name>``, which are extracted
  from the queryset and the action of the view, respectively.
- **MethodAndTypeActionNameGenerator** generates action names in the shape
  ``<model_name>__<view_action_name>__<http_method>``, which are extracted from the queryset, the action of the view, and
  the http method being used, respectively.
- **GroupedMethodActionNameGenerator** generates action names in the shape ``<model_name>__<read|write>``. The model is
      extracted from the queryset. Then we decide if it is a read or a write action based on the HTTP method:

  - Read methods: GET, HEAD, TRACE, OPTIONS.
  - Write methods: POST, PUT, DELETE, PATCH, CONNECT.

Indicating action name while filtering
#########################################

We can also use custom action names with custom filtering. An example is shown next:

.. code-block:: python

    from flex_abac.checkers import get_filter_for_valid_objects

    queryset = Document.objects                               # Using the Document model for this example

    queryset = self.filter_queryset(self.get_queryset())    # The original queryset you want to filter

    valid_filter = get_filter_for_valid_objects(self.request.user,  # The user for which the permissions are being applied
                                                Document,           # The model for which attributes will be applied
                                                action_name=ModuleActionNameGenerator.get_action_name(self)) # Action name
                                                )
