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
        """
        Initialize an instance of the ArrayField class.
        
        Args:
        base_field (Field): The base field to use for each element in the array.
        delimiter (str, optional): The delimiter used to separate elements in the array. Defaults to ','.
        min_length (int, optional): The minimum number of elements allowed in the array. If specified, a `ArrayMinLengthValidator` will be added to the validators list.
        max_length (int, optional): The maximum number of elements
        """

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
        
        This method processes the input `value` and prepares it for output based on its type. If the input is a list, it joins the prepared values of each element using the specified delimiter. Otherwise, it returns the value as is.
        
        Args:
        value (list or any): The input value to be prepared.
        
        Returns:
        str or any: The prepared value for output. If the input is a list, it will be a string with elements joined
        """

        if isinstance(value, list):
            return self.delimiter.join(str(self.base_field.prepare_value(v)) for v in value)
        return value

    def to_python(self, value):
        """
        Converts a given value to a Python list of validated items.
        
        Args:
        value (str or list): The input value to be converted and validated.
        
        Returns:
        list: A list of validated items.
        
        Raises:
        ValidationError: If any item in the input is invalid.
        
        Important Functions:
        - `isinstance`: Checks if the input value is a list.
        - `split`: Splits the input string using the specified delimiter.
        - `self.base_field.to
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
        """
        Validate a list of items using a base field.
        
        Args:
        value (list): The list of items to be validated.
        
        Raises:
        ValidationError: If any item in the list fails validation.
        
        This method iterates over each item in the provided list, validates it using the `base_field.validate` method, and collects any validation errors. If there are any errors, it raises a `ValidationError` with the collected errors.
        """

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
        """
        Runs validators on each item in the given value list. Inherits from `super()` to utilize its validation process. If any item fails validation, it appends an error message with a specific prefix and index to the `errors` list. If there are any errors, raises a `ValidationError` with the collected errors.
        
        Args:
        value (list): The list of items to validate.
        
        Raises:
        ValidationError: If any item in the list fails validation.
        """

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
        """
        Determines if the given data has changed from the initial value.
        
        Args:
        initial (Any): The initial value.
        data (Any): The current data value.
        
        Returns:
        bool: True if the data has changed from the initial value, otherwise False.
        
        Raises:
        ValidationError: If the data is invalid.
        
        This method first attempts to convert the data using `to_python`. If this conversion raises a `ValidationError`, it is caught and ignored. Otherwise, it checks if
        """

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
        """
        Initialize a new instance of the class.
        
        Args:
        widget (type or object): The widget to be used.
        size (int): The size of the widget.
        
        Returns:
        None
        
        This method initializes a new instance of the class with the specified widget and size. It checks if the widget is an instance of a class or an object, and then sets the widget accordingly. The size is assigned directly. Finally, the method calls the superclass's `__init__` method
        """

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
        Determines if the value for a given field has been omitted from the provided data.
        
        Args:
        data (dict): The form data.
        files (dict): The form files.
        name (str): The name of the field.
        
        Returns:
        bool: True if the value for the field has been omitted, False otherwise.
        
        This function checks if the value for a given field has been omitted from the provided data by iterating over a range of indices and using the `value_
        """

        return all(
            self.widget.value_omitted_from_data(data, files, '%s_%s' % (name, index))
            for index in range(self.size)
        )

    def id_for_label(self, id_):
        """
        Generates an ID for a label based on the given ID.
        
        Args:
        id_ (str): The original ID to be modified.
        
        Returns:
        str: The modified ID with an appended '_0' suffix if the original ID is not empty.
        """

        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_

    def get_context(self, name, value, attrs=None):
        """
        Get the context for rendering a widget.
        
        This method processes the input parameters `name`, `value`, and `attrs` to generate a context dictionary that can be used to render a widget. It ensures that the widget is localized if necessary, constructs the final attributes, and appends subwidgets to the context. The method returns the updated context dictionary.
        
        Parameters:
        - name (str): The name of the form field.
        - value (list): The initial value of the form field
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
        """
        Deep copies the current object and its widget attribute using `super().__deepcopy__()` and `copy.deepcopy()`. Returns a new instance of the object with the widget attribute deep-copied.
        
        Args:
        self: The object to be deep copied.
        memo (dict): A dictionary used to memoize objects during the copying process.
        
        Returns:
        obj: A new instance of the object with the widget attribute deep-copied.
        """

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
        size (int): The number of elements in the array.
        remove_trailing_nulls (bool, optional): Whether to remove trailing null values from the array. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the superclass constructor.
        
        Attributes:
        base_field (Field): The base field to split into an array.
        size (int):
        """

        self.base_field = base_field
        self.size = size
        self.remove_trailing_nulls = remove_trailing_nulls
        widget = SplitArrayWidget(widget=base_field.widget, size=size)
        kwargs.setdefault('widget', widget)
        super().__init__(**kwargs)

    def _remove_trailing_nulls(self, values):
        """
        Removes trailing null values from a list of values.
        
        Args:
        values (list): A list of values to be processed.
        
        Returns:
        tuple: A tuple containing the modified list of values and the index of the last non-null value.
        
        Keyword Arguments:
        remove_trailing_nulls (bool): If True, the function will remove trailing null values from the list. Defaults to True.
        base_field (BaseField): The base field object that defines the empty values to consider
        """

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
        """
        Cleans a list of values based on the specified field's validation rules.
        
        Args:
        value (list): The list of values to be cleaned.
        
        Returns:
        list: A cleaned list of values.
        
        Raises:
        ValidationError: If the list is empty and required is True, or if any item in the list fails validation.
        
        Important Functions:
        - `self.base_field.clean`: Cleans individual items in the list.
        - `prefix_validation_error`: Adds context to validation errors
        """

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
        """
        Determines if the provided `data` has changed from the `initial` value.
        
        Args:
        initial (Any): The initial value.
        data (Any): The current value.
        
        Returns:
        bool: True if the data has changed, False otherwise.
        
        This method first attempts to convert the `data` using the `to_python` method. If a `ValidationError` is raised, it is caught and ignored. Then, it removes trailing null values from both `initial` and
        """

        try:
            data = self.to_python(data)
        except ValidationError:
            pass
        else:
            data, _ = self._remove_trailing_nulls(data)
            if initial in self.empty_values and data in self.empty_values:
                return False
        return super().has_changed(initial, data)
