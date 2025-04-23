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
    
    This function checks if the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is set. If it is set, it returns a list containing a specific error code `E001`. Otherwise, it returns an empty list.
    
    Parameters:
    - app_configs: A list of AppConfig instances representing the application configurations.
    - **kwargs: Additional keyword arguments that can be passed to the function.
    
    Returns:
    - A list containing the error code `
    """

    if os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
        return [E001]
    return []
