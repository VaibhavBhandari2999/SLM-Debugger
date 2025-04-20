import warnings

from django.forms import JSONField as BuiltinJSONField
from django.utils.deprecation import RemovedInDjango40Warning

__all__ = ['JSONField']


class JSONField(BuiltinJSONField):
    def __init__(self, *args, **kwargs):
        """
        This function initializes an instance of a form field. It accepts variable positional arguments (*args) and keyword arguments (**kwargs). A deprecation warning is issued to users, advising them to use `django.forms.JSONField` instead of `django.contrib.postgres.forms.JSONField`. The function then calls its superclass's `__init__` method with the provided arguments.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        None: This function does not
        """

        warnings.warn(
            'django.contrib.postgres.forms.JSONField is deprecated in favor '
            'of django.forms.JSONField.',
            RemovedInDjango40Warning, stacklevel=2,
        )
        super().__init__(*args, **kwargs)
