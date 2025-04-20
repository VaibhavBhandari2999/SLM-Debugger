import json

from django.contrib.postgres import forms, lookups
from django.contrib.postgres.fields.array import ArrayField
from django.core import exceptions
from django.db.models import Field, TextField, Transform
from django.db.models.fields.mixins import CheckFieldDefaultMixin
from django.utils.translation import gettext_lazy as _

__all__ = ['HStoreField']


class HStoreField(CheckFieldDefaultMixin, Field):
    empty_strings_allowed = False
    description = _('Map of strings to strings/nulls')
    default_error_messages = {
        'not_a_string': _('The value of “%(key)s” is not a string or null.'),
    }
    _default_hint = ('dict', '{}')

    def db_type(self, connection):
        return 'hstore'

    def get_transform(self, name):
        """
        Retrieve a transformation by name.
        
        Args:
        name (str): The name of the transformation to retrieve.
        
        Returns:
        A transformation object if found, otherwise a KeyTransformFactory object.
        
        This method first attempts to retrieve the transformation with the given name using the superclass's `get_transform` method. If a transformation is found and returned, it is returned directly. If no transformation is found, a `KeyTransformFactory` object for the specified name is returned instead.
        """

        transform = super().get_transform(name)
        if transform:
            return transform
        return KeyTransformFactory(name)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        for key, val in value.items():
            if not isinstance(val, str) and val is not None:
                raise exceptions.ValidationError(
                    self.error_messages['not_a_string'],
                    code='not_a_string',
                    params={'key': key},
                )

    def to_python(self, value):
        """
        Converts a given value to Python type.
        
        This function takes a value and checks if it is a string. If it is, it converts the string to a Python object using `json.loads`. The function returns the converted Python object.
        
        :param value: The value to be converted to a Python object.
        :type value: str or any other type
        :returns: The converted Python object.
        :rtype: any
        """

        if isinstance(value, str):
            value = json.loads(value)
        return value

    def value_to_string(self, obj):
        return json.dumps(self.value_from_object(obj))

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': forms.HStoreField,
            **kwargs,
        })

    def get_prep_value(self, value):
        """
        Converts a value to a prepared value for database storage.
        
        This method processes the input value to ensure it is in a format suitable for database storage. It handles dictionaries and lists by converting their keys and elements to strings, respectively.
        
        Parameters:
        value (Any): The value to be converted to a prepared value.
        
        Returns:
        Any: The prepared value, with all dictionary keys and list elements converted to strings.
        
        Example:
        >>> get_prep_value({'name': 'John', 'age':
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
        return '(%s -> %%s)' % lhs, tuple(params) + (self.key_name,)


class KeyTransformFactory:

    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, *args, **kwargs):
        return KeyTransform(self.key_name, *args, **kwargs)


@HStoreField.register_lookup
class KeysTransform(Transform):
    lookup_name = 'keys'
    function = 'akeys'
    output_field = ArrayField(TextField())


@HStoreField.register_lookup
class ValuesTransform(Transform):
    lookup_name = 'values'
    function = 'avals'
    output_field = ArrayField(TextField())
