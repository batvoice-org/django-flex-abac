.. _rest_api:

REST API
===============

.. _action_endpoint:

/actions
--------

.. http:get:: /actions

   Allows listing all the available actions in the database

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 403: Access Forbidden

.. http:get:: /actions/(pk)

   Allows getting the info for an specific action in the database.

   :query pk: The primary key of the action for which the detail is being requested.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden

.. http:post:: /actions

   Allows the creation of a new action

   :jsonparam string name: Name of the action to be created.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: Object created
   :statuscode 400: Object already exists.
   :statuscode 403: Access Forbidden

.. http:put:: /actions/(pk)

   Updates an existing action.

   :query pk: The primary key of the action we want to update.
   :jsonparam string name: New name of the action to update.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. http:delete:: /actions/(pk)

   Deletes an existing action.

   :query pk: The primary key of the action we want to delete.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 204: Object deleted
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _attributes_endpoint:

/attribute-types
----------------

.. http:get:: /attribute-types

   Allows listing all the available attribute types in the database

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 403: Access Forbidden

.. http:get:: /attribute-types/(pk)

   Allows getting the info for an specific attribute type in the database.

   :query pk: The primary key of the attribute type for which the detail is being requested.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden

.. http:post:: /attribute-types

   Allows the creation of a new attribute-type

   :jsonparam string resourcetype: The attribute type we are creating. Example: ``GenericAttribute``.
   :jsonparam string name: The name of the new attribute type. Example: ``Category name``.
   :jsonparam string field_name: The field lookup of the attribute type. Example: ``category__name``
   :jsonparam string class_name: The model to which the attribute is related. Example: ``exampleapp.document``
   :jsonparam string serializer: The serializer of the attribute type. Example: ``flex_abac.tests.views.test_permissionsview.DatetimeSerializer``
   :jsonparam string nested_field_name: Just with ``NestedCategoricalAttribute``. The field of interest in the nested model. Example: ``id``
   :jsonparam string parent_field_name: Just with ``NestedCategoricalAttribute``. The field of the parent in the nested model. Example: ``parent_id``
   :jsonparam string field_type: Just with ``NestedCategoricalAttribute``. The type of the nested model. Example: ``exampleapp.topic``
   :jsonparam foreign_key parent: Just with ``MaterializedNestedCategoricalAttribute``. The pk of the parent of the attribute (if not a root attribute). Example: ``1``

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: Object created
   :statuscode 400: Object already exists.
   :statuscode 403: Access Forbidden

.. http:put:: /attribute-types/(pk)

   Updates an existing attribute type.

   :query pk: The primary key of the attribute type we want to update.

   :jsonparam string name: The new name of the attribute type. Example: ``Category name``.
   :jsonparam string field_name: The new field lookup of the attribute type. Example: ``category__name``
   :jsonparam string serializer: The serializer of the attribute type. Example: ``flex_abac.tests.views.test_permissionsview.DatetimeSerializer``
   :jsonparam string nested_field_name: Just with ``NestedCategoricalAttribute``. The field of interest in the nested model. Example: ``id``
   :jsonparam string parent_field_name: Just with ``NestedCategoricalAttribute``. The field of the parent in the nested model. Example: ``parent_id``
   :jsonparam string field_type: Just with ``NestedCategoricalAttribute``. The type of the nested model. Example: ``exampleapp.topic``
   :jsonparam foreign_key parent: Just with ``MaterializedNestedCategoricalAttribute``. The pk of the parent of the attribute (if not a root attribute). Example: ``1``

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. http:delete:: /attribute-types/(pk)

   Deletes an existing attribute type.

   :query pk: The primary key of the attribute type we want to delete.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 204: Object deleted
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _attribute_get_all_allowed_values_endpoint:

/attribute-types/(pk)/get_all_allowed_values
********************************************

.. http:get:: /attribute-types/(pk)/get_all_allowed_values

   Allows knowing all the values which are allowed for the current user, for an attribute.

   :query pk: The primary key of the attribute type for which the detail is being requested.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden

.. _filters_endpoint:

/attribute-filters
------------------

.. http:get:: /attribute-filters

   Allows listing all the available filters in the database

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 403: Access Forbidden

.. http:get:: /attribute-filters/(pk)

   Allows getting the info for an specific filter in the database.

   :query pk: The primary key of the filter for which the detail is being requested.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden

