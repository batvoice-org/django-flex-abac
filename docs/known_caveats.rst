mKnown caveats
===============

Getting all possible values
---------------------------

- As explained at :ref:`optimizing_valid_filters`, default serializers are included to allow a direct usage, but it is
  not possible to ensure optimality in queries. For that reason, it is recommended to follow the instructions to create
  your own serializer if this functionality is needed and the number of occurrences in the related model is high.

Future work
-----------

The following features are missing but planned for the near future:

- We are not paginating results in some of the outputs. This is a simple improvement, but we haven't had the time to
  address it, so expect this to be ready soon.
- We plan to allow for nesting actions so we can establish relationships among them.

