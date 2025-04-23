import os

from . import Error, Tags, register

E001 = Error(
    'You should not set the DJANGO_ALLOW_ASYNC_UNSAFE environment variable in '
    'deployment. This disables async safety protection.',
    id='async.E001',
)


@register(Tags.async_support, deploy=True)
def check_async_unsafe(app_configs, **kwargs):
    """
    Check for asynchronous unsafe operations in Django application configurations.
    
    This function checks if any Django application configurations are marked as asynchronous unsafe. If the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is set, the function returns an error code E001, indicating that asynchronous unsafe operations are allowed. Otherwise, it returns an empty list, indicating no issues.
    
    Args:
    app_configs (list): A list of Django application configurations.
    
    Returns:
    list: A list containing the error code E001
    """

    if os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
        return [E001]
    return []
