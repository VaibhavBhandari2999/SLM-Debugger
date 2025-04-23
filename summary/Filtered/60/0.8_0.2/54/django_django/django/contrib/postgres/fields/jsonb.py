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
        This function initializes a KeyTransform object. It issues a deprecation warning to users, advising them to use `django.db.models.fields.json.KeyTransform` instead. The function accepts any number of positional arguments (`*args`) and keyword arguments (`**kwargs`). It then calls the superclass's `__init__` method with the provided arguments.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        None: This function does not return any value.
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
        This function initializes a KeyTextTransform object. It issues a deprecation warning, indicating that the use of `django.contrib.postgres.fields.jsonb.KeyTextTransform` is deprecated in favor of `django.db.models.fields.json.KeyTextTransform`. The function accepts any number of positional arguments (*args) and keyword arguments (**kwargs). It then calls the superclass's `__init__` method with the provided arguments.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments
        """

        warnings.warn(
            'django.contrib.postgres.fields.jsonb.KeyTextTransform is '
            'deprecated in favor of '
            'django.db.models.fields.json.KeyTextTransform.',
            RemovedInDjango40Warning, stacklevel=2,
        )
        super().__init__(*args, **kwargs)
