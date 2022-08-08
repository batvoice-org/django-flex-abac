from django.db import models
from django.contrib.auth.models import User

from polymorphic.models import PolymorphicModel

from flex_abac.models.base_filter import BaseFilter
from django.core.exceptions import FieldDoesNotExist
from jsonfield import JSONField
from django.contrib.auth.models import User


class BaseAttribute(PolymorphicModel):
    """
    All attribute types inherit from this model.
    """

    name = models.CharField(max_length=100, unique=True)
    field_name = models.CharField(max_length=512, null=False)

    serializer = models.CharField(max_length=512, null=True, blank=True,
                                  default="flex_abac.serializers.default.BaseValuesSerializer")

    extra_fields = JSONField(null=True)

    class Meta:
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'


    @classmethod
    def import_from_dict(cls, content_dict: dict):
        raise NotImplementedError

    @classmethod
    def print_all(cls):
        raise NotImplementedError

    @classmethod
    def get_all_to_check_for_model(cls, model):
        """
        content_type = ContentType.objects.get_for_model(model)
        return cls.objects.filter(
            id__in=Subquery(
                ModelBaseAttribute.objects.filter(
                    owner_object_id=content_type.pk
                ).values('attribute_type_id')
            )
        )
        """
        raise NotImplementedError

    # TODO: Add comments
    def get_filter(self, policy):
        raise NotImplementedError

    # TODO: Add comments
    def get_attribute_value(self, value):
        raise NotImplementedError

    def is_represented_in_query_values(self, query_attribute_values):
        """
        Returns a boolean indicating whether the attribute type is referenced
        by one of `query_attribute_values`, either directly or via an ancestor
        of the attribute type
        :param query_attribute_values: attribute values in a query
        :return:
        """
        raise NotImplementedError

    def does_match(self, obj, policy):
        """
        Returns a boolean indicating whether the policy's scope
        includes the provided object's value (obj.value)
        :param obj: the access-controlled object
        :param policy: a policy
        :return: Boolean
        """

        # TODO: Update this documentation
        """
        object_values = BaseFilter.objects.filter(
            attribute_type=self,
            id__in=Subquery(
                ItemAttributeValue.objects.filter(
                    owner_content_type=ContentType.objects.get_for_model(type(obj)),
                    owner_object_id=obj.id
                ).values('value_id')
            )
        )
        if not object_values.count():
            return False

        matching_scope_values = policy.get_attribute_values(AttributeValue).filter(
            id__in=Subquery(object_values.values('id'))
        )
        if not matching_scope_values.count():
            return False
        """

        return False


    # TODO: Add comments
    def get_content_type(self):
        raise NotImplementedError

    # TODO: Add comments
    def get_model(self):
        content_type = self.get_content_type()
        return content_type.model_class()


    # TODO: Add comments
    def find_field_in_model(self, as_path=True):
        model = self.get_model()

        lookups = list(reversed(self.field_name.split("__")))
        field = None

        field_path = []
        while model and lookups:
            current = lookups.pop()
            field = model._meta.get_field(current)

            field_path.append(current)

            model = field.related_model

            if lookups and model is None:
                if field.get_lookup(lookups[-1]):
                    return "__".join(field_path) if as_path else field.get_internal_type()
                else:
                    raise FieldDoesNotExist(self.field_name)

        return "__".join(field_path) if as_path else field.get_internal_type()

    def get_values(self):
        raise NotImplementedError

    def is_scope_empty_for_user(self, FilterClass, user, action_name=None):
        if not isinstance(user, User):
            user = User.objects.get(pk=user)

        user_policies = user.get_policies(). \
            filter(action__name=action_name). \
            exclude(role__name__in=("flex-abac Admin Role", "flex-abac Viewer Role"))

        for user_policy in user_policies:
            policy_filters = FilterClass.objects.filter(attribute_type=self, policies=user_policy)
            if not policy_filters.exists():
                return user_policy

        return None

    def get_all_values_for_user(self, user):
        return BaseFilter.objects.filter(policies__roles__users=user, attribute_type=self)

    def __str__(self):
        return '<BaseAttribute:{}>'.format(self.name)
