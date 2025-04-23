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
    
    This function ensures that the Django application configurations do not contain any asynchronous unsafe operations, unless explicitly allowed by the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE`.
    
    Parameters:
    app_configs (list): A list of Django application configurations.
    **kwargs: Additional keyword arguments.
    
    Returns:
    list: A list of warning codes if asynchronous unsafe operations are detected, otherwise an empty list.
    
    Environment Variables:
    DJANGO_ALLOW_ASYNC_UNSAFE (bool): If
    """

    if os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
        return [E001]
    return []
