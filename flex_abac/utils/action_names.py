from flex_abac.utils.helpers import import_from
from django.conf import settings

class ActionNameGenerator:
    @classmethod
    def get_model_name(cls, view):
        try:
            return view.get_queryset().model.__name__.lower()
        except AttributeError as ae1:
            try:
                return view.queryset.model.__name__.lower()
            except AttributeError as ae2:
                raise AttributeError(f"{str(ae1)}, {str(ae2)}")

    @classmethod
    def get_action_from_view(cls, view):
        return view.action.lower() if view.action else ""

    @classmethod
    def get_method_from_view(cls, view):
        return view.request.method.lower() if view.request.method else ""

    @classmethod
    def get_action_name(cls, view):
        raise NotImplementedError


class ModelActionNameGenerator(ActionNameGenerator):
    @classmethod
    def get_action_name(cls, view):
        return f"{cls.get_model_name(view)}__{cls.get_action_from_view(view)}"


class MethodAndTypeActionNameGenerator(ActionNameGenerator):
    @classmethod
    def get_action_name(cls, view):
        return f"{cls.get_model_name(view)}__{cls.get_action_from_view(view)}__{cls.get_method_from_view(view)}"


class GroupedMethodActionNameGenerator(ActionNameGenerator):
    READ_METHODS = ["get", "head", "trace", "options"]
    WRITE_METHODS = ["post", "put", "delete", "patch", "connect"]

    @classmethod
    def get_method_type(cls, view):
        if cls.get_method_from_view(view) in cls.READ_METHODS:
            return "read"
        elif cls.get_method_from_view(view) in cls.WRITE_METHODS:
            return "write"
        else:
            raise ValueError(f"Unknown HTTP method name: {cls.get_method_from_view(view)}")

    @classmethod
    def get_action_name(cls, view):
        return f"{cls.get_model_name(view)}__{cls.get_method_type(view)}"

DefaultActionNameGenerator = import_from(getattr(settings, "DEFAULT_ACTION_NAME_GENERATOR",
                                                 "flex_abac.utils.action_names.GroupedMethodActionNameGenerator"))


def get_action_name(view):
    flex_abac_action_name = getattr(view, "flex_abac_action_name", None)
    if not flex_abac_action_name and "flex_abac_action_name" in view.kwargs.keys():
        flex_abac_action_name = view.kwargs["flex_abac_action_name"]

    if flex_abac_action_name:
        if isinstance(flex_abac_action_name, type) and issubclass(flex_abac_action_name, ActionNameGenerator):
            return flex_abac_action_name.get_action_name(view)
        else:
            return flex_abac_action_name.lower()
    else:
        return DefaultActionNameGenerator.get_action_name(view)