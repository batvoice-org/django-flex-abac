.. _getting_started_rest_api:

Getting started with REST API
=============================

Flex-abac comes with a REST API interface for managing permissions. You can easily plug in a frontend to the API
to enable permissions management by end users.

Check out the ``example/frontend`` folder which contains an example VueJS frontend illustrating how
a frontend can be easily provided for permissions management.

The entrypoint to the permissions management API has its own permissions which are disabled by default, but which can be
enabled as described in :ref:`metapermissions_intro`.

Creating a Role-Attribute-Based Access Control System using the API
----------------------------------------------------------------------------

In this section, we will work with the same users and data created for the :ref:`getting_started` guide. Also, we will
use the roles, policies, actions, and attributes defined in the table at section :ref:`creating_first_rbac`

We will need to emulate the browser again:

.. code-block:: python

    from rest_framework.test import APIClient
    import json

    # NOTE: This is just needed for testing purposes, do not include the following two lines
    # in your project unless you know what you are doing!
    from django.conf import settings
    settings.ALLOWED_HOSTS += ['testserver']

    django_client = APIClient(enforce_csrf_checks=False)
    django_client.force_authenticate(user=peter)


.. _creating_the_actions_for_the_rbac:

Creating the actions for the RBAC
#################################

We are about to create the same attribute types we created in the "Getting started" guide. To do so, we will access the
:ref:`action_endpoint` endpoint. The way we do so is as follows:

.. code-block:: python

    action_read = django_client.post("/flex_abac/actions/", {
                                        "pretty_name": "Can read documents",
                                        "name": "document__read" })
    print(action_read.status_code)
    # 201
    print(json.dumps(action_read.data, indent=4))
    # {'name': 'document__read', 'pretty_name': 'Can read documents', 'models': [], 'pk': 5}

As can be observed, we just need to provide the same parameters we passed directly to the objects. We do the same for
the write action.

.. code-block:: python

    action_write = django_client.post("/flex_abac/actions/", {
                                            "pretty_name": "Can edit documents",
                                            "name": "document__write" })
    print(action_write.status_code)

We can also add information about the models related to an action. This information is just for visualization purposes
and won't be used in the evaluation of the permissions. It is used by :ref:`get_all_active_attributes` to gather
all the possible attributes related to the models indicated for an action, to ease the construction of the policies. We
do this as follows:

.. code-block:: python

    action_with_models = django_client.post("/flex_abac/actions/", {
                                "pretty_name": "Action with models",
                                "name": "action__with__models",
                                "models": [ 10 ]
                            })

    print(action_with_models.status_code)
    # 201

Additional operations with actions
**********************************

It is also possible to list the available actions:

.. code-block:: python

    response = django_client.get("/flex_abac/actions/")
    print(json.dumps(response.data, indent=4))
    # [
    #     {
    #         "name": "document__read",
    #         "pretty_name": "Can read documents",
    #         "models": [],
    #         "pk": 7
    #     },
    #     {
    #         "name": "document__write",
    #         "pretty_name": "Can edit documents",
    #         "models": [],
    #         "pk": 8
    #     }
    # ]

We can also get the detail for an specific action.

.. code-block:: python

    response = django_client.get("/flex_abac/actions/7/")
    print(json.dumps(response.data, indent=4))
    # {
    #     "name": "document__read",
    #     "pretty_name": "Can read documents",
    #     "models": [],
    #     "pk": 7
    # }

It is also possible to update an action

.. code-block:: python

    response = django_client.put("/flex_abac/actions/7/", {
                                        "pretty_name": "Can read documents (updated)",
                                        "name": "document__read" })
    print(response.status_code)
    # 200

    # Checking it was updated
    response = django_client.get("/flex_abac/actions/7/")
    print(json.dumps(response.data, indent=4))
    # {
    #     "name": "document__read",
    #     "pretty_name": "Can read documents (updated)",
    #     "models": [],
    #     "pk": 7
    # }

Finally, an action can be removed.

.. code-block:: python

    # First, we create a dummy action so we can remove it.
    dummy_action = django_client.post("/flex_abac/actions/", {
                                            "pretty_name": "I'm a short-living action",
                                            "name": "dummy_action" })
    print(dummy_action.status_code, dummy_action.data["pk"])
    # 201 10

    # Then, we remove it
    response = django_client.delete(f'/flex_abac/actions/{dummy_action.data["pk"]}/')
    print(response.status_code)
    # 204

    # Just checking
    response = django_client.get(f'/flex_abac/actions/{dummy_action.data["pk"]}/')
    # Not Found: /flex_abac/actions/10/
    print(response.status_code)
    # 404

