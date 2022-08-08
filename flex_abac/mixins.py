from flex_abac.checkers import get_filter_for_valid_objects

from flex_abac.utils.mappings import get_mapping_from_viewset
from flex_abac.utils.action_names import get_action_name

from django.db.models.expressions import Q

from django.shortcuts import get_object_or_404

class ApplyFilterMixin(object):
    """
    Applies default filtering and permissions to a View, for convenience.

    Usage example:

    .. code-block:: python

        class RetrieveDocumentsViewSet(ApplyFilterMixin, viewsets.ModelViewSet):
            serializer_class = DocumentSerializer
            queryset = Document.objects

            @action(detail=False, methods=["GET"])
            def filter(self, request, *args, **kwargs):
                return Response("example action")
    """

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)

        return obj

    def filter_queryset(self, queryset):
        attribute_mapping = get_mapping_from_viewset(self)

        action_name = get_action_name(self)
        base_model = getattr(self, "base_model", queryset.model)

        base_lookup_name = getattr(self, "base_lookup", None)

        valid_filter = get_filter_for_valid_objects(self.request.user, base_model,
                                                    base_lookup_name=base_lookup_name,
                                                    action_name=action_name)

        if attribute_mapping and queryset.model in attribute_mapping.keys():
            for attribute_name, attribute_filters in attribute_mapping[queryset.model].items():
                additional_filter = Q()
                for attribute_filter in attribute_filters:
                    additional_filter |= Q(**{attribute_name: attribute_filter})
                valid_filter &= additional_filter

        return queryset.filter(valid_filter)
