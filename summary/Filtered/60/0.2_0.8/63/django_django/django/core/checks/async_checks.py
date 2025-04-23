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
    Check if the Django application is configured to allow async unsafety.
    
    This function checks if the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is set.
    If it is set, it returns a list containing a specific error code `E001`, indicating that
    the application is configured to allow async unsafe operations. If the environment
    variable is not set, it returns an empty list, indicating that the application is
    configured to prevent async unsafe operations.
    
    Parameters:
    - app_configs (list):
    """

    if os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
        return [E001]
    return []