Creating categorical attributes using the API
###############################################################

As in the previous example, we will need an attribute for the brand and another one for the category. We will use the
:ref:`attributes_endpoint` endpoint for this.

.. code-block:: python

    attribute_brand = django_client.post("/flex_abac/attribute-types/", {
                                     "name": "Brand attribute",
                                     "class_name": "exampleapp.document",
                                     "field_name": "brand__id",
                                     "resourcetype": "CategoricalAttribute" })
    print(attribute_brand.status_code)
    # 201
    print(json.dumps(attribute_brand.data, indent=4))
    # {
    #     "pk": 1,
    #     "name": "Brand attribute",
    #     "field_name": "brand__id",
    #     "class_name": "exampleapp.document",
    #     "serializer": "flex_abac.serializers.default.CategoricalSerializer",
    #     "extra_fields": null,
    #     "resourcetype": "CategoricalAttribute"
    # }

The attribute has been successfully created. In general, we will need to pass:

* ``name``: The human-readable name we wish to give to the attribute.
* ``class_name``: The name of the model this attribute is related to. In our case, we are dealing with brands, but as
  the foreign key of the Document model, so we pass "exampleapp.document" as the class name.
* ``field_name``: The name of the field of the model defined in the ``class_name`` parameter. Remember that we can use
  nested fields and/or lookups here to cover more complex use cases.
* ``resourcetype``: The type of the attribute we are passing, which should be one of those described in
  :ref:`attribute_types`. In most cases, a CategoricalAttribute should be enough.

Other parameters like ``serializer`` or ``extra_fields``, which are related to how the filters are presented to the user,
are described in more detail in :ref:`custom_serializers` and in :ref:`attributes_endpoint`. In general, the default
serializers will cover most of the use cases, but you might want to extend their behavior.

We repeat the process to create the category attribute.

.. code-block:: python

    attribute_category = django_client.post("/flex_abac/attribute-types/", {
                                     "name": "Category attribute",
                                     "class_name": "exampleapp.document",
                                     "field_name": "category__id",
                                     "resourcetype": "CategoricalAttribute" })
    print(attribute_brand.status_code)
    # 201

As we did for actions, we can also list, detail, update and delete attributes using the REST API. More information about
this is documented at :ref:`attributes_endpoint`.

Adding filters using the categorical attributes for the ARBAC using the API
###########################################################################

Now we have all that we need to start adding filters. To do so, we will use the :ref:`filters_endpoint`.

Using the formerly created attributes, we can do as follows:

.. code-block:: python

    filter_brands = {}
    for value in [1, 3]:
        filter_brand = django_client.post("/flex_abac/attribute-filters/",
                                             {
                                                 "value": value,
                                                 "resourcetype": "CategoricalFilter",
                                                 "attribute_type": attribute_brand.data["pk"]
                                            })
        print(filter_brand.status_code)
        # 201
        filter_brands[value] = filter_brand

    print(json.dumps(filter_brands[1].data, indent=4))
    # {
    #     "pk": 6,
    #     "value": "1",
    #     "attribute_type": {
    #         "pk": 1,
    #         "name": "Brand attribute",
    #         "field_name": "brand__id",
    #         "class_name": "exampleapp.document",
    #         "serializer": "flex_abac.serializers.default.CategoricalSerializer",
    #         "extra_fields": null,
    #         "resourcetype": "CategoricalAttribute"
    #     },
    #     "extra": {},
    #     "resourcetype": "CategoricalFilter"
    # }

We are just interested in values 1 and 3, so created a filter for each of these cases. The required parameters are:

* ``value``: The value of the filter, the primary key of the desired brands in this case.
* ``resourcetype``: The type of the filter we are passing, which should be associated with one of those described in
  :ref:`attribute_types`. Since it is related to a CategoricalAttribute, we indicate it is a CategoricalFilter.
* ``attribute_type``: The attribute for which we want to create the filter. In our case, the positive integer
  identifier of the ``attribute_brand``.

In the output provided, note that the attribute_type is also serialized.

We do the same for categories.

