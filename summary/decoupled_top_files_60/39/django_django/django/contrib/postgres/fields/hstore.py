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
        Transform: The requested transformation object. If the transformation is not found, a KeyTransformFactory object is returned instead.
        
        This function first attempts to retrieve the transformation using the superclass's `get_transform` method. If the transformation is found, it is returned. Otherwise, a `KeyTransformFactory` object for the specified name is returned.
        """

        transform = super().get_transform(name)
        if transform:
            return transform
        return KeyTransformFactory(name)

    def validate(self, value, model_instance):
        """
        Validate a dictionary value to ensure all non-null items are strings.
        
        This method checks each item in the provided dictionary. If any item, except for None, is not a string, a ValidationError is raised with a specific error message.
        
        Parameters:
        value (dict): The dictionary value to be validated.
        model_instance (object): The model instance associated with the validation.
        
        Returns:
        None: This method does not return any value. It either validates the input or raises a ValidationError.
        
        Raises:
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
        
        This function is a custom formfield method for a model field that handles HStore data. It returns a form field instance of type `forms.HStoreField`.
        
        Parameters:
        **kwargs: Additional keyword arguments to be passed to the form field constructor.
        
        Returns:
        An instance of `forms.HStoreField` with the provided keyword arguments.
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
ookup_name = 'values'
    function = 'avals'
    output_field = ArrayField(TextField())
