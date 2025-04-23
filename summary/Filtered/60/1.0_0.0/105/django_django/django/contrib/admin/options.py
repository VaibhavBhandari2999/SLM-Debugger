import copy
import json
import re
from functools import partial, update_wrapper
from urllib.parse import quote as urlquote

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import helpers, widgets
from django.contrib.admin.checks import (
    BaseModelAdminChecks,
    InlineModelAdminChecks,
    ModelAdminChecks,
)
from django.contrib.admin.decorators import display
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import (
    NestedObjects,
    construct_change_message,
    flatten_fieldsets,
    get_deleted_objects,
    lookup_spawns_duplicates,
    model_format_dict,
    model_ngettext,
    quote,
    unquote,
)
from django.contrib.admin.widgets import AutocompleteSelect, AutocompleteSelectMultiple
from django.contrib.auth import get_permission_codename
from django.core.exceptions import (
    FieldDoesNotExist,
    FieldError,
    PermissionDenied,
    ValidationError,
)
from django.core.paginator import Paginator
from django.db import models, router, transaction
from django.db.models.constants import LOOKUP_SEP
from django.forms.formsets import DELETION_FIELD_NAME, all_valid
from django.forms.models import (
    BaseInlineFormSet,
    inlineformset_factory,
    modelform_defines_fields,
    modelform_factory,
    modelformset_factory,
)
from django.forms.widgets import CheckboxSelectMultiple, SelectMultiple
from django.http import HttpResponseRedirect
from django.http.response import HttpResponseBase
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.text import (
    capfirst,
    format_lazy,
    get_text_list,
    smart_split,
    unescape_string_literal,
)
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.views.decorators.csrf import csrf_protect
from django.views.generic import RedirectView

IS_POPUP_VAR = "_popup"
TO_FIELD_VAR = "_to_field"


HORIZONTAL, VERTICAL = 1, 2


def get_content_type_for_model(obj):
    """
    Retrieve the content type for a given model.
    
    This function returns the content type object for a specified model. The model can be an instance or a class. The `for_concrete_model` parameter is set to `False` to ensure that the content type is retrieved for the abstract base class if applicable.
    
    Parameters:
    obj (Model): The model instance or class for which to retrieve the content type.
    
    Returns:
    ContentType: The content type object corresponding to the provided model.
    
    Example:
    >>>
    """

    # Since this module gets imported in the application's root package,
    # it cannot import models from other applications at the module level.
    from django.contrib.contenttypes.models import ContentType

    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


def get_ul_class(radio_style):
    return "radiolist" if radio_style == VERTICAL else "radiolist inline"


class IncorrectLookupParameters(Exception):
    pass


# Defaults for formfield_overrides. ModelAdmin subclasses can change this
# by adding to ModelAdmin.formfield_overrides.

FORMFIELD_FOR_DBFIELD_DEFAULTS = {
    models.DateTimeField: {
        "form_class": forms.SplitDateTimeField,
        "widget": widgets.AdminSplitDateTime,
    },
    models.DateField: {"widget": widgets.AdminDateWidget},
    models.TimeField: {"widget": widgets.AdminTimeWidget},
    models.TextField: {"widget": widgets.AdminTextareaWidget},
    models.URLField: {"widget": widgets.AdminURLFieldWidget},
    models.IntegerField: {"widget": widgets.AdminIntegerFieldWidget},
    models.BigIntegerField: {"widget": widgets.AdminBigIntegerFieldWidget},
    models.CharField: {"widget": widgets.AdminTextInputWidget},
    models.ImageField: {"widget": widgets.AdminFileWidget},
    models.FileField: {"widget": widgets.AdminFileWidget},
    models.EmailField: {"widget": widgets.AdminEmailInputWidget},
    models.UUIDField: {"widget": widgets.AdminUUIDInputWidget},
}

csrf_protect_m = method_decorator(csrf_protect)


