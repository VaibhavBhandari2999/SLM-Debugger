import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

__all__ = ["HStoreField"]


class HStoreField(forms.CharField):
    """
    A field for HStore data which accepts dictionary JSON input.
    """

    widget = forms.Textarea
    default_error_messages = {
        "invalid_json": _("Could not load JSON data."),
        "invalid_format": _("Input must be a JSON dictionary."),
    }

    def prepare_value(self, value):
        """
        Prepare a value for storage.
        
        This function prepares a given value for storage by converting a dictionary to a JSON string. If the input value is a dictionary, it is converted to a JSON string using `json.dumps`. For any other type of value, it is returned as is.
        
        Parameters:
        value (Any): The value to be prepared for storage.
        
        Returns:
        str or Any: The prepared value, which will be a JSON string if the input was a dictionary, or the original value otherwise
        """

        if isinstance(value, dict):
            return json.dumps(value)
        return value

    def to_python(self, value):
        if not value:
            return {}
        if not isinstance(value, dict):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError(
                    self.error_messages["invalid_json"],
                    code="invalid_json",
                )

        if not isinstance(value, dict):
            raise ValidationError(
                self.error_messages["invalid_format"],
                code="invalid_format",
            )

        # Cast everything to strings for ease.
        for key, val in value.items():
            if val is not None:
                val = str(val)
            value[key] = val
        return value

    def has_changed(self, initial, data):
        """
        Return True if data differs from initial.
        """
        # For purposes of seeing whether something has changed, None is
        # the same as an empty dict, if the data or initial value we get
        # is None, replace it w/ {}.
        initial_value = self.to_python(initial)
        return super().has_changed(initial_value, data)
