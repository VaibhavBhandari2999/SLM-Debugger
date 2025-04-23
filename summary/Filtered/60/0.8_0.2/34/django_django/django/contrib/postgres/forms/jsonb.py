import warnings

from django.forms import JSONField as BuiltinJSONField
from django.utils.deprecation import RemovedInDjango40Warning

__all__ = ['JSONField']


class JSONField(BuiltinJSONField):
    def __init__(self, *args, **kwargs):
        """
        Initializes a JSONField instance. This method is deprecated in favor of using django.forms.JSONField. It accepts variable positional arguments (*args) and keyword arguments (**kwargs). It also issues a warning using the warnings module, indicating that it is being replaced by django.forms.JSONField. The method then calls its superclass's __init__ method with the provided arguments.
        
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        :raises: RemovedInDjango40Warning:
        """

        warnings.warn(
            'django.contrib.postgres.forms.JSONField is deprecated in favor '
            'of django.forms.JSONField.',
            RemovedInDjango40Warning, stacklevel=2,
        )
        super().__init__(*args, **kwargs)