class BaseModelAdmin(metaclass=forms.MediaDefiningClass):
    """Functionality common to both ModelAdmin and InlineAdmin."""

    autocomplete_fields = ()
    raw_id_fields = ()
    fields = None
    exclude = None
    fieldsets = None
    form = forms.ModelForm
    filter_vertical = ()
    filter_horizontal = ()
    radio_fields = {}
    prepopulated_fields = {}
    formfield_overrides = {}
    readonly_fields = ()
    ordering = None
    sortable_by = None
    view_on_site = True
    show_full_result_count = True
    checks_class = BaseModelAdminChecks

    def check(self, **kwargs):
        return self.checks_class().check(self, **kwargs)

    def __init__(self):
        # Merge FORMFIELD_FOR_DBFIELD_DEFAULTS with the formfield_overrides
        # rather than simply overwriting.
        overrides = copy.deepcopy(FORMFIELD_FOR_DBFIELD_DEFAULTS)
        for k, v in self.formfield_overrides.items():
            overrides.setdefault(k, {}).update(v)
        self.formfield_overrides = overrides

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance.

        If kwargs are given, they're passed to the form Field's constructor.
        """
        # If the field specifies choices, we don't need to look for special
        # admin widgets - we just need to use a select widget of some kind.
        if db_field.choices:
            return self.formfield_for_choice_field(db_field, request, **kwargs)

        # ForeignKey or ManyToManyFields
        if isinstance(db_field, (models.ForeignKey, models.ManyToManyField)):
            # Combine the field kwargs with any options for formfield_overrides.
            # Make sure the passed in **kwargs override anything in
            # formfield_overrides because **kwargs is more specific, and should
            # always win.
            if db_field.__class__ in self.formfield_overrides:
                kwargs = {**self.formfield_overrides[db_field.__class__], **kwargs}

            # Get the correct formfield.
            if isinstance(db_field, models.ForeignKey):
                formfield = self.formfield_for_foreignkey(db_field, request, **kwargs)
            elif isinstance(db_field, models.ManyToManyField):
                formfield = self.formfield_for_manytomany(db_field, request, **kwargs)

            # For non-raw_id fields, wrap the widget with a wrapper that adds
            # extra HTML -- the "add other" interface -- to the end of the
            # rendered output. formfield can be None if it came from a
            # OneToOneField with parent_link=True or a M2M intermediary.
            if formfield and db_field.name not in self.raw_id_fields:
                related_modeladmin = self.admin_site._registry.get(
                    db_field.remote_field.model
                )
                wrapper_kwargs = {}
                if related_modeladmin:
                    wrapper_kwargs.update(
                        can_add_related=related_modeladmin.has_add_permission(request),
                        can_change_related=related_modeladmin.has_change_permission(
                            request
                        ),
                        can_delete_related=related_modeladmin.has_delete_permission(
                            request
                        ),
                        can_view_related=related_modeladmin.has_view_permission(
                            request
                        ),
                    )
                formfield.widget = widgets.RelatedFieldWidgetWrapper(
                    formfield.widget,
                    db_field.remote_field,
                    self.admin_site,
                    **wrapper_kwargs,
                )

            return formfield

        # If we've got overrides for the formfield defined, use 'em. **kwargs
        # passed to formfield_for_dbfield override the defaults.
        for klass in db_field.__class__.mro():
            if klass in self.formfield_overrides:
                kwargs = {**copy.deepcopy(self.formfield_overrides[klass]), **kwargs}
                return db_field.formfield(**kwargs)

        # For any other type of field, just call its formfield() method.
        return db_field.formfield(**kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Get a form Field for a database Field that has declared choices.
        """
        # If the field is named as a radio_field, use a RadioSelect
        if db_field.name in self.radio_fields:
            # Avoid stomping on custom widget/choices arguments.
            if "widget" not in kwargs:
                kwargs["widget"] = widgets.AdminRadioSelect(
                    attrs={
                        "class": get_ul_class(self.radio_fields[db_field.name]),
                    }
                )
            if "choices" not in kwargs:
                kwargs["choices"] = db_field.get_choices(
                    include_blank=db_field.blank, blank_choice=[("", _("None"))]
                )
        return db_field.formfield(**kwargs)

    def get_field_queryset(self, db, db_field, request):
        """
        If the ModelAdmin specifies ordering, the queryset should respect that
        ordering.  Otherwise don't specify the queryset, let the field decide
        (return None in that case).
        """
        related_admin = self.admin_site._registry.get(db_field.remote_field.model)
        if related_admin is not None:
            ordering = related_admin.get_ordering(request)
            if ordering is not None and ordering != ():
                return db_field.remote_field.model._default_manager.using(db).order_by(
                    *ordering
                )
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        db = kwargs.get("using")

        if "widget" not in kwargs:
            if db_field.name in self.get_autocomplete_fields(request):
                kwargs["widget"] = AutocompleteSelect(
                    db_field, self.admin_site, using=db
                )
            elif db_field.name in self.raw_id_fields:
                kwargs["widget"] = widgets.ForeignKeyRawIdWidget(
                    db_field.remote_field, self.admin_site, using=db
                )
            elif db_field.name in self.radio_fields:
                kwargs["widget"] = widgets.AdminRadioSelect(
                    attrs={
                        "class": get_ul_class(self.radio_fields[db_field.name]),
                    }
                )
                kwargs["empty_label"] = (
                    kwargs.get("empty_label", _("None")) if db_field.blank else None
                )

        if "queryset" not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs["queryset"] = queryset

        return db_field.formfield(**kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # If it uses an intermediary model that isn't auto created, don't show
        # a field in admin.
        if not db_field.remote_field.through._meta.auto_created:
            return None
        db = kwargs.get("using")

        if "widget" not in kwargs:
            autocomplete_fields = self.get_autocomplete_fields(request)
            if db_field.name in autocomplete_fields:
                kwargs["widget"] = AutocompleteSelectMultiple(
                    db_field,
                    self.admin_site,
                    using=db,
                )
            elif db_field.name in self.raw_id_fields:
                kwargs["widget"] = widgets.ManyToManyRawIdWidget(
                    db_field.remote_field,
                    self.admin_site,
                    using=db,
                )
            elif db_field.name in [*self.filter_vertical, *self.filter_horizontal]:
                kwargs["widget"] = widgets.FilteredSelectMultiple(
                    db_field.verbose_name, db_field.name in self.filter_vertical
                )
        if "queryset" not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs["queryset"] = queryset

        form_field = db_field.formfield(**kwargs)
        if (
            isinstance(form_field.widget, SelectMultiple)
            and form_field.widget.allow_multiple_selected
            and not isinstance(
                form_field.widget, (CheckboxSelectMultiple, AutocompleteSelectMultiple)
            )
        ):
            msg = _(
                "Hold down “Control”, or “Command” on a Mac, to select more than one."
            )
            help_text = form_field.help_text
            form_field.help_text = (
                format_lazy("{} {}", help_text, msg) if help_text else msg
            )
        return form_field

    def get_autocomplete_fields(self, request):
        """
        Return a list of ForeignKey and/or ManyToMany fields which should use
        an autocomplete widget.
        """
        return self.autocomplete_fields

    def get_view_on_site_url(self, obj=None):
        if obj is None or not self.view_on_site:
            return None

        if callable(self.view_on_site):
            return self.view_on_site(obj)
        elif hasattr(obj, "get_absolute_url"):
            # use the ContentType lookup if view_on_site is True
            return reverse(
                "admin:view_on_site",
                kwargs={
                    "content_type_id": get_content_type_for_model(obj).pk,
                    "object_id": obj.pk,
                },
                current_app=self.admin_site.name,
            )

    def get_empty_value_display(self):
        """
        Return the empty_value_display set on ModelAdmin or AdminSite.
        """
        try:
            return mark_safe(self.empty_value_display)
        except AttributeError:
            return mark_safe(self.admin_site.empty_value_display)

    def get_exclude(self, request, obj=None):
        """
        Hook for specifying exclude.
        """
        return self.exclude

    def get_fields(self, request, obj=None):
        """
        Hook for specifying fields.
        """
        if self.fields:
            return self.fields
        # _get_form_for_get_fields() is implemented in subclasses.
        form = self._get_form_for_get_fields(request, obj)
        return [*form.base_fields, *self.get_readonly_fields(request, obj)]

    def get_fieldsets(self, request, obj=None):
        """
        Hook for specifying fieldsets.
        """
        if self.fieldsets:
            return self.fieldsets
        return [(None, {"fields": self.get_fields(request, obj)})]

    def get_inlines(self, request, obj):
        """Hook for specifying custom inlines."""
        return self.inlines

    def get_ordering(self, request):
        """
        Hook for specifying field ordering.
        """
        return self.ordering or ()  # otherwise we might try to *None, which is bad ;)

    def get_readonly_fields(self, request, obj=None):
        """
        Hook for specifying custom readonly fields.
        """
        return self.readonly_fields

    def get_prepopulated_fields(self, request, obj=None):
        """
        Hook for specifying custom prepopulated fields.
        """
        return self.prepopulated_fields

    def get_queryset(self, request):
        """
        Return a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = self.model._default_manager.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_sortable_by(self, request):
        """Hook for specifying which fields can be sorted in the changelist."""
        return (
            self.sortable_by
            if self.sortable_by is not None
            else self.get_list_display(request)
        )

    def lookup_allowed(self, lookup, value):
        from django.contrib.admin.filters import SimpleListFilter

        model = self.model
        # Check FKey lookups that are allowed, so that popups produced by
        # ForeignKeyRawIdWidget, on the basis of ForeignKey.limit_choices_to,
        # are allowed to work.
        for fk_lookup in model._meta.related_fkey_lookups:
            # As ``limit_choices_to`` can be a callable, invoke it here.
            if callable(fk_lookup):
                fk_lookup = fk_lookup()
            if (lookup, value) in widgets.url_params_from_lookup_dict(
                fk_lookup
            ).items():
                return True

        relation_parts = []
        prev_field = None
        for part in lookup.split(LOOKUP_SEP):
            try:
                field = model._meta.get_field(part)
            except FieldDoesNotExist:
                # Lookups on nonexistent fields are ok, since they're ignored
                # later.
                break
            # It is allowed to filter on values that would be found from local
            # model anyways. For example, if you filter on employee__department__id,
            # then the id value would be found already from employee__department_id.
            if not prev_field or (
                prev_field.is_relation
                and field not in prev_field.path_infos[-1].target_fields
            ):
                relation_parts.append(part)
            if not getattr(field, "path_infos", None):
                # This is not a relational field, so further parts
                # must be transforms.
                break
            prev_field = field
            model = field.path_infos[-1].to_opts.model

        if len(relation_parts) <= 1:
            # Either a local field filter, or no fields at all.
            return True
        valid_lookups = {self.date_hierarchy}
        for filter_item in self.list_filter:
            if isinstance(filter_item, type) and issubclass(
                filter_item, SimpleListFilter
            ):
                valid_lookups.add(filter_item.parameter_name)
            elif isinstance(filter_item, (list, tuple)):
                valid_lookups.add(filter_item[0])
            else:
                valid_lookups.add(filter_item)

        # Is it a valid relational lookup?
        return not {
            LOOKUP_SEP.join(relation_parts),
            LOOKUP_SEP.join(relation_parts + [part]),
        }.isdisjoint(valid_lookups)

    def to_field_allowed(self, request, to_field):
        """
        Return True if the model associated with this admin should be
        allowed to be referenced by the specified field.
        """
        try:
            field = self.opts.get_field(to_field)
        except FieldDoesNotExist:
            return False

        # Always allow referencing the primary key since it's already possible
        # to get this information from the change view URL.
        if field.primary_key:
            return True

        # Allow reverse relationships to models defining m2m fields if they
        # target the specified field.
        for many_to_many in self.opts.many_to_many:
            if many_to_many.m2m_target_field_name() == to_field:
                return True

        # Make sure at least one of the models registered for this site
        # references this field through a FK or a M2M relationship.
        registered_models = set()
        for model, admin in self.admin_site._registry.items():
            registered_models.add(model)
            for inline in admin.inlines:
                registered_models.add(inline.model)

        related_objects = (
            f
            for f in self.opts.get_fields(include_hidden=True)
            if (f.auto_created and not f.concrete)
        )
        for related_object in related_objects:
            related_model = related_object.related_model
            remote_field = related_object.field.remote_field
            if (
                any(issubclass(model, related_model) for model in registered_models)
                and hasattr(remote_field, "get_related_field")
                and remote_field.get_related_field() == field
            ):
                return True

        return False

    def has_add_permission(self, request):
        """
        Return True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        opts = self.opts
        codename = get_permission_codename("add", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_change_permission(self, request, obj=None):
        """
        Return True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to change the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to change *any* object of the given type.
        """
        opts = self.opts
        codename = get_permission_codename("change", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_delete_permission(self, request, obj=None):
        """
        Return True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to delete the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to delete *any* object of the given type.
        """
        opts = self.opts
        codename = get_permission_codename("delete", opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_view_permission(self, request, obj=None):
        """
        Return True if the given request has permission to view the given
        Django model instance. The default implementation doesn't examine the
        `obj` parameter.

        If overridden by the user in subclasses, it should return True if the
        given request has permission to view the `obj` model instance. If `obj`
        is None, it should return True if the request has permission to view
        any object of the given type.
        """
        opts = self.opts
        codename_view = get_permission_codename("view", opts)
        codename_change = get_permission_codename("change", opts)
        return request.user.has_perm(
            "%s.%s" % (opts.app_label, codename_view)
        ) or request.user.has_perm("%s.%s" % (opts.app_label, codename_change))

    def has_view_or_change_permission(self, request, obj=None):
        return self.has_view_permission(request, obj) or self.has_change_permission(
            request, obj
        )

    def has_module_permission(self, request):
        """
        Return True if the given request has any permission in the given
        app label.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to view the module on
        the admin index page and access the module's index page. Overriding it
        does not restrict access to the add, change or delete views. Use
        `ModelAdmin.has_(add|change|delete)_permission` for that.
        """
        return request.user.has_module_perms(self.opts.app_label)


class ModelAdmin(BaseModelAdmin):
    """Encapsulate all admin options and functionality for a given model."""

    list_display = ("__str__",)
    list_display_links = ()
    list_filter = ()
    list_select_related = False
    list_per_page = 100
    list_max_show_all = 200
    list_editable = ()
    search_fields = ()
    search_help_text = None
    date_hierarchy = None
    save_as = False
    save_as_continue = True
    save_on_top = False
    paginator = Paginator
    preserve_filters = True
    inlines = ()

    # Custom templates (designed to be over-ridden in subclasses)
    add_form_template = None
    change_form_template = None
    change_list_template = None
    delete_confirmation_template = None
    delete_selected_confirmation_template = None
    object_history_template = None
    popup_response_template = None

    # Actions
    actions = ()
    action_form = helpers.ActionForm
    actions_on_top = True
    actions_on_bottom = False
    actions_selection_counter = True
    checks_class = ModelAdminChecks

    def __init__(self, model, admin_site):
        self.model = model
        self.opts = model._meta
        self.admin_site = admin_site
        super().__init__()

    def __str__(self):
        return "%s.%s" % (self.opts.app_label, self.__class__.__name__)

    def __repr__(self):
        """
        This function returns a string representation of the object. The string includes the class name, the model name, and the admin site. The model name is obtained from the `model` attribute of the object, which is expected to be an instance of a model class. The `admin_site` attribute is expected to be an instance of the admin site where the model is registered. The function does not take any parameters and returns a string.
        
        :returns: A string representation of the object in the format:
        """

        return (
            f"<{self.__class__.__qualname__}: model={self.model.__qualname__} "
            f"site={self.admin_site!r}>"
        )

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        for inline_class in self.get_inlines(request, obj):
            inline = inline_class(self.model, self.admin_site)
            if request:
                if not (
                    inline.has_view_or_change_permission(request, obj)
                    or inline.has_add_permission(request, obj)
                    or inline.has_delete_permission(request, obj)
                ):
                    continue
                if not inline.has_add_permission(request, obj):
                    inline.max_num = 0
            inline_instances.append(inline)

        return inline_instances

    def get_urls(self):
        """
        This function generates URL patterns for a Django admin interface. It returns a list of URL patterns for various admin actions such as listing, adding, changing, and deleting objects.
        
        Key Parameters:
        - `self`: The instance of the admin model.
        
        Returns:
        - A list of `path` objects, each representing a URL pattern for a specific admin action.
        
        Each path object is defined as follows:
        - `path("", wrap(self.changelist_view), name="%s_%s_changelist" % info
        """

        from django.urls import path

        def wrap(view):
            """
            This function wraps a view function to be used with the Django admin site. It returns a new view function that is decorated with `admin_site.admin_view`, which provides additional functionality such as permission checks and context injection. The wrapped function retains the original view's functionality while adding admin-specific behavior.
            
            Parameters:
            - view: The original view function to be wrapped.
            
            Returns:
            - A new view function that is ready to be used with the Django admin site, with the original view's functionality preserved.
            
            Key Attributes
            """

            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.opts.app_label, self.opts.model_name

        return [
            path("", wrap(self.changelist_view), name="%s_%s_changelist" % info),
            path("add/", wrap(self.add_view), name="%s_%s_add" % info),
            path(
                "<path:object_id>/history/",
                wrap(self.history_view),
                name="%s_%s_history" % info,
            ),
            path(
                "<path:object_id>/delete/",
                wrap(self.delete_view),
                name="%s_%s_delete" % info,
            ),
            path(
                "<path:object_id>/change/",
                wrap(self.change_view),
                name="%s_%s_change" % info,
            ),
            # For backwards compatibility (was the change url before 1.9)
            path(
                "<path:object_id>/",
                wrap(
                    RedirectView.as_view(
                        pattern_name="%s:%s_%s_change"
                        % ((self.admin_site.name,) + info)
                    )
                ),
            ),
        ]

    @property
    def urls(self):
        return self.get_urls()

    @property
    def media(self):
        """
        Generates the JavaScript media for Django admin.
        
        This function returns a Media object containing the JavaScript files required for Django admin functionality. The files are specified in the `js` list, which includes both vendor and Django-specific JavaScript files. The `extra` variable is used to conditionally append '.min' to the file names based on the `settings.DEBUG` value. The generated Media object is then returned.
        
        Parameters:
        - None
        
        Returns:
        - Media: A Media object containing the list of JavaScript files
        """

        extra = "" if settings.DEBUG else ".min"
        js = [
            "vendor/jquery/jquery%s.js" % extra,
            "jquery.init.js",
            "core.js",
            "admin/RelatedObjectLookups.js",
            "actions.js",
            "urlify.js",
            "prepopulate.js",
            "vendor/xregexp/xregexp%s.js" % extra,
        ]
        return forms.Media(js=["admin/js/%s" % url for url in js])

    def get_model_perms(self, request):
        """
        Return a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, ``delete``, and ``view`` mapping to the True/False
        for each of those actions.
        """
        return {
            "add": self.has_add_permission(request),
            "change": self.has_change_permission(request),
            "delete": self.has_delete_permission(request),
            "view": self.has_view_permission(request),
        }

    def _get_form_for_get_fields(self, request, obj):
        return self.get_form(request, obj, fields=None)

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Return a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        if "fields" in kwargs:
            fields = kwargs.pop("fields")
        else:
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        excluded = self.get_exclude(request, obj)
        exclude = [] if excluded is None else list(excluded)
        readonly_fields = self.get_readonly_fields(request, obj)
        exclude.extend(readonly_fields)
        # Exclude all fields if it's a change form and the user doesn't have
        # the change permission.
        if (
            change
            and hasattr(request, "user")
            and not self.has_change_permission(request, obj)
        ):
            exclude.extend(fields)
        if excluded is None and hasattr(self.form, "_meta") and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # if exclude is an empty list we pass None to be consistent with the
        # default on modelform_factory
        exclude = exclude or None

        # Remove declared form fields which are in readonly_fields.
        new_attrs = dict.fromkeys(
            f for f in readonly_fields if f in self.form.declared_fields
        )
        form = type(self.form.__name__, (self.form,), new_attrs)

        defaults = {
            "form": form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            **kwargs,
        }

        if defaults["fields"] is None and not modelform_defines_fields(
            defaults["form"]
        ):
            defaults["fields"] = forms.ALL_FIELDS

        try:
            return modelform_factory(self.model, **defaults)
        except FieldError as e:
            raise FieldError(
                "%s. Check fields/fieldsets/exclude attributes of class %s."
                % (e, self.__class__.__name__)
            )

    def get_changelist(self, request, **kwargs):
        """
        Return the ChangeList class for use on the changelist page.
        """
        from django.contrib.admin.views.main import ChangeList

        return ChangeList

    def get_changelist_instance(self, request):
        """
        Return a `ChangeList` instance based on `request`. May raise
        `IncorrectLookupParameters`.
        """
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        # Add the action checkboxes if any actions are available.
        if self.get_actions(request):
            list_display = ["action_checkbox", *list_display]
        sortable_by = self.get_sortable_by(request)
        ChangeList = self.get_changelist(request)
        return ChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            self.get_list_filter(request),
            self.date_hierarchy,
            self.get_search_fields(request),
            self.get_list_select_related(request),
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
            sortable_by,
            self.search_help_text,
        )

    def get_object(self, request, object_id, from_field=None):
        """
        Return an instance matching the field and value provided, the primary
        key is used if no field is provided. Return ``None`` if no match is
        found or the object_id fails validation.
        """
        queryset = self.get_queryset(request)
        model = queryset.model
        field = (
            model._meta.pk if from_field is None else model._meta.get_field(from_field)
        )
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None

    def get_changelist_form(self, request, **kwargs):
        """
        Return a Form class for use in the Formset on the changelist page.
        """
        defaults = {
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            **kwargs,
        }
        if defaults.get("fields") is None and not modelform_defines_fields(
            defaults.get("form")
        ):
            defaults["fields"] = forms.ALL_FIELDS

        return modelform_factory(self.model, **defaults)

    def get_changelist_formset(self, request, **kwargs):
        """
        Return a FormSet class for use on the changelist page if list_editable
        is used.
        """
        defaults = {
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            **kwargs,
        }
        return modelformset_factory(
            self.model,
            self.get_changelist_form(request),
            extra=0,
            fields=self.list_editable,
            **defaults,
        )

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Yield formsets and the corresponding inlines.
        """
        for inline in self.get_inline_instances(request, obj):
            yield inline.get_formset(request, obj), inline

    def get_paginator(
        self, request, queryset, per_page, orphans=0, allow_empty_first_page=True
    ):
        return self.paginator(queryset, per_page, orphans, allow_empty_first_page)

    def log_addition(self, request, obj, message):
        """
        Log that an object has been successfully added.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import ADDITION, LogEntry

        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=str(obj),
            action_flag=ADDITION,
            change_message=message,
        )

    def log_change(self, request, obj, message):
        """
        Log that an object has been successfully changed.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import CHANGE, LogEntry

        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=str(obj),
            action_flag=CHANGE,
            change_message=message,
        )

    def log_deletion(self, request, obj, object_repr):
        """
        Log that an object will be deleted. Note that this method must be
        called before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import DELETION, LogEntry

        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=object_repr,
            action_flag=DELETION,
        )

    @display(description=mark_safe('<input type="checkbox" id="action-toggle">'))
    def action_checkbox(self, obj):
        """
        A list_display column containing a checkbox widget.
        """
        return helpers.checkbox.render(helpers.ACTION_CHECKBOX_NAME, str(obj.pk))

    @staticmethod
    def _get_action_description(func, name):
        return getattr(func, "short_description", capfirst(name.replace("_", " ")))

    def _get_base_actions(self):
        """Return the list of actions, prior to any request-based filtering."""
        actions = []
        base_actions = (self.get_action(action) for action in self.actions or [])
        # get_action might have returned None, so filter any of those out.
        base_actions = [action for action in base_actions if action]
        base_action_names = {name for _, name, _ in base_actions}

        # Gather actions from the admin site first
        for (name, func) in self.admin_site.actions:
            if name in base_action_names:
                continue
            description = self._get_action_description(func, name)
            actions.append((func, name, description))
        # Add actions from this ModelAdmin.
        actions.extend(base_actions)
        return actions

    def _filter_actions_by_permissions(self, request, actions):
        """Filter out any actions that the user doesn't have access to."""
        filtered_actions = []
        for action in actions:
            callable = action[0]
            if not hasattr(callable, "allowed_permissions"):
                filtered_actions.append(action)
                continue
            permission_checks = (
                getattr(self, "has_%s_permission" % permission)
                for permission in callable.allowed_permissions
            )
            if any(has_permission(request) for has_permission in permission_checks):
                filtered_actions.append(action)
        return filtered_actions

    def get_actions(self, request):
        """
        Return a dictionary mapping the names of all actions for this
        ModelAdmin to a tuple of (callable, name, description) for each action.
        """
        # If self.actions is set to None that means actions are disabled on
        # this page.
        if self.actions is None or IS_POPUP_VAR in request.GET:
            return {}
        actions = self._filter_actions_by_permissions(request, self._get_base_actions())
        return {name: (func, name, desc) for func, name, desc in actions}

    def get_action_choices(self, request, default_choices=models.BLANK_CHOICE_DASH):
        """
        Return a list of choices for use in a form object.  Each choice is a
        tuple (name, description).
        """
        choices = [] + default_choices
        for func, name, description in self.get_actions(request).values():
            choice = (name, description % model_format_dict(self.opts))
            choices.append(choice)
        return choices

    def get_action(self, action):
        """
        Return a given action from a parameter, which can either be a callable,
        or the name of a method on the ModelAdmin.  Return is a tuple of
        (callable, name, description).
        """
        # If the action is a callable, just use it.
        if callable(action):
            func = action
            action = action.__name__

        # Next, look for a method. Grab it off self.__class__ to get an unbound
        # method instead of a bound o
