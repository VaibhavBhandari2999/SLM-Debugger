from psycopg2.extras import DateRange, DateTimeTZRange, NumericRange

from django import forms
from django.core import exceptions
from django.forms.widgets import HiddenInput, MultiWidget
from django.utils.translation import gettext_lazy as _

__all__ = [
    "BaseRangeField",
    "IntegerRangeField",
    "DecimalRangeField",
    "DateTimeRangeField",
    "DateRangeField",
    "HiddenRangeWidget",
    "RangeWidget",
]


class RangeWidget(MultiWidget):
    def __init__(self, base_widget, attrs=None):
        widgets = (base_widget, base_widget)
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """
        Decompress a value into a tuple of lower and upper bounds.
        
        Args:
        value (str): The string value to be decompressed. If the value is not None, it is expected to be a string in the format "lower-upper".
        
        Returns:
        tuple: A tuple containing two elements, the lower and upper bounds as strings. If the input value is None, the returned tuple will contain two None values.
        
        Example:
        >>> decompress("a-z")
        ('a', '
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
        "invalid": _("Enter two valid values."),
        "bound_ordering": _(
            "The start of the range must not exceed the end of the range."
        ),
    }
    hidden_widget = HiddenRangeWidget

    def __init__(self, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = RangeWidget(self.base_field.widget)
        if "fields" not in kwargs:
            kwargs["fields"] = [
                self.base_field(required=False),
                self.base_field(required=False),
            ]
        kwargs.setdefault("required", False)
        kwargs.setdefault("require_all_fields", False)
        self.range_kwargs = {}
        if default_bounds := kwargs.pop("default_bounds", None):
            self.range_kwargs = {"bounds": default_bounds}
        super().__init__(**kwargs)

    def prepare_value(self, value):
        """
        Prepare a value for serialization.
        
        This method prepares a value for serialization by ensuring it is in the correct format. It handles two main cases:
        1. If the value is an instance of a specified range type, it prepares the lower and upper bounds separately.
        2. If the value is `None`, it prepares `None` for both the lower and upper bounds.
        3. For any other value, it returns the value as is.
        
        Parameters:
        value: The value to be prepared for serialization.
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
        Compress a range of values into a specific type of range.
        
        This function takes a list of two values, `lower` and `upper`, and attempts to create a range object of a specified type (`range_type`). The function ensures that the `lower` value is less than or equal to the `upper` value. If the values are invalid or the range type is not compatible, it raises a `ValidationError`.
        
        Parameters:
        values (list): A list containing two elements, `lower`
        """

        if not values:
            return None
        lower, upper = values
        if lower is not None and upper is not None and lower > upper:
            raise exceptions.ValidationError(
                self.error_messages["bound_ordering"],
                code="bound_ordering",
            )
        try:
            range_value = self.range_type(lower, upper, **self.range_kwargs)
        except TypeError:
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
            )
        else:
            return range_value


class IntegerRangeField(BaseRangeField):
    default_error_messages = {"invalid": _("Enter two whole numbers.")}
    base_field = forms.IntegerField
    range_type = NumericRange


class DecimalRangeField(BaseRangeField):
    default_error_messages = {"invalid": _("Enter two numbers.")}
    base_field = forms.DecimalField
    range_type = NumericRange


class DateTimeRangeField(BaseRangeField):
    default_error_messages = {"invalid": _("Enter two valid date/times.")}
    base_field = forms.DateTimeField
    range_type = DateTimeTZRange


class DateRangeField(BaseRangeField):
    default_error_messages = {"invalid": _("Enter two valid dates.")}
    base_field = forms.DateField
    range_type = DateRange
