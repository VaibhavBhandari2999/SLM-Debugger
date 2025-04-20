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
    Checks if the Django application is configured to allow asynchronous operations.
    
    This function is designed to be used as a Django app configuration check. It verifies whether the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is set. If this variable is set, it indicates that the application is configured to allow potentially unsafe asynchronous operations, which might lead to issues in a multi-threaded environment.
    
    Parameters:
    app_configs (list): A list of Django app configuration objects.
    **kwargs: Additional keyword arguments that can
    """

    if os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
        return [E001]
    return []
