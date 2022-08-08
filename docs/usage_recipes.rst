.. _usage_recipes:

Usage Recipes
=============

To help you climb the learning curve, we provide a few recipes for applying permissions to your application.

Let's imagine that your application is composed of several modules. Some modules can be accessed by
clients, other modules can be accessed by managers.

We also want to add finer-grained access control over the document objects in our app on the basis of the document's "category".

Action names generator (example)
--------------------------------

In our example, we want the actions to be related to the module, and not in the queryset model as done by default.
For that reason, we create the following action name generator, which inherits from ``GroupedMethodActionNameGenerator``:

.. code-block:: python

    from flex_abac.utils.action_names import GroupedMethodActionNameGenerator

    class ModuleActionNameGenerator(GroupedMethodActionNameGenerator):

        @classmethod
        def get_action_name(cls, view):
            module_name = "client"                         # By default, we are providing the "client" module name
            if getattr(view, "module_name", None):
                module_name = view.module_name

            return f"{cls.get_module_name(view)}__{cls.get_method_type(view)}"

Basic permissions (example)
---------------------------

The first recommendation is to extend the default CustomPermissions to create specific permissions for each of the
permissions needed on each part of your application.

Based on the provided example, we could have something like this:

.. code-block:: python

    from flex_abac.permissions import CanExecuteMethodPermission

    class AppBasePermission(CanExecuteMethodPermission):
        """
            Updates the permissions based on the module we are working on
        """

        # We will override this method so in each case we apply the proper module name and action name generator
        @classmethod
        def _update_view(cls, view):
            raise NotImplementedError()

        def has_permission(self, request, view=None):
            view = self._update_view(view)
            return super().has_permission(request, view=view)

        def has_object_permission(self, request, view=None, obj=None):
            view = self._update_view(view)
            return super().has_object_permission(request, view=view, obj=obj)


    class ClientModulePermission(CWBasePermission):
        """
            Permissions for the client module
        """
        @classmethod
        def _update_view(cls, view):
            view.module_name = "client"
            view.flex_abac_action_name = ModuleActionNameGenerator

            return view


    class ManagerModulePermission(CWBasePermission):
        """
            Permissions for the manager module
        """
        @classmethod
        def _update_view(cls, view):
            view.module_name = "manager"
            view.flex_abac_action_name = ModuleActionNameGenerator

            return view

Applying permissions to endpoints created with a ViewSet (example)
------------------------------------------------------------------

It is easy to include these custom permissions on a ViewSet:

.. code-block:: python

    # Filtering is done by default by the mixin
    from flex_abac.mixins import ApplyFilterMixin

    class ClientDocumentsViewSet(ApplyFilterMixin, viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, ClientModulePermission]
        serializer_class = DocumentSerializer
        queryset = Document.objects

        # We also might need this (check the example on section Advanced Usage -> Changing the default attribute mapping.
        # attribute_mapping = CustomAttributeMappingGenerator()


    class ManagerDocumentsViewSet(ApplyFilterMixin, viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, ClientModulePermission]
        serializer_class = DocumentSerializer
        queryset = Document.objects

        # We also might need this (check the example on section Advanced Usage -> Changing the default attribute mapping.
        # attribute_mapping = CustomAttributeMappingGenerator()

Applying permissions to endpoints created with a View
-----------------------------------------------------

.. code-block:: python

    class DocumentsListView(ListAPIView):

        permission_classes = [IsAuthenticated, ClientPermission]

        # We also might need this (check the example on section Advanced Usage -> Changing the default attribute mapping.
        # attribute_mapping = CustomAttributeMappingGenerator()

        queryset = Document.objects
        serializer_class = DocumentSerializer

        # Example of how we could apply filtering (done by default by the mixin)
        def filter_queryset(self, queryset):
            objects = Call.objects

            valid_filter = get_filter_for_valid_objects(
                                self.request.user,
                                Document,
                                action_name=get_action_name(self)     # Included in the custom ModuleActionNameGenerator
                                                                      # we created at the beginning of this section
                                )
            return queryset.filter(valid_filter)


Applying permissions to a simple view function
----------------------------------------------

.. code-block:: python

    @flex_abac_params_api_view(flex_abac_action_name="client__read")
    @api_view(["GET"])
    @permission_classes([IsAuthenticated, AudioAgentClientPermission])
    def document_view(request, document_id=None, **kwargs):
        # If it is not allowed, an exception is triggered
        if not can_user_do(action_name="client__read", user=request.user, obj=document_object):
            return HttpResponseForbidden("You don't have permissions!!!")

        ...


More uses cases
---------------

Additional use cases and how they are solved are presented in the file
https://github.com/batvoice-org/django-flex-rbac/blob/main/example/backend/exampleapp/views/example_view.py
