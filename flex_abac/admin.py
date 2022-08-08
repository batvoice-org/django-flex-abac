from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from .models import (
    Role,
    UserRole,
    RolePolicy,
    Policy,
    PolicyAction,
    Action,
    PolicyGenericFilter,
    PolicyCategoricalFilter,
    PolicyNestedCategoricalFilter,
    PolicyMaterializedNestedCategoricalFilter,
    ModelCategoricalAttribute,
    ModelGenericAttribute,
    ModelNestedCategoricalAttribute,
    ModelMaterializedNestedCategoricalAttribute,
    BaseAttribute,
    GenericAttribute,
    CategoricalAttribute,
    NestedCategoricalAttribute,
    MaterializedNestedCategoricalAttribute,
    GenericFilter,
    CategoricalFilter,
    NestedCategoricalFilter,
    MaterializedNestedCategoricalFilter,
)


class ModelGenericAttributeInline(admin.StackedInline):
    model = ModelGenericAttribute
    extra = 0
    fields = ['owner_object_id']


class ModelCategoricalAttributeInline(admin.StackedInline):
    model = ModelCategoricalAttribute
    extra = 0
    fields = ['owner_object_id']


class ModelNestedCategoricalAttributeInline(admin.StackedInline):
    model = ModelNestedCategoricalAttribute
    extra = 0
    fields = ['owner_object_id']


class ModelMaterializedNestedCategoricalAttributeInline(admin.StackedInline):
    model = ModelMaterializedNestedCategoricalAttribute
    extra = 0
    fields = ['owner_object_id']


class GenericFilterInline(admin.StackedInline):
    model = GenericFilter
    extra = 0
    list_display = ('name',)


class CategoricalFilterInline(admin.StackedInline):
    model = CategoricalFilter
    extra = 0
    list_display = ('name',)


class NestedCategoricalFilterInline(admin.StackedInline):
    model = NestedCategoricalFilter
    extra = 0


class MaterializedNestedCategoricalFilterAdmin(TreeAdmin):
    model = MaterializedNestedCategoricalFilter
    form = movenodeform_factory(MaterializedNestedCategoricalFilter)
    list_display = ('value', 'get_attribute_type')
    extra = 0

    def get_attribute_type(self, obj):
        return obj.attribute_type.name

    get_attribute_type.short_description = 'Materialized Nested Categorical Attribute Type'
    get_attribute_type.admin_order_field = 'attribute_type__name'


class BaseAttributeChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = BaseAttribute
    list_display = ('name',)


@admin.register(GenericAttribute)
class GenericAttributeAdmin(BaseAttributeChildAdmin):
    base_model = GenericAttribute
    show_in_index = False
    inlines = (ModelGenericAttributeInline, GenericFilterInline,)


@admin.register(CategoricalAttribute)
class CategoricalAttributeAdmin(BaseAttributeChildAdmin):
    base_model = CategoricalAttribute
    show_in_index = False
    inlines = (ModelCategoricalAttributeInline, CategoricalFilterInline,)


@admin.register(NestedCategoricalAttribute)
class NestedCategoricalAttributeAdmin(BaseAttributeChildAdmin):
    base_model = NestedCategoricalAttribute
    show_in_index = False
    inlines = (ModelNestedCategoricalAttributeInline, NestedCategoricalFilterInline,)


@admin.register(MaterializedNestedCategoricalAttribute)
class MaterializedNestedCategoricalAttributeAdmin(BaseAttributeChildAdmin, TreeAdmin):
    base_model = MaterializedNestedCategoricalAttribute
    form = movenodeform_factory(MaterializedNestedCategoricalAttribute)
    show_in_index = False
    inlines = (ModelMaterializedNestedCategoricalAttributeInline,)


@admin.register(BaseAttribute)
class BaseAttributeParentAdmin(PolymorphicParentModelAdmin):
    base_model = BaseAttribute
    child_models = (
        GenericAttribute,
        CategoricalAttribute,
        NestedCategoricalAttribute,
        MaterializedNestedCategoricalAttribute
    )
    list_filter = (PolymorphicChildModelFilter,)
    list_display = ('name',)


class PolicyGenericFilterInline(admin.StackedInline):
    model = PolicyGenericFilter
    extra = 0


class PolicyCategoricalFilterInline(admin.StackedInline):
    model = PolicyCategoricalFilter
    extra = 0


class PolicyNestedCategoricalFilterInline(admin.StackedInline):
    model = PolicyNestedCategoricalFilter
    extra = 0


class PolicyMaterializedNestedCategoricalFilterInline(admin.StackedInline):
    model = PolicyMaterializedNestedCategoricalFilter
    extra = 0


class ActionInline(admin.StackedInline):
    model = PolicyAction
    extra = 0


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    inlines = (
        ActionInline,
        PolicyGenericFilterInline,
        PolicyCategoricalFilterInline,
        PolicyNestedCategoricalFilterInline,
        PolicyMaterializedNestedCategoricalFilterInline,
    )
    model = Policy
    list_display = ('name',)


class PolicyInline(admin.StackedInline):
    model = RolePolicy
    extra = 0


@admin.register(Role)
class PolicyAdmin(admin.ModelAdmin):
    inlines = (PolicyInline, )
    model = Role
    list_display = ('name',)


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    model = Action
    list_display = ('pretty_name', 'name',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    model = UserRole
    list_display = ('user', 'get_role')

    def get_role(self, obj):
        return obj.role.name

    get_role.short_description = 'Role'
    get_role.admin_order_field = 'role__name'
