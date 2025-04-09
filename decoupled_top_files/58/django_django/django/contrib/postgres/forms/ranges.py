"""
This Python file defines a set of Django form fields and widgets for handling range-based data types. It includes:

1. **RangeWidget**: A custom widget that splits input into two parts and renders them as hidden inputs.
2. **HiddenRangeWidget**: A subclass of `RangeWidget` that uses hidden input fields.
3. **BaseRangeField**: A base class for creating range fields. It handles common logic for preparing and compressing range values.
4. **IntegerRangeField**: A specific range field for integer ranges.
5. **DecimalRangeField**: A specific range field for decimal number ranges.
6. **DateTimeRangeField**: A specific range field for datetime ranges.
7. **DateRangeField**: A specific range field for date
"""
from psycopg2.extras import DateRange, DateTimeTZRange, NumericRange

from django import forms
from django.core import exceptions
from django.forms.widgets import HiddenInput, MultiWidget
from django.utils.translation import gettext_lazy as _

__all__ = [
    'BaseRangeField', 'IntegerRangeField', 'DecimalRangeField',
    'DateTimeRangeField', 'DateRangeField', 'HiddenRangeWidget', 'RangeWidget',
]


class RangeWidget(MultiWidget):
    def __init__(self, base_widget, attrs=None):
        widgets = (base_widget, base_widget)
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """
        Decompresses a given value into a tuple of lower and upper case representations.
        
        Args:
        value (str): The input string to be decompressed.
        
        Returns:
        tuple: A tuple containing the lower and upper case versions of the input string.
        If the input is empty, returns a tuple of (None, None).
        
        Examples:
        >>> decompress('Hello')
        ('hello', 'HELLO')
        
        >>> decompress('')
        (None, None)
        """

        if value:
            return (value.lower, value.upper)
        return (None, None)


class HiddenRangeWidget(RangeWidget):
    """A widget that splits input into two <input type="hidden"> inputs."""
    def __init__(self, attrs=None):
        super().__init__(HiddenInput, attrs)


class BaseRangeField(forms.MultiValueField):
    default_error_messages = {
        'invalid': _('Enter two valid values.'),
        'bound_ordering': _('The start of the range must not exceed the end of the range.'),
    }
    hidden_widget = HiddenRangeWidget

    def __init__(self, **kwargs):
        """
        Initialize a RangeField instance.
        
        Args:
        **kwargs: Arbitrary keyword arguments.
        
        Keyword Args:
        widget (Widget): The widget to use for rendering the field. Defaults to RangeWidget with base_field's widget.
        fields (list): A list of two fields, each being an instance of base_field. Defaults to two instances of base_field, both optional.
        required (bool): Whether the field is required. Defaults to False.
        require_all_fields (bool): Whether all fields
        """

        if 'widget' not in kwargs:
            kwargs['widget'] = RangeWidget(self.base_field.widget)
        if 'fields' not in kwargs:
            kwargs['fields'] = [self.base_field(required=False), self.base_field(required=False)]
        kwargs.setdefault('required', False)
        kwargs.setdefault('require_all_fields', False)
        super().__init__(**kwargs)

    def prepare_value(self, value):
        """
        Prepares the given value for storage or transmission.
        
        This method handles the preparation of a value that is expected to be within a specified range type. It processes the value based on its type and ensures that the lower and upper bounds are correctly prepared using the `prepare_value` methods from the `lower_base` and `upper_base` fields.
        
        Args:
        value (Union[range_type, None]): The value to be prepared. If it's an instance of `range_type`, it
        """

        lower_base, upper_base = self.fields
        if isinstance(value, self.range_type):
            return [
                lower_base.prepare_value(value.lower),
                upper_base.prepare_value(value.upper),
            ]
        if value is None:
            return [
                lower_base.prepare_value(None),
                upper_base.prepare_value(None),
            ]
        return value

    def compress(self, values):
        """
        Compresses a range of values.
        
        Args:
        values (tuple): A tuple containing two elements representing the lower and upper bounds of the range.
        
        Returns:
        range_value: An instance of the specified range type.
        
        Raises:
        ValidationError: If the input values are invalid or do not meet certain conditions.
        
        Important Functions:
        - `range_type`: The type of range to be created from the given bounds.
        - `exceptions.ValidationError`: Raised when the input values are invalid
        """

        if not values:
            return None
        lower, upper = values
        if lower is not None and upper is not None and lower > upper:
            raise exceptions.ValidationError(
                self.error_messages['bound_ordering'],
                code='bound_ordering',
            )
        try:
            range_value = self.range_type(lower, upper)
        except TypeError:
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
            )
        else:
            return range_value


class IntegerRangeField(BaseRangeField):
    default_error_messages = {'invalid': _('Enter two whole numbers.')}
    base_field = forms.IntegerField
    range_type = NumericRange


class DecimalRangeField(BaseRangeField):
    default_error_messages = {'invalid': _('Enter two numbers.')}
    base_field = forms.DecimalField
    range_type = NumericRange


class DateTimeRangeField(BaseRangeField):
    default_error_messages = {'invalid': _('Enter two valid date/times.')}
    base_field = forms.DateTimeField
    range_type = DateTimeTZRange


class DateRangeField(BaseRangeField):
    default_error_messages = {'invalid': _('Enter two valid dates.')}
    base_field = forms.DateField
    range_type = DateRange
