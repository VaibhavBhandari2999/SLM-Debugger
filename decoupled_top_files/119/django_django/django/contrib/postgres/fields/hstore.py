import json

from django.contrib.postgres import forms, lookups
from django.contrib.postgres.fields.array import ArrayField
from django.core import exceptions
from django.db.models import Field, TextField, Transform
from django.db.models.fields.mixins import CheckFieldDefaultMixin
from django.utils.translation import gettext_lazy as _

__all__ = ["HStoreField"]


class HStoreField(CheckFieldDefaultMixin, Field):
    empty_strings_allowed = False
    description = _("Map of strings to strings/nulls")
    default_error_messages = {
        "not_a_string": _("The value of “%(key)s” is not a string or null."),
    }
    _default_hint = ("dict", "{}")

    def db_type(self, connection):
        return "hstore"

    def get_transform(self, name):
        """
        Retrieve a transformation by name.
        
        Args:
        name (str): The name of the transformation to retrieve.
        
        Returns:
        Transform: The requested transformation object. If no transformation is found with the given name, returns an instance of `KeyTransformFactory` with the specified name.
        """

        transform = super().get_transform(name)
        if transform:
            return transform
        return KeyTransformFactory(name)

    def validate(self, value, model_instance):
        """
        Validates that all values in the dictionary `value` are strings. If any value is not a string (and is not None), a ValidationError is raised with the message "not_a_string". This method is called by the parent class's `validate` method.
        
        Args:
        value (dict): The dictionary containing the values to be validated.
        model_instance (object): The instance of the model being validated.
        
        Raises:
        ValidationError: If any value in the dictionary is not a string
        """

        super().validate(value, model_instance)
        for key, val in value.items():
            if not isinstance(val, str) and val is not None:
                raise exceptions.ValidationError(
                    self.error_messages["not_a_string"],
                    code="not_a_string",
                    params={"key": key},
                )

    def to_python(self, value):
        """
        Converts a given value to Python data structure.
        
        Args:
        value (str): The input value to be converted.
        
        Returns:
        Any: The converted Python data structure.
        
        Summary:
        This function takes an input value and checks if it is a string. If it is, it converts the string to a JSON object using `json.loads`. The function then returns the resulting Python data structure.
        """

        if isinstance(value, str):
            value = json.loads(value)
        return value

    def value_to_string(self, obj):
        return json.dumps(self.value_from_object(obj))

    def formfield(self, **kwargs):
        """
        Generates a form field for a HStoreField.
        
        This method overrides the default formfield generation for a specific
        database field type (HStoreField). It uses the `super()` method to call
        the parent class's implementation of `formfield` and then customizes the
        result by setting the `form_class` to `forms.HStoreField`.
        
        Args:
        **kwargs: Additional keyword arguments that are passed through to the
        parent class's `formfield
        """

        return super().formfield(
            **{
                "form_class": forms.HStoreField,
                **kwargs,
            }
        )

    def get_prep_value(self, value):
        """
        Converts the input value to a prepared value suitable for database storage.
        
        This method processes the input value by converting dictionaries and lists into
        string representations of their keys and elements. It ensures that all values are
        converted to strings before being returned.
        
        Args:
        value: The input value to be converted.
        
        Returns:
        The prepared value, with all dictionary keys and list items converted to strings.
        """

        value = super().get_prep_value(value)

        if isinstance(value, dict):
            prep_value = {}
            for key, val in value.items():
                key = str(key)
                if val is not None:
                    val = str(val)
                prep_value[key] = val
            value = prep_value

        if isinstance(value, list):
            value = [str(item) for item in value]

        return value


HStoreField.register_lookup(lookups.DataContains)
HStoreField.register_lookup(lookups.ContainedBy)
HStoreField.register_lookup(lookups.HasKey)
HStoreField.register_lookup(lookups.HasKeys)
HStoreField.register_lookup(lookups.HasAnyKeys)


class KeyTransform(Transform):
    output_field = TextField()

    def __init__(self, key_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_name = key_name

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return "(%s -> %%s)" % lhs, tuple(params) + (self.key_name,)


class KeyTransformFactory:
    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, *args, **kwargs):
        return KeyTransform(self.key_name, *args, **kwargs)


@HStoreField.register_lookup
class KeysTransform(Transform):
    lookup_name = "keys"
    function = "akeys"
    output_field = ArrayField(TextField())


@HStoreField.register_lookup
class ValuesTransform(Transform):
    lookup_name = "values"
    function = "avals"
    output_field = ArrayField(TextField())