.. code-block:: python

    filter_categories = {}
    for value in [2, 4]:
        filter_category = django_client.post("/flex_abac/attribute-filters/",
                                             {
                                                 "value": value,
                                                 "resourcetype": "CategoricalFilter",
                                                 "attribute_type": attribute_category.data["pk"]
                                            })
        print(filter_category.status_code)
        # 201
        filter_categories[value] = filter_category


Adding filters and actions to policies using the API
####################################################

Now we are about to create the policies as described in the previous example. The names of policies will be
``Policy Read Everything``, ``Policy Read Odd Brands``, ``Policy Write Odd Brands``, ``Policy Read Even Category``. We will create
the following different approaches so we can see the different possibilities.

The ``Policy Read Everything`` policy
*************************************

Let's start with the ``Policy Read Everything`` policy. We create it through the :ref:`policies_endpoint`.

.. code-block::

    policy_read_everything = django_client.post("/flex_abac/policies/",
                                                        {
                                                            "name": "Policy Read Everything",
                                                            "actions": [],
                                                            "scopes": []
                                                        }, format="json")
    print(policy_read_everything.status_code)
    # 201
    print(json.dumps(policy_read_everything.data, indent=4))
    # {
    #     "pk": 1,
    #     "name": "Policy Read Everything",
    #     "actions": [],
    #     "scopes": []
    # }

As we can see, the policy has been created, but we haven't added any action nor scope. In this particular case, we
won't need any scope. But what about the actions? We could have added it directly, we will show an example for this
later, but let's see how can an additional action can be added at any time. For that we will use the
:ref:`policies_add_actions_endpoint` endpoint.

.. code-block:: python

    response = django_client.put(
                    f'/flex_abac/policies/{policy_read_everything.data["pk"]}/add_actions/',
                    {
                        "actions": [
                            action_read.data["pk"]
                        ],
                    })
    print(response.status_code)
    # 200
    print(json.dumps(response.data, indent=4))
    # {
    #     "pk": 1,
    #     "actions": [
    #         {
    #             "name": "document__read",
    #             "pretty_name": "Can read documents (updated)",
    #             "models": [],
    #             "pk": 7
    #         }
    #     ]
    # }

We can see that the existing read action has been attached to the list of actions for that policy.

It is also possible to remove actions through the :ref:`policies_delete_actions_endpoint` endpoint.

The ``Policy Read Odd Brands`` policy
*************************************

On this occasion, we will add the actions directly when creating the policy. We will just include a scope, so we
can see how to add another one.

.. code-block:: python

    policy_read_odd_brands = django_client.post("/flex_abac/policies/",
                                    {
                                        "name": "Policy Read Odd Brands",
                                        "actions": [ action_read.data["pk"] ],
                                        "scopes": [ filter_brands[1].data["pk"] ]
                                    }, format="json")
    print(policy_read_odd_brands.status_code)
    # 201
    print(json.dumps(policy_read_odd_brands.data, indent=4))
    # {
    #     "pk": 2,
    #     "name": "Policy Read Odd Brands",
    #     "actions": [
    #         {
    #             "name": "document__read",
    #             "pretty_name": "Can read documents (updated)",
    #             "models": [],
    #             "pk": 7
    #         }
    #     ],
    #     "scopes": [
    #         {
    #             "pk": 6,
    #             "value": "1",
    #             "attribute_type": {
    #                 "pk": 1,
    #                 "name": "Brand attribute",
    #                 "field_name": "brand__id",
    #                 "class_name": "exampleapp.document",
    #                 "serializer": "flex_abac.serializers.default.CategoricalSerializer",
    #                 "extra_fields": null,
    #                 "resourcetype": "CategoricalAttribute"
    #             },
    #             "extra": {},
    #             "resourcetype": "CategoricalFilter"
    #         }
    #     ]
    # }

We can see in the output, the deployed information for this policy. We miss an additional filter when the brand
identifier is 3. Let's add it through the :ref:`policies_add_scopes_endpoint` endpoint.

