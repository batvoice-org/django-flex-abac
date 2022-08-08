.. django-flex-abac documentation master file, created by
   sphinx-quickstart on Tue Sep 14 10:57:09 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-flex-abac's documentation!
============================================

**django-flex-abac** is a Python library for a generic, easy to use,
application of an Attribute-Role-based access control system
(https://en.wikipedia.org/wiki/Attribute-based_access_control).
The main strengths of the library are listed next:

- Generic model attributes can be defined.
- Permissions can be defined on a database, allowing users to easily manage access control.
- API endpoints for the management of permissions.
- Extensible, flexible attributes: attributes can be numerical, dates, categories, trees, etc.
- High flexibility.
- Progressive: you can use this library to implement a basic, attribute-less role-based access control (RBAC)
  system, and easily add attributes later on once your project requires it.
- Easy integration with Django and Django REST Framework Viewsets, Views, and functions.

Attribute-based access control a.k.a policy-based access control is a paradigm for access control that defines a
combination of the following:

- User (subject) attributes
- Environmental attributes, like organizational threat levels
- Resource (object) attributes: creation date, resource owner, file name, data sensitivity, etc.

``django-flex-abac`` defines a flexible environment for permissions management based on Django and Django REST Framework.
Thanks to this flexibility it is possible to build a Role-Based Access Control (RBAC), as well as an Attribute-Based
Access Control (ABAC), or a combination of both (Attribute-Role-Based Access Control, ARBAC). Roles are assigned to users,
and roles can reference the attributes over which we need to define the permissions.

Permissions are computed as a combination of policies, which are defined by sets of actions and filters, which define
the scope of the objects a user can access to. Policies are configured directly as elements in the database, so it is easy
to re-define them or create new ones without touching a line of code.

Policies are assigned to roles, which are then assigned to the users. Effective permissions for a user will be computed
as the combination of policies associated with the roles a user belongs to.

- If you want install information, check :doc:`installation`.
- To know the concepts of the library, check :doc:`concepts`.
- If you just want to start managing users, check :doc:`getting_started`.
- If you want to add permissions to your endpoints, check the :doc:`usage_recipes`.


.. note::

   This project is under active development.

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

   self
   installation
   getting_started
   concepts
   usage_recipes
   getting_started_with_rest_api
   advanced_usage
   commands
   attribute_types
   additional_functions
   rest_api
   known_caveats
   faq
   genindex

