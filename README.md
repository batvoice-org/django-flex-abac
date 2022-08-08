# django-flex-rbac
Standalone Django app for flexible, parameterized Role-Based Access Control.
<!-- django-flex-abac documentation master file, created by
sphinx-quickstart on Tue Sep 14 10:57:09 2021.
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive. -->

**django-flex-abac** is a Python library for a generic, easy to use,
application of an Attribute-Role-based access control system
(https://en.wikipedia.org/wiki/Attribute-based_access_control).
Main strengths of the library are listed next:

- Generic model attributes can be defined.
- Permissions can be defined on database, allowing users to easily manage access control.
- API endpoints for the management of permissions.
- High flexibility.
- Easy integration with Django and Django REST Framework viewsets, views and functions.

Attribute-based access control a.k.a policy-based access control is a paradigm for access control which defines a
combination of the following:

- User (subject) attributes
- Environmental attributes, like organizational threat levels
- Resource (object) attributes: creation date, resource owner, file name, data sensitivity, etc.

``django-flex-abac`` defines a flexible environment for permissions management based on Django and Django REST Framework.
Permissions are computed as a combination of policies, which are defined by sets of actions and filters, which define
the scope of the objects an user can access to. Policies are configured directly as elements in database, so it is easy
to re-define them or create new ones without touching a line of code.

Policies are assigned to roles, which are then assigned to the users. Effective permissions for an user will be computed
as the combination of policies associated to the roles a user belongs to.

## License

This project is released under the [BSD-3 license](https://opensource.org/licenses/BSD-3-Clause)

## Building the documentation

If you want to read the documentation for this project, do as follows:

```bash
pip install -e .[doc]
cd docs
make html
```

Then you can open `docs/_build/html/index.html` and start checking the documentation.


## F.A.Q.

###Is the project production ready?

- This project is under active development and not all features have been fully tested. Use it at your own risk.
- Please note that on some points and until version 1.0, we will tune things and change the way it works to find the most flexible way to operate. That means that updates may break things.
- Feel free to review changes, report issues and propose new features at any moment.

###Can I contribute?

- We accept contributions of every kind: documentation, code, artwork. Any help is greatly appreciated.
- We keep the source code on GitHub and take contributions through GitHub pull requests.
- For smaller patches and bug fixes just go ahead and either report an issue or submit a pull request.
- It is usually a good idea to discuss major changes with the developers, this will help us determine whether the contribution would be a good fit for the project and if it is likely to be accepted.

