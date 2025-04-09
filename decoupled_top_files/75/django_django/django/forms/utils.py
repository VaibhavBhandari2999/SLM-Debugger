"""
This Python file contains utility functions and classes for handling form validation and timezone conversions in Django applications. It includes:

- `pretty_name`: Converts a field name like 'first_name' to a human-readable format 'First name'.
- `flatatt`: Converts a dictionary of attributes to a single string suitable for HTML attributes.
- `ErrorDict`: A dictionary subclass that can represent validation errors in various formats (HTML, JSON, text).
- `ErrorList`: A list subclass that can represent a collection of errors and provide methods to format them for display.
- `from_current_timezone`: Converts naive datetime objects to aware datetime objects based on the current timezone.
- `to_current_timezone`: Converts aware datetime objects to naive datetime objects based on the current timezone
"""
import json
from collections import UserList

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import escape, format_html, format_html_join, html_safe
from django.utils.translation import gettext_lazy as _


def pretty_name(name):
    """Convert 'first_name' to 'First name'."""
    if not name:
        return ''
    return name.replace('_', ' ').capitalize()


def flatatt(attrs):
    """
    Convert a dictionary of attributes to a single string.
    The returned string will contain a leading space followed by key="value",
    XML-style pairs. In the case of a boolean value, the key will appear
    without a value. It is assumed that the keys do not need to be
    XML-escaped. If the passed dictionary is empty, then return an empty
    string.

    The result is passed through 'mark_safe' (by way of 'format_html_join').
    """
    key_value_attrs = []
    boolean_attrs = []
    for attr, value in attrs.items():
        if isinstance(value, bool):
            if value:
                boolean_attrs.append((attr,))
        elif value is not None:
            key_value_attrs.append((attr, value))

    return (
        format_html_join('', ' {}="{}"', sorted(key_value_attrs)) +
        format_html_join('', ' {}', sorted(boolean_attrs))
    )


@html_safe
class ErrorDict(dict):
    """
    A collection of errors that knows how to display itself in various formats.

    The dictionary keys are the field names, and the values are the errors.
    """
    def as_data(self):
        return {f: e.as_data() for f, e in self.items()}

    def get_json_data(self, escape_html=False):
        return {f: e.get_json_data(escape_html) for f, e in self.items()}

    def as_json(self, escape_html=False):
        return json.dumps(self.get_json_data(escape_html))

    def as_ul(self):
        """
        Generates an unordered list HTML representation of the error messages.
        
        Args:
        None (the method operates on the instance's `self` attribute).
        
        Returns:
        A string containing the HTML representation of the error list.
        
        Summary:
        This function takes a list of error messages stored in the instance's `self` attribute, formats them into an unordered list with each error message wrapped in a list item, and returns the formatted HTML string. The function uses `format_html` and `format
        """

        if not self:
            return ''
        return format_html(
            '<ul class="errorlist">{}</ul>',
            format_html_join('', '<li>{}{}</li>', self.items())
        )

    def as_text(self):
        """
        Generate a text representation of validation errors.
        
        Args:
        None
        
        Returns:
        str: A formatted string representing validation errors.
        
        Raises:
        None
        
        Examples:
        >>> from some_module import SomeClass
        >>> instance = SomeClass()
        >>> instance.as_text()
        '* field1\n  * Error message 1\n  * Error message 2\n* field2\n  * Error message 3'
        
        Notes:
        - The function iterates over each field
        """

        output = []
        for field, errors in self.items():
            output.append('* %s' % field)
            output.append('\n'.join('  * %s' % e for e in errors))
        return '\n'.join(output)

    def __str__(self):
        return self.as_ul()


