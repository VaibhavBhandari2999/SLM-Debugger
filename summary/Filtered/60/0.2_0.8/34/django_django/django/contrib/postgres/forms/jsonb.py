import warnings

from django.forms import JSONField as BuiltinJSONField
from django.utils.deprecation import RemovedInDjango40Warning

__all__ = ['JSONField']


class JSONField(BuiltinJSONField):
    def __init__(self, *args, **kwargs):
        """
        Initializes a JSONField instance. This method is deprecated and should be replaced with django.forms.JSONField. It accepts variable positional arguments (*args) and keyword arguments (**kwargs). It also issues a warning when called, indicating that it will be removed in Django 4.0.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        None: This method does not return any value. It primarily serves to initialize the JSONField instance and issue a
        """

        warnings.warn(
            'django.contrib.postgres.forms.JSONField is deprecated in favor '
            'of django.forms.JSONField.',
            RemovedInDjango40Warning, stacklevel=2,
        )
        super().__init__(*args, **kwargs)
