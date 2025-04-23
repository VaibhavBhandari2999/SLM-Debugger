import copy
from itertools import chain

from django import forms
from django.contrib.postgres.validators import (
    ArrayMaxLengthValidator, ArrayMinLengthValidator,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ..utils import prefix_validation_error


class SimpleArrayField(forms.CharField):
    default_error_messages = {
        'item_invalid': _('Item %(nth)s in the array did not validate:'),
    }

    def __init__(self, base_field, *, delimiter=',', max_length=None, min_length=None, **kwargs):
        self.base_field = base_field
        self.delimiter = delimiter
        super().__init__(**kwargs)
        if min_length is not None:
            self.min_length = min_length
            self.validators.append(ArrayMinLengthValidator(int(min_length)))
        if max_length is not None:
            self.max_length = max_length
            self.validators.append(ArrayMaxLengthValidator(int(max_length)))

    def clean(self, value):
        value = super().clean(value)
        return [self.base_field.clean(val) for val in value]

    def prepare_value(self, value):
        """
        Prepare a value for output.
        
        This method prepares a value for output, handling lists by joining their elements with a delimiter. It also prepares each element of the list using the base field's prepare_value method.
        
        Parameters:
        value (any): The value to prepare for output.
        
        Returns:
        str: The prepared value, either as a single value or a joined string of list elements.
        
        Example:
        >>> field = SomeField()
        >>> field.prepare_value([1, 2, 3])
        """

        if isinstance(value, list):
            return self.delimiter.join(str(self.base_field.prepare_value(v)) for v in value)
        return value

    def to_python(self, value):
        """
        Converts a given value to a Python list based on the delimiter.
        
        Parameters:
        value (str or list): The input value to be converted. If a string, it is split using the delimiter to form a list. If already a list, it is used as is.
        
        Returns:
        list: A list of values converted from the input, with each item processed by the base_field's to_python method.
        
        Raises:
        ValidationError: If any item in the list fails to convert using the base
        """

        if isinstance(value, list):
            items = value
        elif value:
            items = value.split(self.delimiter)
        else:
            items = []
        errors = []
        values = []
        for index, item in enumerate(items):
            try:
                values.append(self.base_field.to_python(item))
            except ValidationError as error:
                errors.append(prefix_validation_error(
                    error,
                    prefix=self.error_messages['item_invalid'],
                    code='item_invalid',
                    params={'nth': index + 1},
                ))
        if errors:
            raise ValidationError(errors)
        return values

    def validate(self, value):
        super().validate(value)
        errors = []
        for index, item in enumerate(value):
            try:
                self.base_field.validate(item)
            except ValidationError as error:
                errors.append(prefix_validation_error(
                    error,
                    prefix=self.error_messages['item_invalid'],
                    code='item_invalid',
                    params={'nth': index + 1},
                ))
        if errors:
            raise ValidationError(errors)

    def run_validators(self, value):
        super().run_validators(value)
        errors = []
        for index, item in enumerate(value):
            try:
                self.base_field.run_validators(item)
            except ValidationError as error:
                errors.append(prefix_validation_error(
                    error,
                    prefix=self.error_messages['item_invalid'],
                    code='item_invalid',
                    params={'nth': index + 1},
                ))
        if errors:
            raise ValidationError(errors)

    def has_changed(self, initial, data):
        try:
            value = self.to_python(data)
        except ValidationError:
            pass
        else:
            if initial in self.empty_values and value in self.empty_values:
                return False
        return super().has_changed(initial, data)


class SplitArrayWidget(forms.Widget):
    template_name = 'postgres/widgets/split_array.html'

    def __init__(self, widget, size, **kwargs):
        self.widget = widget() if isinstance(widget, type) else widget
        self.size = size
        super().__init__(**kwargs)

    @property
    def is_hidden(self):
        return self.widget.is_hidden

    def value_from_datadict(self, data, files, name):
        return [self.widget.value_from_datadict(data, files, '%s_%s' % (name, index))
                for index in range(self.size)]

    def value_omitted_from_data(self, data, files, name):
        """
        value_omitted_from_data(self, data, files, name)
        
        Determine if the value for a given widget is omitted from the data.
        
        Parameters:
        - data (dict): The data dictionary containing the form data.
        - files (dict): The files dictionary containing the form files.
        - name (str): The name of the widget for which to check if the value is omitted.
        
        Returns:
        - bool: True if the value for the widget is omitted from the data, False otherwise.
        
        This
        """

        return all(
            self.widget.value_omitted_from_data(data, files, '%s_%s' % (name, index))
            for index in range(self.size)
        )

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_

    def get_context(self, name, value, attrs=None):
        """
        Generates a context dictionary for a form widget.
        
        This method is responsible for creating the context dictionary used by a form widget. It ensures that the widget is localized if the form is localized, and it populates the 'subwidgets' key with a list of subwidgets. Each subwidget corresponds to a value in the 'value' parameter, or a default value if the index is out of range. The method also handles the construction of HTML attributes for each subwidget.
        
        Parameters:
        name (
        """

        attrs = {} if attrs is None else attrs
        context = super().get_context(name, value, attrs)
        if self.is_localized:
            self.widget.is_localized = self.is_localized
        value = value or []
        context['widget']['subwidgets'] = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id')
        for i in range(max(len(value), self.size)):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = {**final_attrs, 'id': '%s_%s' % (id_, i)}
            context['widget']['subwidgets'].append(
                self.widget.get_context(name + '_%s' % i, widget_value, final_attrs)['widget']
            )
        return context

    @property
    def media(self):
        return self.widget.media

    def __deepcopy__(self, memo):
        obj = super().__deepcopy__(memo)
        obj.widget = copy.deepcopy(self.widget)
        return obj

    @property
    def needs_multipart_form(self):
        return self.widget.needs_multipart_form


class SplitArrayField(forms.Field):
    default_error_messages = {
        'item_invalid': _('Item %(nth)s in the array did not validate:'),
    }

    def __init__(self, base_field, size, *, remove_trailing_nulls=False, **kwargs):
        """
        Initialize a SplitArrayField instance.
        
        Args:
        base_field (Field): The base field to split into an array.
        size (int): The size of the array.
        remove_trailing_nulls (bool, optional): Whether to remove trailing null values from the array. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the superclass constructor.
        
        This method initializes a SplitArrayField with the specified base field, array size, and optional trailing null removal. It sets up a
        """

        self.base_field = base_field
        self.size = size
        self.remove_trailing_nulls = remove_trailing_nulls
        widget = SplitArrayWidget(widget=base_field.widget, size=size)
        kwargs.setdefault('widget', widget)
        super().__init__(**kwargs)

    def _remove_trailing_nulls(self, values):
        index = None
        if self.remove_trailing_nulls:
            for i, value in reversed(list(enumerate(values))):
                if value in self.base_field.empty_values:
                    index = i
                else:
                    break
            if index is not None:
                values = values[:index]
        return values, index

    def to_python(self, value):
        value = super().to_python(value)
        return [self.base_field.to_python(item) for item in value]

    def clean(self, value):
        cleaned_data = []
        errors = []
        if not any(value) and self.required:
            raise ValidationError(self.error_messages['required'])
        max_size = max(self.size, len(value))
        for index in range(max_size):
            item = value[index]
            try:
                cleaned_data.append(self.base_field.clean(item))
            except ValidationError as error:
                errors.append(prefix_validation_error(
                    error,
                    self.error_messages['item_invalid'],
                    code='item_invalid',
                    params={'nth': index + 1},
                ))
                cleaned_data.append(None)
            else:
                errors.append(None)
        cleaned_data, null_index = self._remove_trailing_nulls(cleaned_data)
        if null_index is not None:
            errors = errors[:null_index]
        errors = list(filter(None, errors))
        if errors:
            raise ValidationError(list(chain.from_iterable(errors)))
        return cleaned_data

    def has_changed(self, initial, data):
        try:
            data = self.to_python(data)
        except ValidationError:
            pass
        else:
            data, _ = self._remove_trailing_nulls(data)
            if initial in self.empty_values and data in self.empty_values:
                return False
        return super().has_changed(initial, data)
