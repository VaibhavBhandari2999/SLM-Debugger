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
    Check for asynchronous unsafety in Django applications.
    
    This function checks if the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is set. If it is not set, it returns a list containing a specific error code `E001`. This function is typically used in Django's app configuration checks.
    
    Parameters:
    app_configs (list): A list of application configurations.
    **kwargs: Additional keyword arguments.
    
    Returns:
    list: A list containing the error code `E001` if
    """

    if os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
        return [E001]
    return []