.. code-block:: python

    response = django_client.put(
                    f'/flex_abac/policies/{policy_read_odd_brands.data["pk"]}/add_scopes/',
                    {
                        "scopes": [
                            filter_brands[3].data["pk"]
                        ]
                    })

    print(json.dumps(response.data, indent=4))
    # {
    #     "pk": 2,
    #     "scopes": [
    #         {
    #             "pk": 6,
    #             "value": "1",
    #             "attribute_type": {
    #                 "pk": 1,
    #                 ...
    #             },
    #             "extra": {},
    #             "resourcetype": "CategoricalFilter"
    #         },
    #         {
    #             "pk": 7,
    #             "value": "3",
    #             "attribute_type": {
    #                 "pk": 1,
    #                 ...
    #             },
    #             "extra": {},
    #             "resourcetype": "CategoricalFilter"
    #         }
    #     ]
    # }

We can see that now there are two scopes associated with the policy.

It is also possible to remove filters from a policy through the :ref:`policies_delete_scopes_endpoint` endpoint.

``Policy Write Odd Brands`` and ``Policy Read Even Categories`` policies
************************************************************************

We are now ready to build the remaining policies as follows:

.. code-block:: python

    policy_write_odd_brands = django_client.post("/flex_abac/policies/",
                                    {
                                        "name": "Policy Write Odd Brands",
                                        "actions": [ action_write.data["pk"] ],
                                        "scopes": [
                                            filter_brands[1].data["pk"],
                                            filter_brands[3].data["pk"],
                                        ]
                                    }, format="json")
    print(policy_write_odd_brands.status_code)
    # 201

    policy_read_even_categories = django_client.post("/flex_abac/policies/",
                                    {
                                        "name": "Policy Read Even Categories",
                                        "actions": [ action_read.data["pk"] ],
                                        "scopes": [
                                            filter_categories[2].data["pk"],
                                            filter_categories[4].data["pk"],
                                        ]
                                    }, format="json")
    print(policy_read_even_categories.status_code)
    # 201

Creating the filters at the same time as the policy
***************************************************

It is also possible to create new action filters as the policy is created. Let's create for instance the Policy
``Policy DummyAction over Odd Categories``:

.. code-block:: python

    response = django_client.post("/flex_abac/policies/",
                    {
                        "name": "Policy DummyAction over Odd Categories",
                        "actions": [{
                            "pretty_name": "NewDummyActionFromPolicy",
                            "name": "this_action_do_nothing"
                        }],
                        "scopes": [
                            {
                                "value": 1,
                                "attribute_type": attribute_category.data["pk"],
                                "resourcetype": "CategoricalFilter"
                            },
                            {
                                "value": 3,
                                "attribute_type": attribute_category.data["pk"],
                                "resourcetype": "CategoricalFilter"
                            }
                        ]
                    }, format="json")
    print(response.status_code)
    # 201

Let's see if the action and the scopes where properly created

.. code-block:: python

    print(json.dumps(
            django_client.get(
                f'/flex_abac/actions/{response.data["actions"][0]["pk"]}/'
            ).data, indent=4))
    # {
    #     "name": "this_action_do_nothing",
    #     "pretty_name": "NewDummyActionFromPolicy",
    #     "models": [],
    #     "pk": 11
    # }

    print(json.dumps(
            django_client.get(
                f'/flex_abac/attribute-filters/{response.data["scopes"][0]["pk"]}/'
            ).data, indent=4))
    # {
    #     "pk": 10,
    #     "value": 1,
    #     "attribute_type": {
    #         "pk": 2,
    #         "name": "Category attribute",
    #         "field_name": "category__id",
    #         "class_name": "exampleapp.document",
    #         "serializer": "flex_abac.serializers.default.CategoricalSerializer",
    #         "extra_fields": null,
    #         "resourcetype": "CategoricalAttribute"
    #     },
    #     "extra": {},
    #     "resourcetype": "CategoricalFilter"
    # }

Adding policies to roles using the API
######################################

Now we are ready to add the roles. As we did during the policy creation for actions and scopes, we can add one or
more policies directly to the roles, and we can add/remove them later on. We will use the
:ref:`roles_add_policies_endpoint` and :ref:`roles_delete_policies_endpoint` endpoints to demonstrate.