.. http:post:: /attribute-filters

   Allows the creation of a new attribute-type

   :jsonparam string resourcetype: The attribute type of the filter we are creating. Example: ``GenericFilter``.
   :jsonparam Object value: The value of the filter. Examples: ``1``, ``Italy``, ``2021-10-20``, etc.
   :jsonparam json extra: The extra information required by the default serializer. Examples: ``{ "brand__id": "id", "brand__name": "category" }``
   :jsonparam Object attribute_type: The primary key of the attribute type the filter belongs to; or a serialized version
              of a new attribute type, if we need to create it on the fly. Examples: ``1``,
              ``{ "resourcetype": "GenericAttribute", "name": "Category", "field_name": "category_id", "class_name": "exampleapp.document" }``

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: Object created
   :statuscode 400: Object already exists.
   :statuscode 403: Access Forbidden

.. http:put:: /attribute-filters/(pk)

   Updates an existing filter.

   :query pk: The primary key of the filter we want to update.

   :jsonparam Object value: The value of the filter. Examples: ``1``, ``Italy``, ``2021-10-20``, etc.
   :jsonparam json extra: The extra information required by the default serializer. Examples: ``{ "brand__id": "id", "brand__name": "category" }``
   :jsonparam Object attribute_type: The primary key of the attribute type the filter belongs to; or a serialized version
              of a new attribute type, if we need to create it on the fly. Examples: ``1``,
              ``{ "resourcetype": "GenericAttribute", "name": "Category", "field_name": "category_id", "class_name": "exampleapp.document" }``

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. http:delete:: /attribute-filters/(pk)

   Deletes an existing filter.

   :query pk: The primary key of the filter we want to delete.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 204: Object deleted
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _policies_endpoint:

/policies
---------

.. http:get:: /policies

   Allows listing all the available policies in the database

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 403: Access Forbidden

.. http:get:: /policies/(pk)

   Allows getting the info for an specific policy in the database.

   :query pk: The primary key of the policy for which the detail is being requested.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden

.. http:post:: /policies

   Allows the creation of a new attribute-type

   :jsonparam string name: The name of the policy we want to create.
   :jsonparam list actions: A list of actions we want to have into the policy. It can be the primary key of the action, or
                            the serialization of the action if we want to create it on the fly.
   :jsonparam list scopes: A list of filters we want to have into the scope of the policy. It can be the primary key
                           of the filter, or the serialization of a new filter if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: Object created
   :statuscode 400: Object already exists.
   :statuscode 403: Access Forbidden

.. http:put:: /policies/(pk)

   Updates an existing policy.

   :query pk: The primary key of the policy we want to update.

   :jsonparam string name: The name of the policy we want to update.
   :jsonparam list actions: A list of actions we want to have into the policy. It can be the primary key of the action, or
                            the serialization of the action if we want to create it on the fly.
   :jsonparam list scopes: A list of filters we want to have into the scope of the policy. It can be the primary key
                           of the filter, or the serialization of a new filter if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. http:delete:: /policies/(pk)

   Deletes an existing policy.

   :query pk: The primary key of the policy we want to delete.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 204: Object deleted
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _policies_add_actions_endpoint:

/policies/(pk)/add_actions
**************************

.. http:put:: /policies/(pk)/add_actions

   Adds actions to the list of actions of an existing policy.

   :query pk: The primary key of the policy we want to update.

   :jsonparam list actions: A list of actions we want to add into the policy. It can be the primary key of the action, or
                            the serialization of the action if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _policies_delete_actions_endpoint:

/policies/(pk)/delete_actions
*****************************

.. http:delete:: /policies/(pk)/delete_actions

   Deletes actions from the list of actions of an existing policy.

   :query pk: The primary key of the policy we want to update.

   :jsonparam list actions: A list of actions we want to remove from the policy. It can be the primary key of the action, or
                            the serialization of the action if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _policies_add_scopes_endpoint:

/policies/(pk)/add_scopes
*************************

.. http:put:: /policies/(pk)/add_scopes

   Adds scopes to the list of actions of an existing policy.

   :query pk: The primary key of the policy we want to update.

   :jsonparam list scopes: A list of filters we want to add into the scope of the policy. It can be the primary key
                           of the filter, or the serialization of a new filter if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _policies_delete_scopes_endpoint:

/policies/(pk)/delete_scopes
****************************

.. http:delete:: /policies/(pk)/delete_scopes

   Deletes scopes from the list of actions of an existing policy.

   :query pk: The primary key of the policy we want to update.

   :jsonparam list scopes: A list of filters we want to delete from the scope of the policy. It can be the primary key
                           of the filter, or the serialization of a new filter if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _policy_get_all_active_attributes_endpoint:

/policies/(pk)/get_all_active_attributes
****************************************

.. http:get:: /policies/(pk)/get_all_active_attributes

   Gathers all distinct attribute types which can be used to construct a filter, based on the models associated to
   the list of actions in a policy.

   :query pk: The primary key of the policy for which the detail is being requested.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden

