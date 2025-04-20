import json

from django import forms
from django.contrib.admin.utils import (
    display_for_field, flatten_fieldsets, help_text_for_field, label_for_field,
    lookup_field, quote,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.related import (
    ForeignObjectRel, ManyToManyRel, OneToOneField,
)
from django.forms.utils import flatatt
from django.template.defaultfilters import capfirst, linebreaksbr
from django.urls import NoReverseMatch, reverse
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _

ACTION_CHECKBOX_NAME = '_selected_action'


class ActionForm(forms.Form):
    action = forms.ChoiceField(label=_('Action:'))
    select_across = forms.BooleanField(
        label='',
        required=False,
        initial=0,
        widget=forms.HiddenInput({'class': 'select-across'}),
    )


checkbox = forms.CheckboxInput({'class': 'action-select'}, lambda value: False)


class AdminForm:
    def __init__(self, form, fieldsets, prepopulated_fields, readonly_fields=None, model_admin=None):
        """
        Initialize the form and fieldsets for a model form.
        
        Args:
        form (forms.ModelForm): The form instance to be used.
        fieldsets (list): A list of fieldsets for the form.
        prepopulated_fields (dict): A dictionary where keys are field names and values are lists of dependencies for prepopulating fields.
        readonly_fields (tuple, optional): A tuple of field names that should be read-only. Defaults to an empty tuple.
        model_admin (ModelAdmin,
        """

        self.form, self.fieldsets = form, fieldsets
        self.prepopulated_fields = [{
            'field': form[field_name],
            'dependencies': [form[f] for f in dependencies]
        } for field_name, dependencies in prepopulated_fields.items()]
        self.model_admin = model_admin
        if readonly_fields is None:
            readonly_fields = ()
        self.readonly_fields = readonly_fields

    def __repr__(self):
        return (
            f'<{self.__class__.__qualname__}: '
            f'form={self.form.__class__.__qualname__} '
            f'fieldsets={self.fieldsets!r}>'
        )

    def __iter__(self):
        for name, options in self.fieldsets:
            yield Fieldset(
                self.form, name,
                readonly_fields=self.readonly_fields,
                model_admin=self.model_admin,
                **options
            )

    @property
    def errors(self):
        return self.form.errors

    @property
    def non_field_errors(self):
        return self.form.non_field_errors

    @property
    def media(self):
        """
        Calculate the combined media attributes of a form and its fields.
        
        Parameters:
        self (Form): The form object which contains the media attributes and fields.
        
        Returns:
        Media: A combined Media object that includes the media attributes of the form itself and all its fields.
        
        This function iterates through each field in the form and accumulates their media attributes to the form's media, returning the total media.
        """

        media = self.form.media
        for fs in self:
            media = media + fs.media
        return media


class Fieldset:
    def __init__(self, form, name=None, readonly_fields=(), fields=(), classes=(),
                 description=None, model_admin=None):
        self.form = form
        self.name, self.fields = name, fields
        self.classes = ' '.join(classes)
        self.description = description
        self.model_admin = model_admin
        self.readonly_fields = readonly_fields

    @property
    def media(self):
        """
        Generates a Media object for Django admin forms.
        
        This function returns a Media object which can be used to include JavaScript files in the Django admin interface. The inclusion of JavaScript is conditional based on the presence of 'collapse' in the list of classes associated with the current form.
        
        Parameters:
        None
        
        Returns:
        forms.Media: A Media object that can be used to include JavaScript files in the Django admin interface.
        
        Key Considerations:
        - The function checks if 'collapse' is in the '
        """

        if 'collapse' in self.classes:
            return forms.Media(js=['admin/js/collapse.js'])
        return forms.Media()

    def __iter__(self):
        for field in self.fields:
            yield Fieldline(self.form, field, self.readonly_fields, model_admin=self.model_admin)


class Fieldline:
    def __init__(self, form, field, readonly_fields=None, model_admin=None):
        self.form = form  # A django.forms.Form instance
        if not hasattr(field, "__iter__") or isinstance(field, str):
            self.fields = [field]
        else:
            self.fields = field
        self.has_visible_field = not all(
            field in self.form.fields and self.form.fields[field].widget.is_hidden
            for field in self.fields
        )
        self.model_admin = model_admin
        if readonly_fields is None:
            readonly_fields = ()
        self.readonly_fields = readonly_fields

    def __iter__(self):
        """
        Iterates over the fields in the form and yields either an AdminReadonlyField or an AdminField instance based on whether the field is in the readonly_fields list. The function takes no parameters and returns an iterator of field instances.
        
        Key Parameters:
        - self: The current instance of the class, which contains the form, fields, and readonly_fields.
        
        Keywords:
        - readonly_fields: A list of field names that should be displayed as read-only in the admin interface.
        
        Returns:
        - An iterator of instances
        """

        for i, field in enumerate(self.fields):
            if field in self.readonly_fields:
                yield AdminReadonlyField(self.form, field, is_first=(i == 0), model_admin=self.model_admin)
            else:
                yield AdminField(self.form, field, is_first=(i == 0))

    def errors(self):
        return mark_safe(
            '\n'.join(
                self.form[f].errors.as_ul() for f in self.fields if f not in self.readonly_fields
            ).strip('\n')
        )


class AdminField:
    def __init__(self, form, field, is_first):
        """
        Initialize a form field.
        
        Args:
        form (dict): A dictionary containing the form data, where the key is the field name and the value is a django.forms.BoundField instance.
        field (str): The name of the field in the form.
        is_first (bool): A boolean indicating whether this field is the first on the line.
        
        Attributes:
        field (django.forms.BoundField): The BoundField instance representing the form field.
        is_first (bool): Whether this field
        """

        self.field = form[field]  # A django.forms.BoundField instance
        self.is_first = is_first  # Whether this field is first on the line
        self.is_checkbox = isinstance(self.field.field.widget, forms.CheckboxInput)
        self.is_readonly = False

    def label_tag(self):
        classes = []
        contents = conditional_escape(self.field.label)
        if self.is_checkbox:
            classes.append('vCheckboxLabel')

        if self.field.field.required:
            classes.append('required')
        if not self.is_first:
            classes.append('inline')
        attrs = {'class': ' '.join(classes)} if classes else {}
        # checkboxes should not have a label suffix as the checkbox appears
        # to the left of the label.
        return self.field.label_tag(
            contents=mark_safe(contents), attrs=attrs,
            label_suffix='' if self.is_checkbox else None,
        )

    def errors(self):
        return mark_safe(self.field.errors.as_ul())


class AdminReadonlyField:
    def __init__(self, form, field, is_first, model_admin=None):
        # Make self.field look a little bit like a field. This means that
        # {{ field.name }} must be a useful class name to identify the field.
        # For convenience, store other field-related data here too.
        if callable(field):
            class_name = field.__name__ if field.__name__ != '<lambda>' else ''
        else:
            class_name = field

        if form._meta.labels and class_name in form._meta.labels:
            label = form._meta.labels[class_name]
        else:
            label = label_for_field(field, form._meta.model, model_admin, form=form)

        if form._meta.help_texts and class_name in form._meta.help_texts:
            help_text = form._meta.help_texts[class_name]
        else:
            help_text = help_text_for_field(class_name, form._meta.model)

        self.field = {
            'name': class_name,
            'label': label,
            'help_text': help_text,
            'field': field,
        }
        self.form = form
        self.model_admin = model_admin
        self.is_first = is_first
        self.is_checkbox = False
        self.is_readonly = True
        self.empty_value_display = model_admin.get_empty_value_display()

    def label_tag(self):
        """
        Generate a label tag for a form field.
        
        This function creates an HTML label tag for a form field. It can be used to customize the appearance of the label based on the field's position in the form.
        
        Parameters:
        self (FormField): The current form field object.
        
        Returns:
        str: A formatted HTML string representing the label tag.
        
        Attributes:
        is_first (bool): Indicates whether the field is the first in the form.
        field (dict): A dictionary containing the field's
        """

        attrs = {}
        if not self.is_first:
            attrs["class"] = "inline"
        label = self.field['label']
        return format_html('<label{}>{}{}</label>', flatatt(attrs), capfirst(label), self.form.label_suffix)

    def get_admin_url(self, remote_field, remote_obj):
        url_name = 'admin:%s_%s_change' % (
            remote_field.model._meta.app_label,
            remote_field.model._meta.model_name,
        )
        try:
            url = reverse(url_name, args=[quote(remote_obj.pk)])
            return format_html('<a href="{}">{}</a>', url, remote_obj)
        except NoReverseMatch:
            return str(remote_obj)

    def contents(self):
        """
        Generate a representation of the field's value for display in the admin interface.
        
        This function retrieves the field's value from the form's instance and formats it for display. It handles various types of fields, including boolean fields, many-to-many relationships, and foreign key relationships. The function also supports custom widgets and escapes the output to prevent HTML injection.
        
        Parameters:
        self (AdminField): The admin field instance.
        field (str): The name of the field to display.
        obj (Model):
        """

        from django.contrib.admin.templatetags.admin_list import _boolean_icon
        field, obj, model_admin = self.field['field'], self.form.instance, self.model_admin
        try:
            f, attr, value = lookup_field(field, obj, model_admin)
        except (AttributeError, ValueError, ObjectDoesNotExist):
            result_repr = self.empty_value_display
        else:
            if field in self.form.fields:
                widget = self.form[field].field.widget
                # This isn't elegant but suffices for contrib.auth's
                # ReadOnlyPasswordHashWidget.
                if getattr(widget, 'read_only', False):
                    return widget.render(field, value)
            if f is None:
                if getattr(attr, 'boolean', False):
                    result_repr = _boolean_icon(value)
                else:
                    if hasattr(value, "__html__"):
                        result_repr = value
                    else:
                        result_repr = linebreaksbr(value)
            else:
                if isinstance(f.remote_field, ManyToManyRel) and value is not None:
                    result_repr = ", ".join(map(str, value.all()))
                elif (
                    isinstance(f.remote_field, (ForeignObjectRel, OneToOneField)) and
                    value is not None
                ):
                    result_repr = self.get_admin_url(f.remote_field, value)
                else:
                    result_repr = display_for_field(value, f, self.empty_value_display)
                result_repr = linebreaksbr(result_repr)
        return conditional_escape(result_repr)


class InlineAdminFormSet:
    """
    A wrapper around an inline formset for use in the admin system.
    """
    def __init__(self, inline, formset, fieldsets, prepopulated_fields=None,
                 readonly_fields=None, model_admin=None, has_add_permission=True,
                 has_change_permission=True, has_delete_permission=True,
                 has_view_permission=True):
        self.opts = inline
        self.formset = formset
        self.fieldsets = fieldsets
        self.model_admin = model_admin
        if readonly_fields is None:
            readonly_fields = ()
        self.readonly_fields = readonly_fields
        if prepopulated_fields is None:
            prepopulated_fields = {}
        self.prepopulated_fields = prepopulated_fields
        self.classes = ' '.join(inline.classes) if inline.classes else ''
        self.has_add_permission = has_add_permission
        self.has_change_permission = has_change_permission
        self.has_delete_permission = has_delete_permission
        self.has_view_permission = has_view_permission

    def __iter__(self):
        if self.has_change_permission:
            readonly_fields_for_editing = self.readonly_fields
        else:
            readonly_fields_for_editing = self.readonly_fields + flatten_fieldsets(self.fieldsets)

        for form, original in zip(self.formset.initial_forms, self.formset.get_queryset()):
            view_on_site_url = self.opts.get_view_on_site_url(original)
            yield InlineAdminForm(
                self.formset, form, self.fieldsets, self.prepopulated_fields,
                original, readonly_fields_for_editing, model_admin=self.opts,
                view_on_site_url=view_on_site_url,
            )
        for form in self.formset.extra_forms:
            yield InlineAdminForm(
                self.formset, form, self.fieldsets, self.prepopulated_fields,
                None, self.readonly_fields, model_admin=self.opts,
            )
        if self.has_add_permission:
            yield InlineAdminForm(
                self.formset, self.formset.empty_form,
                self.fieldsets, self.prepopulated_fields, None,
                self.readonly_fields, model_admin=self.opts,
            )

    def fields(self):
        """
        Generate a list of form fields for a formset.
        
        This function is designed to generate a list of form fields for a formset, which can be used to display or manipulate form fields in a Django admin interface. The function takes into account various parameters and settings to customize the field representation.
        
        Parameters:
        - self: The instance of the formset or form class.
        - fk (optional): A ForeignKey field name to exclude from the fields list.
        - fieldsets (optional): A list of fieldsets
        """

        fk = getattr(self.formset, "fk", None)
        empty_form = self.formset.empty_form
        meta_labels = empty_form._meta.labels or {}
        meta_help_texts = empty_form._meta.help_texts or {}
        for i, field_name in enumerate(flatten_fieldsets(self.fieldsets)):
            if fk and fk.name == field_name:
                continue
            if not self.has_change_permission or field_name in self.readonly_fields:
                yield {
                    'name': field_name,
                    'label': meta_labels.get(field_name) or label_for_field(
                        field_name,
                        self.opts.model,
                        self.opts,
                        form=empty_form,
                    ),
                    'widget': {'is_hidden': False},
                    'required': False,
                    'help_text': meta_help_texts.get(field_name) or help_text_for_field(field_name, self.opts.model),
                }
            else:
                form_field = empty_form.fields[field_name]
                label = form_field.label
                if label is None:
                    label = label_for_field(field_name, self.opts.model, self.opts, form=empty_form)
                yield {
                    'name': field_name,
                    'label': label,
                    'widget': form_field.widget,
                    'required': form_field.required,
                    'help_text': form_field.help_text,
                }

    def inline_formset_data(self):
        """
        Generates a JSON object for inline formset data.
        
        This function returns a JSON object that can be used to initialize an inline formset in a web application. The JSON object contains the formset's prefix and options for adding and deleting formset entries.
        
        Parameters:
        self (object): The instance of the class containing the formset.
        
        Returns:
        str: A JSON string representing the inline formset data.
        
        Example:
        >>> inline_formset_data()
        '{"name": "#formset_prefix
        """

        verbose_name = self.opts.verbose_name
        return json.dumps({
            'name': '#%s' % self.formset.prefix,
            'options': {
                'prefix': self.formset.prefix,
                'addText': gettext('Add another %(verbose_name)s') % {
                    'verbose_name': capfirst(verbose_name),
                },
                'deleteText': gettext('Remove'),
            }
        })

    @property
    def forms(self):
        return self.formset.forms

    @property
    def non_form_errors(self):
        return self.formset.non_form_errors

    @property
    def media(self):
        """
        Generates the media (CSS and JavaScript) required for the form.
        
        This method combines the media from the form's options, formset, and all its subforms.
        
        Parameters:
        None
        
        Returns:
        str: A string containing the combined media (CSS and JavaScript) required for rendering the form.
        
        Note:
        - The media is a combination of the form's options media, formset media, and the media from each subform.
        - This method is typically used in Django forms to
        """

        media = self.opts.media + self.formset.media
        for fs in self:
            media = media + fs.media
        return media


class InlineAdminForm(AdminForm):
    """
    A wrapper around an inline form for use in the admin system.
    """
    def __init__(self, formset, form, fieldsets, prepopulated_fields, original,
                 readonly_fields=None, model_admin=None, view_on_site_url=None):
        self.formset = formset
        self.model_admin = model_admin
        self.original = original
        self.show_url = original and view_on_site_url is not None
        self.absolute_url = view_on_site_url
        super().__init__(form, fieldsets, prepopulated_fields, readonly_fields, model_admin)

    def __iter__(self):
        """
        Generates an iterator for inline fieldsets.
        
        This function yields instances of InlineFieldset for each fieldset in the formset. Each InlineFieldset is initialized with the formset, form, fieldset name, readonly fields, and an optional model admin object.
        
        Parameters:
        self (object): The current instance of the class, which should have attributes like `fieldsets`, `formset`, `form`, `readonly_fields`, and `model_admin`.
        
        Returns:
        Iterator[InlineFieldset
        """

        for name, options in self.fieldsets:
            yield InlineFieldset(
                self.formset, self.form, name, self.readonly_fields,
                model_admin=self.model_admin, **options
            )

    def needs_explicit_pk_field(self):
        return (
            # Auto fields are editable, so check for auto or non-editable pk.
            self.form._meta.model._meta.auto_field or not self.form._meta.model._meta.pk.editable or
            # Also search any parents for an auto field. (The pk info is
            # propagated to child models so that does not need to be checked
            # in parents.)
            any(parent._meta.auto_field or not parent._meta.model._meta.pk.editable
                for parent in self.form._meta.model._meta.get_parent_list())
        )

    def pk_field(self):
        return AdminField(self.form, self.formset._pk_field.name, False)

    def fk_field(self):
        """
        Generate a field for a foreign key in a formset.
        
        This function retrieves the foreign key field from a formset and returns an `AdminField` object if available. If no foreign key is found, an empty string is returned.
        
        Parameters:
        - self (FormsetInstance): An instance of a formset.
        
        Returns:
        - AdminField: An instance of `AdminField` representing the foreign key field, or an empty string if no foreign key is found.
        
        Example:
        ```python
        # Assuming
        """

        fk = getattr(self.formset, "fk", None)
        if fk:
            return AdminField(self.form, fk.name, False)
        else:
            return ""

    def deletion_field(self):
        from django.forms.formsets import DELETION_FIELD_NAME
        return AdminField(self.form, DELETION_FIELD_NAME, False)

    def ordering_field(self):
        from django.forms.formsets import ORDERING_FIELD_NAME
        return AdminField(self.form, ORDERING_FIELD_NAME, False)


class InlineFieldset(Fieldset):
    def __init__(self, formset, *args, **kwargs):
        self.formset = formset
        super().__init__(*args, **kwargs)

    def __iter__(self):
        """
        Iterates over the fields in the formset and yields a Fieldline object for each field. The function checks if the field is related to a ForeignKey (fk) and skips it if it is. It takes the form, field name, readonly_fields, and an optional model_admin as parameters. The form is an instance of a formset, field is the name of the field, readonly_fields is a list of fields that should be read-only, and model_admin is an instance of ModelAdmin.
        """

        fk = getattr(self.formset, "fk", None)
        for field in self.fields:
            if not fk or fk.name != field:
                yield Fieldline(self.form, field, self.readonly_fields, model_admin=self.model_admin)


class AdminErrorList(forms.utils.ErrorList):
    """Store errors for the form/formsets in an add/change view."""
    def __init__(self, form, inline_formsets):
        super().__init__()

        if form.is_bound:
            self.extend(form.errors.values())
            for inline_formset in inline_formsets:
                self.extend(inline_formset.non_form_errors())
                for errors_in_inline_form in inline_formset.errors:
                    self.extend(errors_in_inline_form.values())
