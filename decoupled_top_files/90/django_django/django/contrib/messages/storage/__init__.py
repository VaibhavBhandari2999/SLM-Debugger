"""
The provided Python file contains a single function `default_storage` which dynamically imports and returns an instance of the message storage class specified in Django's settings. This function ensures that the storage mechanism for messages can be easily changed without modifying the core logic of the application. The file also imports necessary modules from Django to facilitate this functionality. ```python
"""
from django.conf import settings
from django.utils.module_loading import import_string


def default_storage(request):
    """
    Callable with the same interface as the storage classes.

    This isn't just default_storage = import_string(settings.MESSAGE_STORAGE)
    to avoid accessing the settings at the module level.
    """
    return import_string(settings.MESSAGE_STORAGE)(request)