.. code-block:: python

    role_read_everything = django_client.post("/flex_abac/roles/",
                                    {
                                        "name": "Role Read Everything",
                                        "policies": [
                                            policy_read_everything.data["pk"]
                                        ]
                                    }, format="json")

    print(role_read_everything.status_code)
    # 201
    print(json.dumps(role_read_everything.data, indent=4))
    # {
    #     "pk": 1,
    #     "name": "Role Read Everything",
    #     "policies": [
    #         {
    #             "pk": 1,
    #             "name": "Policy Read Everything",
    #             "actions": [
    #                 {
    #                     "name": "document__read",
    #                     "pretty_name": "Can read documents (updated)",
    #                     "models": [],
    #                     "pk": 7
    #                 }
    #             ],
    #             "scopes": []
    #         }
    #     ]
    # }

We do the same for the rest of the roles.

.. code-block:: python

    role_read_odd_brands = django_client.post("/flex_abac/roles/",
                                    {
                                        "name": "Role Read Odd Brands",
                                        "policies": [
                                            policy_read_odd_brands.data["pk"]
                                        ]
                                    }, format="json")

    print(role_read_odd_brands.status_code)
    # 201

    role_write_odd_brands = django_client.post("/flex_abac/roles/",
                                    {
                                        "name": "Role Write Odd Brands",
                                        "policies": [
                                            policy_write_odd_brands.data["pk"]
                                        ]
                                    }, format="json")

    print(role_write_odd_brands.status_code)
    # 201

    role_read_even_categories = django_client.post("/flex_abac/roles/",
                                    {
                                        "name": "Role Read Even Categories",
                                        "policies": [
                                            policy_read_even_categories.data["pk"]
                                        ]
                                    }, format="json")

    print(role_read_even_categories.status_code)
    # 201

Creating everything at once
***************************

It is also possible to create the whole set of roles/policies/actions/filters at once, by providing the nested
information as we did in the last section but adding a new level. We can even mix new policies, actions, or
filters with existing ones.

.. code-block:: python

    response = django_client.post("/flex_abac/roles/",
                    {
                        "name": "Role Create All At Once",
                        "policies": [
                            {
                                "name": "Policy Create All At Once",
                                "actions": [
                                    { "name": "Dummy all at once",
                                      "pretty_name": "This is just a test of an action",
                                    },
                                    action_read.data["pk"]
                                ],
                                "scopes": [
                                    {
                                        "resourcetype": "CategoricalFilter",
                                        "value": -1,
                                        "attribute_type": attribute_brand.data["pk"]
                                    },
                                    {
                                        "resourcetype": "CategoricalFilter",
                                        "value": -1,
                                        "attribute_type": attribute_category.data["pk"]
                                    },
                                    filter_brands[1].data["pk"]
                                ]
                            },
                            policy_read_everything.data["pk"]
                        ]
                    }, format="json")

    print(response.status_code)
    # 201

Adding users to roles using the API
###################################

Users can be added in a similar fashion as in the above examples, in this case using the :ref:`users_endpoint` for
setting the whole set of roles associated to an user. We can also add/remove roles for a user by using the
:ref:`users_add_roles_endpoint` and :ref:`users_delete_roles_endpoint` endpoints.

.. code-block:: python

    response = django_client.put(
                    f"/flex_abac/users/{susan.id}/",
                    {
                        "roles": [
                          role_read_odd_brands.data["pk"],
                          role_read_even_categories.data["pk"]
                       ]
                    }, format="json")

    print(response.status_code)
    # 200

    print(json.dumps(response.data, indent=4))
    # {
    #     "pk": 34,
    #     "username": "Susan",
    #     "email": "",
    #     "is_staff": false,
    #     "roles": [
    #         {
    #             "pk": 2,
    #             "name": "Role Read Odd Brands",
    #             "policies": [
    #                 ...
    #             ]
    #         },
    #         {
    #             "pk": 4,
    #             "name": "Role Read Even Categories",
    #             "policies": [
    #                 {
    #                     ...
    #                 }
    #             ]
    #         }
    #     ]
    # }

It is also possible to create the role as it is provided to the user by following the same steps above for the other
elements.

Additional endpoints
---------------------

Apart from the endpoints which directly interact with the configuration of the permission system, other endpoints are
provided mainly to help in the implementation of a management frontend, such as the example in example/frontend.

.. _get_all_allowed_values:

Getting all allowed values per attribute and user
#################################################

More info on this endpoint is provided here: :ref:`attribute_get_all_allowed_values_endpoint`.

The purpose of this endpoint is to provide all allowed values the logged in user can access, given a specific
attribute. This endpoint enables the frontend to configure filter fields, only displaying filter values that
are within the user's scope.

For instance:

