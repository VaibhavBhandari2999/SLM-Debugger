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
        transform = super().get_transform(name)
        if transform:
            return transform
        return KeyTransformFactory(name)

    def validate(self, value, model_instance):
        """
        Validate a dictionary value to ensure all its keys have string values.
        
        Args:
        value (dict): The dictionary value to be validated.
        model_instance (object): The model instance associated with the validation.
        
        Raises:
        ValidationError: If any value in the dictionary is not a string or is None.
        
        This method extends the validation process by checking that each value in the provided dictionary is a string. If any value is not a string (and is not None), a ValidationError is raised with a specific error
        """

        super().validate(value, model_instance)
        for key, val in value.items():
            if not isinstance(val, str) and val is not None:
                raise exceptions.ValidationError(
                    self.error_messages['not_a_string'],
                    code='not_a_string',
                    params={'key': key},
                )

    def to_python(self, value):
        if isinstance(value, str):
            value = json.loads(value)
        return value

    def value_to_string(self, obj):
        return json.dumps(self.value_from_object(obj))

    def formfield(self, **kwargs):
        """
        Generates a form field for a HStoreField.
        
        This function is a custom implementation of the formfield method for a model field. It returns a form field of type `forms.HStoreField` which is designed to handle fields that store key-value pairs in a dictionary-like structure.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments. These can include various options for configuring the form field, such as initial values, widget types, help text, etc.
        
        Returns:
        A form field instance of type
        """

        return super().formfield(**{
            'form_class': forms.HStoreField,
            **kwargs,
        })

    def get_prep_value(self, value):
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