@html_safe
class ErrorList(UserList, list):
    """
    A collection of errors that knows how to display itself in various formats.
    """
    def __init__(self, initlist=None, error_class=None):
        """
        Initialize an instance of the class with an optional list of initial errors and an optional error class.
        
        Args:
        initlist (list, optional): A list of initial errors. Defaults to None.
        error_class (str, optional): The error class to use. If not provided, defaults to 'errorlist'.
        
        Returns:
        None: This function does not return any value, but initializes the instance with the given parameters.
        """

        super().__init__(initlist)

        if error_class is None:
            self.error_class = 'errorlist'
        else:
            self.error_class = 'errorlist {}'.format(error_class)

    def as_data(self):
        return ValidationError(self.data).error_list

    def copy(self):
        """
        Copies the current object and sets the error_class attribute of the copied object to the same value as the original object.
        
        Args:
        None
        
        Returns:
        copy (object): A new instance of the same class as the original object, with the error_class attribute set to the same value as the original object.
        
        Attributes:
        error_class (class): The class of errors associated with the object.
        
        Methods:
        copy: Creates a deep copy of the current object and sets the
        """

        copy = super().copy()
        copy.error_class = self.error_class
        return copy

    def get_json_data(self, escape_html=False):
        """
        Retrieve JSON-formatted error data.
        
        Args:
        escape_html (bool): Whether to escape HTML characters in error messages.
        
        Returns:
        list: A list of dictionaries containing error messages and codes.
        
        Summary:
        This function iterates over the error data generated by `self.as_data()`, extracts the message from each error, and formats it into a dictionary with the message and code. If `escape_html` is True, the message is escaped using the `escape` function.
        """

        errors = []
        for error in self.as_data():
            message = next(iter(error))
            errors.append({
                'message': escape(message) if escape_html else message,
                'code': error.code or '',
            })
        return errors

    def as_json(self, escape_html=False):
        return json.dumps(self.get_json_data(escape_html))

    def as_ul(self):
        """
        Generates an unordered list (ul) HTML element from the form's data.
        
        Args:
        None (the method operates on the instance's `data` attribute).
        
        Returns:
        A string containing the formatted HTML representation of the form's data as an unordered list.
        
        Keyword Arguments:
        error_class (str): The CSS class name to be applied to the unordered list element.
        
        Usage:
        This method is typically called on a form instance to generate an HTML unordered list representation of its
        """

        if not self.data:
            return ''

        return format_html(
            '<ul class="{}">{}</ul>',
            self.error_class,
            format_html_join('', '<li>{}</li>', ((e,) for e in self))
        )

    def as_text(self):
        return '\n'.join('* %s' % e for e in self)

    def __str__(self):
        return self.as_ul()

    def __repr__(self):
        return repr(list(self))

    def __contains__(self, item):
        return item in list(self)

    def __eq__(self, other):
        return list(self) == other

    def __getitem__(self, i):
        """
        Retrieve an item from the data attribute.
        
        Args:
        i (int): The index of the item to retrieve.
        
        Returns:
        ValidationError or any: Returns the error at the specified index if it is a ValidationError instance; otherwise, returns the error directly.
        """

        error = self.data[i]
        if isinstance(error, ValidationError):
            return next(iter(error))
        return error

    def __reduce_ex__(self, *args, **kwargs):
        """
        Reduces the UserList instance to a tuple containing the class name, its state, and a function for reconstructing the object. The fourth and fifth elements of the returned tuple are set to None to prevent duplicate entries when populating the list.
        
        Args:
        *args: Variable length argument list passed to the superclass's `__reduce_ex__` method.
        **kwargs: Arbitrary keyword arguments passed to the superclass's `__reduce_ex__` method.
        
        Returns:
        A tuple containing
        """

        # The `list` reduce function returns an iterator as the fourth element
        # that is normally used for repopulating. Since we only inherit from
        # `list` for `isinstance` backward compatibility (Refs #17413) we
        # nullify this iterator as it would otherwise result in duplicate
        # entries. (Refs #23594)
        info = super(UserList, self).__reduce_ex__(*args, **kwargs)
        return info[:3] + (None, None)


# Utilities for time zone support in DateTimeField et al.

def from_current_timezone(value):
    """
    When time zone support is enabled, convert naive datetimes
    entered in the current time zone to aware datetimes.
    """
    if settings.USE_TZ and value is not None and timezone.is_naive(value):
        current_timezone = timezone.get_current_timezone()
        try:
            if (
                not timezone._is_pytz_zone(current_timezone) and
                timezone._datetime_ambiguous_or_imaginary(value, current_timezone)
            ):
                raise ValueError('Ambiguous or non-existent time.')
            return timezone.make_aware(value, current_timezone)
        except Exception as exc:
            raise ValidationError(
                _('%(datetime)s couldn’t be interpreted '
                  'in time zone %(current_timezone)s; it '
                  'may be ambiguous or it may not exist.'),
                code='ambiguous_timezone',
                params={'datetime': value, 'current_timezone': current_timezone}
            ) from exc
    return value


def to_current_timezone(value):
    """
    When time zone support is enabled, convert aware datetimes
    to naive datetimes in the current time zone for display.
    """
    if settings.USE_TZ and value is not None and timezone.is_aware(value):
        return timezone.make_naive(value)
    return value
