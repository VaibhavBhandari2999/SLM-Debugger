from django import forms
from django.core import exceptions
from django.db.backends.postgresql.psycopg_any import (
    DateRange,
    DateTimeTZRange,
    NumericRange,
)
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
        
        This method sets up the RangeField with default configurations and handles optional parameters.
        
        Parameters:
        **kwargs (dict): Arbitrary keyword arguments. Expected keys include:
        - 'widget': A widget to use for the range field. If not provided, a RangeWidget with the base field's widget is used.
        - 'fields': A list of two fields, typically the same type as the base field, used to represent the range. If not provided, two instances of
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
        """
        Compress a range of values.
        
        This function takes a list of two values (lower and upper bounds) and returns a compressed range object. If the input list is empty, it returns None. If the lower bound is greater than the upper bound, it raises a ValidationError with the message "bound_ordering". If the range type cannot be instantiated due to a TypeError, it raises a ValidationError with the message "invalid". Otherwise, it returns a valid range object.
        
        Parameters:
        values (list):
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
