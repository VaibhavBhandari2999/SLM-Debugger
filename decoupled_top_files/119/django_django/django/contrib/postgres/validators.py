from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy


class ArrayMaxLengthValidator(MaxLengthValidator):
    message = ngettext_lazy(
        "List contains %(show_value)d item, it should contain no more than "
        "%(limit_value)d.",
        "List contains %(show_value)d items, it should contain no more than "
        "%(limit_value)d.",
        "show_value",
    )


class ArrayMinLengthValidator(MinLengthValidator):
    message = ngettext_lazy(
        "List contains %(show_value)d item, it should contain no fewer than "
        "%(limit_value)d.",
        "List contains %(show_value)d items, it should contain no fewer than "
        "%(limit_value)d.",
        "show_value",
    )


@deconstructible
class KeysValidator:
    """A validator designed for HStore to require/restrict keys."""

    messages = {
        "missing_keys": _("Some keys were missing: %(keys)s"),
        "extra_keys": _("Some unknown keys were provided: %(keys)s"),
    }
    strict = False

    def __init__(self, keys, strict=False, messages=None):
        """
        Initialize a new instance of the class.
        
        Args:
        keys (set): A set of keys that the object will validate against.
        strict (bool, optional): If True, only the specified keys are allowed. Defaults to False.
        messages (dict, optional): Custom error messages for validation failures. If provided, these messages will override the default ones. Defaults to None.
        
        Attributes:
        keys (set): The set of keys that the object will validate against.
        strict (bool
        """

        self.keys = set(keys)
        self.strict = strict
        if messages is not None:
            self.messages = {**self.messages, **messages}

    def __call__(self, value):
        """
        Calls the function with the given value.
        
        Args:
        value (set): The input value to be validated.
        
        Raises:
        ValidationError: If the input value is missing any required keys or contains extra keys based on the `strict` flag.
        
        Attributes:
        keys (set): The set of required keys.
        strict (bool): A flag indicating whether to enforce strict validation.
        messages (dict): A dictionary containing error message templates for missing and extra keys.
        """

        keys = set(value)
        missing_keys = self.keys - keys
        if missing_keys:
            raise ValidationError(
                self.messages["missing_keys"],
                code="missing_keys",
                params={"keys": ", ".join(missing_keys)},
            )
        if self.strict:
            extra_keys = keys - self.keys
            if extra_keys:
                raise ValidationError(
                    self.messages["extra_keys"],
                    code="extra_keys",
                    params={"keys": ", ".join(extra_keys)},
                )

    def __eq__(self, other):
        """
        Check if two instances of the class are equal.
        
        Args:
        other (object): The object to compare with.
        
        Returns:
        bool: True if both instances have the same keys, messages, and strict flag; False otherwise.
        
        Notes:
        - Compares the `keys`, `messages`, and `strict` attributes of the current instance with those of the `other` instance.
        - Only returns True if both instances are of the same class (`self.__class__`).
        """

        return (
            isinstance(other, self.__class__)
            and self.keys == other.keys
            and self.messages == other.messages
            and self.strict == other.strict
        )


class RangeMaxValueValidator(MaxValueValidator):
    def compare(self, a, b):
        return a.upper is None or a.upper > b

    message = _(
        "Ensure that the upper bound of the range is not greater than %(limit_value)s."
    )


class RangeMinValueValidator(MinValueValidator):
    def compare(self, a, b):
        return a.lower is None or a.lower < b

    message = _(
        "Ensure that the lower bound of the range is not less than %(limit_value)s."
    )
