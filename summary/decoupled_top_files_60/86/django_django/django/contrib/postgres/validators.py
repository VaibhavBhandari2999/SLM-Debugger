from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxLengthValidator, MaxValueValidator, MinLengthValidator,
    MinValueValidator,
)
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _, ngettext_lazy


class ArrayMaxLengthValidator(MaxLengthValidator):
    message = ngettext_lazy(
        'List contains %(show_value)d item, it should contain no more than %(limit_value)d.',
        'List contains %(show_value)d items, it should contain no more than %(limit_value)d.',
        'limit_value')


class ArrayMinLengthValidator(MinLengthValidator):
    message = ngettext_lazy(
        'List contains %(show_value)d item, it should contain no fewer than %(limit_value)d.',
        'List contains %(show_value)d items, it should contain no fewer than %(limit_value)d.',
        'limit_value')


@deconstructible
class KeysValidator:
    """A validator designed for HStore to require/restrict keys."""

    messages = {
        'missing_keys': _('Some keys were missing: %(keys)s'),
        'extra_keys': _('Some unknown keys were provided: %(keys)s'),
    }
    strict = False

    def __init__(self, keys, strict=False, messages=None):
        self.keys = set(keys)
        self.strict = strict
        if messages is not None:
            self.messages = {**self.messages, **messages}

    def __call__(self, value):
        """
        Validate a dictionary against a set of keys.
        
        This method checks if the provided dictionary contains all the required keys and optionally ensures that it does not contain any extra keys.
        
        Parameters:
        value (dict): The dictionary to validate.
        
        Returns:
        None: This method does not return a value but raises a ValidationError if the validation fails.
        
        Raises:
        ValidationError: If the dictionary is missing any required keys or contains extra keys (when strict is True).
        
        Attributes:
        keys (set): The set of required
        """

        keys = set(value)
        missing_keys = self.keys - keys
        if missing_keys:
            raise ValidationError(
                self.messages['missing_keys'],
                code='missing_keys',
                params={'keys': ', '.join(missing_keys)},
            )
        if self.strict:
            extra_keys = keys - self.keys
            if extra_keys:
                raise ValidationError(
                    self.messages['extra_keys'],
                    code='extra_keys',
                    params={'keys': ', '.join(extra_keys)},
                )

    def __eq__(self, other):
        """
        Function: __eq__
        
        This method checks if the current object is equal to another object of the same class based on certain attributes.
        
        Parameters:
        - self: The current instance of the class.
        - other: The object to compare with the current instance.
        
        Returns:
        - True if the current instance and the other object have the same keys, messages, and strict flag; False otherwise.
        
        Note:
        - The comparison is only valid if 'other' is an instance of the same class as 'self'.
        """

        return (
            isinstance(other, self.__class__) and
            self.keys == other.keys and
            self.messages == other.messages and
            self.strict == other.strict
        )


class RangeMaxValueValidator(MaxValueValidator):
    def compare(self, a, b):
        return a.upper is None or a.upper > b
    message = _('Ensure that this range is completely less than or equal to %(limit_value)s.')


class RangeMinValueValidator(MinValueValidator):
    def compare(self, a, b):
        return a.lower is None or a.lower < b
    message = _('Ensure that this range is completely greater than or equal to %(limit_value)s.')
