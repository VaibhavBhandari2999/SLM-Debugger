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
        Decompresses a given value into a tuple of lower and upper case representations.
        
        Args:
        value (str or None): The string value to be decompressed. If None, returns (None, None).
        
        Returns:
        tuple: A tuple containing the lower case and upper case versions of the input string. If the input is None, returns (None, None).
        
        Example:
        >>> decompress('Hello')
        ('hello', 'HELLO')
        >>> decompress(None)
        (
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
        """
        Initialize a RangeField instance.
        
        Args:
        **kwargs: Arbitrary keyword arguments.
        
        This method initializes a RangeField instance. It sets the `widget` and `fields` attributes if they are not provided in the keyword arguments. The `widget` is set to a RangeWidget with the base field's widget as its argument. The `fields` are set to two instances of the base field, both optional. The `required` and `require_all_fields` attributes are set to False if not specified
        """

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
e = NumericRange


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
