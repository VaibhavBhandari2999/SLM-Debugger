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
    
    This function checks if the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is set. If it is not set, it returns a list containing a specific error code (E001). This is used to ensure that certain operations within the Django application are not executed in an asynchronous unsafe manner.
    
    Parameters:
    app_configs (list): A list of configuration objects for Django applications.
    **kwargs: Additional keyword arguments that are not used in this
    """

    if os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
        return [E001]
    return []