.. _roles_endpoint:

/roles
------

.. http:get:: /roles

   Allows listing all the available roles in the database

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 403: Access Forbidden

.. http:get:: /roles/(pk)

   Allows getting the info for an specific role in the database.

   :query pk: The primary key of the role for which the detail is being requested.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden

.. http:post:: /roles

   Allows the creation of a new attribute-type

   :jsonparam string name: The name of the role we want to create.
   :jsonparam list policies: A list of policies we want to have into the role. It can be the primary key of the policy, or
                             the serialization of the policy if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: Object created
   :statuscode 400: Object already exists.
   :statuscode 403: Access Forbidden

.. http:put:: /roles/(pk)

   Updates an existing role.

   :query pk: The primary key of the role we want to update.

   :jsonparam string name: The name of the role we want to update.
   :jsonparam list policies: A list of policies we want to have into the role. It can be the primary key of the policy, or
                            the serialization of the policy if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. http:delete:: /roles/(pk)

   Deletes an existing role.

   :query pk: The primary key of the role we want to delete.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 204: Object deleted
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _roles_add_policies_endpoint:

/roles/(pk)/add_policies
************************

.. http:put:: /roles/(pk)/add_policies

   Adds policies to the list of policies of an existing role.

   :query pk: The primary key of the role we want to update.

   :jsonparam list policies: A list of policies we want to add into the role. It can be the primary key of the policy, or
                            the serialization of the policy if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _roles_delete_policies_endpoint:

/roles/(pk)/delete_policies
***************************

.. http:delete:: /roles/(pk)/delete_policies

   Deletes policies from the list of policies of an existing role.

   :query pk: The primary key of the role we want to update.

   :jsonparam list policies: A list of policies we want to remove from the role. It can be the primary key of the policy, or
                            the serialization of the policy if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _users_endpoint:

/users
------

.. http:get:: /users

   Allows listing all the available users in the database

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 403: Access Forbidden

.. http:get:: /users/(pk)

   Allows getting the info for an specific user in the database.

   :query pk: The primary key of the user for which the detail is being requested.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden

.. http:post:: /users

   Allows the creation of a new attribute-type

   :jsonparam string name: The name of the user we want to create.
   :jsonparam list roles: A list of roles we want to have into the user. It can be the primary key of the role, or
                             the serialization of the role if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: Object created
   :statuscode 400: Object already exists.
   :statuscode 403: Access Forbidden

.. http:put:: /users/(pk)

   Updates an existing user.

   :query pk: The primary key of the user we want to update.

   :jsonparam string name: The name of the user we want to update.
   :jsonparam list roles: A list of roles we want to have into the user. It can be the primary key of the role, or
                            the serialization of the role if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. http:delete:: /users/(pk)

   Deletes an existing user.

   :query pk: The primary key of the user we want to delete.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 204: Object deleted
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _users_add_roles_endpoint:

/users/(pk)/add_roles
*********************

.. http:put:: /users/(pk)/add_roles

   Adds roles to the list of roles of an existing user.

   :query pk: The primary key of the user we want to update.

   :jsonparam list roles: A list of roles we want to add into the user. It can be the primary key of the role, or
                            the serialization of the role if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden

.. _users_delete_roles_endpoint:

/users/(pk)/delete_roles
************************

.. http:delete:: /users/(pk)/delete_roles

   Deletes roles from the list of roles of an existing user.

   :query pk: The primary key of the user we want to update.

   :jsonparam list roles: A list of roles we want to remove from the user. It can be the primary key of the role, or
                            the serialization of the role if we want to create it on the fly.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: Object updated
   :statuscode 404: Object to update not found
   :statuscode 403: Access Forbidden


.. _users_get_all_allowed_values_endpoint:

/users/(pk)/get_all_allowed_values
**********************************

.. http:get:: /users/(pk)/get_all_allowed_values

   Allows knowing all the values which are allowed for an specific user, for all the attributes.

   :query pk: The primary key of the user for which the allowed values are being obtained.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden

.. _attribute_possible_values_endpoint:

/possible-values
----------------

.. http:get:: /possible-values

   Allows listing all the possible values that all the attribute types can take, grouped by attribute.

   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 403: Access Forbidden

.. http:get:: /possible-values/(pk)

   Allows listing all the possible values that an specific attribute type can take.

   :query pk: The primary key of the attribute type for which the possible values are being requested.
   :reqheader Accept: the response content type depends on
                      :mailheader:`Accept` header
   :reqheader Authorization: optional OAuth token to authenticate
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: No Error
   :statuscode 404: Object not found
   :statuscode 403: Access Forbidden