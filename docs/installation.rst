Installation
=============

There are several ways to install django-flex-abac. If you’re not sure, just use pip.

pip (or easy_install)
---------------------

You can install the release versions from django-flex-abac’s PyPI page using pip:

.. code-block:: console

   pip install django-flex-abac

or if for some reason you can’t use pip, you can try easy_install, (at your own risk):

.. code-block:: console

   easy_install --always-unzip django-flex-abac

setup.py
********

Download a release from the django-flex-abac download page and unpack it, then run:

.. code-block:: console

   python setup.py install

Configuration
--------------

settings.py
***********

Add the following requirements to the installed apps.

.. code-block:: python

   INSTALLED_APPS = [
       'flex_abac',
       'polymorphic',
       'treebeard',
   ]

urls.py
*******

Additionally, if you need to use the permissions management endpoint, you should add this.

.. code-block:: python

   urlpatterns += [
       path('flex_abac/', include('flex_abac.urls'))
   ]

In that case, it is recommended to set permissions on these endpoints. This can be done as follows:

#. Set ``USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS`` to ``True``.
#. Load necessary permissions data into the database using the :ref:`load_flex_abac_data` command.

.. code-block:: console

    python manage.py load_flex_abac_data --add_admin_users <list_of_users> --clean_users

``<list_of_users>`` is a list of usernames for which you want to allow permissions management. More information on this
can be found in the documentation for the :ref:`load_flex_abac_data` command.

Environment variables
*********************

* ``USE_PERMISSIONS_ON_FLEX_ARBAC_ENDPOINTS``: False by default, but recommended to True. Indicates whether permissions
  will also be applied to the provided permissions management REST API endpoints. To make these permissions
  work, you will need to load the necessary data as described in :ref:`load_flex_abac_data`.
* ``DEFAULT_ACTION_NAME_GENERATOR``: By default, ``flex_abac.utils.action_names.GroupedMethodActionNameGenerator``. See
  more information on this at :ref:`custom_action_names`.

Building the documentation
--------------------------

If you want to read the documentation for this project, do as follows:

.. code-block:: console

    pip install -e .[doc]
    cd docs
    make html

Then you can open `docs/_build/html/index.html` and start checking the documentation.

Launching the provided example application
------------------------------------------

The easiest way to understand the library is by launching the provided example application. To do so:

* First, launch the Django backend as usual:

.. code-block:: console

    cd example/backend
    python manage.py runserver

* Then, launch the front end. You will need to install ``node.js`` (https://nodejs.org/). This is done as follows:

.. code-block:: console

    cd example/frontend
    export VUE_APP_BACKEND_API=http://localhost:8000/flex_abac/
    export VUE_APP_BACKEND_EXAMPLE_API=http://localhost:8000/example/
    npm install
    npm run serve

Change localhost and port to the proper server and port names, if needed.


