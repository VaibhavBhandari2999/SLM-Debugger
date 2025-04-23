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
        Validate a dictionary value to ensure all non-null values are strings.
        
        This method is called to validate a dictionary value for a model field. It inherits from a superclass's validation method and then checks each value in the dictionary. If any non-null value is not a string, it raises a ValidationError with a specific error message.
        
        Parameters:
        value (dict): The dictionary value to validate.
        model_instance (object): The instance of the model being validated.
        
        Returns:
        None: This method does not
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
        
        This method overrides the default formfield method to ensure that the form field
        uses the HStoreField class. It accepts any number of keyword arguments which are
        then passed to the HStoreField constructor.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments to be passed to the HStoreField constructor.
        
        Returns:
        An instance of HStoreField configured with the provided keyword arguments.
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
