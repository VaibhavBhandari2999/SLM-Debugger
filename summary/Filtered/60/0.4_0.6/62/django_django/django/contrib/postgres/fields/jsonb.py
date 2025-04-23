import warnings

from django.db.models import JSONField as BuiltinJSONField
from django.db.models.fields.json import (
    KeyTextTransform as BuiltinKeyTextTransform,
    KeyTransform as BuiltinKeyTransform,
)
from django.utils.deprecation import RemovedInDjango40Warning

__all__ = ['JSONField']


class JSONField(BuiltinJSONField):
    system_check_deprecated_details = {
        'msg': (
            'django.contrib.postgres.fields.JSONField is deprecated. Support '
            'for it (except in historical migrations) will be removed in '
            'Django 4.0.'
        ),
        'hint': 'Use django.db.models.JSONField instead.',
        'id': 'fields.W904',
    }


class KeyTransform(BuiltinKeyTransform):
    def __init__(self, *args, **kwargs):
        """
        This function initializes an instance of a custom JSON field transformation class. It is a deprecated method in favor of using `django.db.models.fields.json.KeyTransform`.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        None: This function does not return any value. It is primarily used for setting up the instance attributes.
        
        Deprecation Notice:
        This class is deprecated and should not be used in new code. Instead, use `django.db.models
        """

        warnings.warn(
            'django.contrib.postgres.fields.jsonb.KeyTransform is deprecated '
            'in favor of django.db.models.fields.json.KeyTransform.',
            RemovedInDjango40Warning, stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class KeyTextTransform(BuiltinKeyTextTransform):
    def __init__(self, *args, **kwargs):
        """
        This function initializes an instance of a custom database field transformation class. It is deprecated and should be replaced with `django.db.models.fields.json.KeyTextTransform`.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        None
        
        Note:
        This class is deprecated and will be removed in Django 4.0. Users should migrate to using `django.db.models.fields.json.KeyTextTransform` instead.
        """

        warnings.warn(
            'django.contrib.postgres.fields.jsonb.KeyTextTransform is '
            'deprecated in favor of '
            'django.db.models.fields.json.KeyTextTransform.',
            RemovedInDjango40Warning, stacklevel=2,
        )
        super().__init__(*args, **kwargs)
