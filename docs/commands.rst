Commands
=========

import_attributes
-------------------

Imports attributes from a given yaml file. For an example of a yaml file, check
:meth:`flex_abac.utils.import_attributes.import_from_yaml`

.. code-block:: console

    usage: manage.py import_attributes [-h] --yaml-path YAML_PATH

    Imports attributes

    optional arguments:
      -h, --help            show this help message and exit
      --yaml-path YAML_PATH
                            Path to yaml containing data to load

.. _load_flex_abac_data:


load_flex_abac_data
-------------------

Loads the necessary permissions in the database to restrict permissions to the users for the provided
REST API.

It creates several attributes, filters, actions, policies, and roles, which are easily recognized through the
name, which starts with ``flex-abac``.

To make these permissions functional, the settings variable ``USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS``
should be set to ``True``.

There are two special roles, ``flex-abac Admin Role`` and ``flex-abac Viewer Role``, which allow assigned users
to admin and to read the flex-abac related permissions, respectively. Users can be easily assigned to these
roles through the ``admin_users`` and ``viewer_users`` variables. By default, superusers will be added to the
``admin_users`` role.

.. note::

    If you accidentally partially/fully removed the flex-abac permissions from the database, you can restore
    them at any moment using this function.

For additional information, check :meth:`flex_abac.utils.load_flex_abac_data.load_flex_abac_data`.

.. code-block:: console

    usage: manage.py load_flex_abac_data [-h] [--add_admin_users ADMIN_USERS [ADMIN_USERS ...]] [--add_viewer_users VIEWER_USERS [VIEWER_USERS ...]] [--clean_users]
    Loads initial data required to make the permissions system work.

    optional arguments:
      -h, --help            show this help message and exit
      --add_admin_users ADMIN_USERS [ADMIN_USERS ...]
                            Adds the flex-abac admin role to the provided users.
      --add_viewer_users VIEWER_USERS [VIEWER_USERS ...]
                            Adds the flex-abac viewer role to the provided users.
      --clean_users         Removes flex-abac roles for all users.