.. code-block:: python

    django_client.force_authenticate(user=susan)

    response = django_client.get(
                f'/flex_abac/attribute-types/{brand_attribute.data["pk"]}/get_all_allowed_values/'
               )
    print(json.dumps(response.data, indent=4))

    # [
    #     {
    #         "pk": 6,
    #         "value": "1",
    #         "extra": {},
    #         "resourcetype": "CategoricalFilter"
    #     },
    #     {
    #         "pk": 7,
    #         "value": "3",
    #         "extra": {},
    #         "resourcetype": "CategoricalFilter"
    #     }
    # ]

We observe that values 1 and 3 have been obtained as a result. The content in the ``extra`` field will depend on the
configured serializer (as described in :ref:`custom_serializers`).

Getting all allowed values per user
#################################################

More info on this endpoint is provided here: :ref:`users_get_all_allowed_values_endpoint`.

This endpoint is similar to '/flex_abac/attribute-types/<attribute-pk>/get_all_allowed_values/', but
instead of providing all the allowed values for an attribute, it lists all the allowed values for a user-model pair.
It receives as a parameter the model for
which we want to know the allowed values.

For instance, to gather the attributes for the model document and category (none at the moment):

.. code-block:: python

    response = django_client.get("/flex_abac/users/get_all_allowed_values/",
                                { "models": "exampleapp.document,exampleapp.category"})
    print(json.dumps(response.data, indent=4))
    # [
    #     {
    #         "pk": 8,
    #         "value": "2",
    #         "attribute_type": {
    #             "pk": 2,
    #             "name": "Category attribute",
    #             "field_name": "category__id",
    #             "class_name": "exampleapp.document",
    #             "serializer": "flex_abac.serializers.default.CategoricalSerializer",
    #             "extra_fields": null,
    #             "resourcetype": "CategoricalAttribute"
    #         },
    #         "extra": {},
    #         "resourcetype": "CategoricalFilter"
    #     },
    #     {...},
    #     {...},
    #     {...}
    # ]

.. _get_all_possible_values:

Getting all possible values
###########################

More info on this endpoint is provided here: :ref:`attribute_possible_values_endpoint`.

Also, it will be necessary to list all possible values that can be filtered, for a given attribute. The idea of this
endpoint is to provide all the possible objects which can be used to construct a scope filter for that attribute. The main
advantage is that these values are provided with a shape which allows inserting them back to the database as
filters.

.. note::

   Please have in mind that in a situation like an example provided for Brand and Category models, which are foreign keys
    of the Document model, just the linked instances will be shown. To gather the complete list of values
    in such a case, you should extend the default serializer as explained in :ref:`custom_serializers`.

For instance, we can gather all the brands which are linked to a document in the database.

.. code-block:: python

    possible_brand_filters = django_client.get(
                                f'/flex_abac/possible-values/{brand_attribute.data["pk"]}/'
                             )

    print(json.dumps(possible_brand_filters.data, indent=4))
        # {
        #     "possible_values": [
        #         {...},
        #         {
        #             "value": 3,
        #             "extra": {},
        #             "attribute_type": {
        #                 "pk": 1,
        #                 "name": "Brand attribute",
        #                 "field_name": "brand__id",
        #                 "class_name": "exampleapp.document",
        #                 "serializer": "flex_abac.serializers.default.CategoricalSerializer",
        #                 "extra_fields": null,
        #                 "resourcetype": "CategoricalAttribute"
        #             },
        #             "resourcetype": "CategoricalFilter"
        #         },
        #         {...}
        #     ],
        #     "field_type": "AutoField",
        #     "resourcetype": "CategoricalAttribute"
        # }

We can then use this information to add a new filter:

.. code-block:: python

    new_filter = django_client.post("/flex_abac/attribute-filters/",
                                    possible_brand_filters.data["possible_values"][1],
                                    format="json")
    print(new_filter.status_code)
    #201

.. _get_all_active_attributes:

Getting all the active attributes for a policy
##############################################

More info on this endpoint is provided here: :ref:`policy_get_all_active_attributes_endpoint`.

When providing a frontend for the construction of the scopes in a policy, it might be helpful to have a list of
models related to an action that can be used to filter out all the attributes which might not be related to the
current policy, to reduce the list of shown attributes. This list of models is added to actions as described
at the end of section :ref:`creating_the_actions_for_the_rbac`.

For instance, we can create a policy with an action with associated models as done here:

.. code-block:: python

    new_policy = django_client.post("/flex_abac/policies/",
                                    {
                                        "name": "Policy for which we want to Check Attributes",
                                        "actions": [ {
                                            "pretty_name": "Some action with models",
                                            "name": "some__action__with__models",
                                            "models": [ 10 ]
                                        } ],
                                        "scopes": [ ]
                                    }, format="json")
    print(new_policy.status_code)
    # 201

    response = django_client.get(
                f'/flex_abac/policies/{new_policy.data["pk"]}/get_all_active_attributes/')
    print(json.dumps(response.data, indent=4))
    # {
    #     "pk": 7,
    #     "attributes": [
    #         {
    #             "pk": 1,
    #             "name": "Brand attribute",
    #             "field_name": "brand__id",
    #             "class_name": "exampleapp.document",
    #             "serializer": "flex_abac.serializers.default.CategoricalSerializer",
    #             "extra_fields": null,
    #             "resourcetype": "CategoricalAttribute"
    #         },
    #         {
    #             "pk": 2,
    #             "name": "Category attribute",
    #             "field_name": "category__id",
    #             "class_name": "exampleapp.document",
    #             "serializer": "flex_abac.serializers.default.CategoricalSerializer",
    #             "extra_fields": null,
    #             "resourcetype": "CategoricalAttribute"
    #         }
    #     ]
    # }


.. _metapermissions_intro:

Adding permissions to the django-flex-abac's REST API
-----------------------------------------------------

These endpoints allow to modify the effective permissions, so it wouldn't be safe to allow anyone to access them.

Because of that, these endpoints provide their own permissions mechanism based on django-flex-abac. To activate
them, you would need to set the variable ``USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS`` to ``True`` in your settings.py
configuration.

Then, you will need to load the attributes, policies, filters, etc. related to flex-abac into your database. This
can be done through the following command:

.. code-block:: console

    usage: manage.py load_flex_abac_data [-h] \
                                         [--add_admin_users ADMIN_USERS [ADMIN_USERS ...]] \
                                         [--add_viewer_users VIEWER_USERS [VIEWER_USERS ...]] \
                                         [--clean_users]

    Loads initial data required to make the permissions system work.

    optional arguments:
      -h, --help            show this help message and exit
      --add_admin_users ADMIN_USERS [ADMIN_USERS ...]
                            Adds the flex-abac admin role to the provided users.
      --add_viewer_users VIEWER_USERS [VIEWER_USERS ...]
                            Adds the flex-abac viewer role to the provided users.
      --clean_users         Removes flex-abac roles for all users.

This command will load the required permissions, creating two roles:

* ``flex-abac Viewer Role``: Allows listing the permissions through the REST API (except those related to
    django-flex-abac itself), but does not allow modifying them.
* ``flex-abac Admin Role``: It also allows modifying the permissions through the REST API (except those related to
    django-flex-abac itself).

There are three additional parameters:

* ``--add_admin_users``: allows adding certain users directly to the ``flex-abac Admin Role``. They are added to the
  existing ones.
* ``--add_viewer_users``: allows adding certain users directly to the ``flex-abac Viewer Role``. They are added to the
  existing ones.
* ``--clean_users``: Detach all users from the ``flex-abac Admin Role`` and ``flex-abac Viewer Role``, so just the provided
  users will be attached to the roles.

If for some reason we want specific behavior, like just being able to modify the policies but not actions or attributes,
you can check the ``flex_abac/utils/load_flex_abac_data.py`` file to modify the existing policies or create additional
ones. For instance, you could try to remove the actions related to the "action", "basefilter" and "baseattribute" model
names so just actions related to the rest of the models are available. Or create new ones using the existing policies as
a reference.

If by accident you removed/modified one of these permissions, it is possible to launch the command again and everything
should be restored to normal.

What's next?
------------

See more usage examples with different attribute types and fields by checking the tests at
``flex_abac/tests/views/test_permissionsview.py``.

Check the :ref:`advanced_usage` documentation to check more advanced usage you can apply on ViewSets/Views.

More uses cases
---------------

Additional use cases and how they are solved are presented in the file
https://github.com/batvoice-org/django-flex-rbac/blob/main/flex_abac/tests/views/test_permissionsview.py
