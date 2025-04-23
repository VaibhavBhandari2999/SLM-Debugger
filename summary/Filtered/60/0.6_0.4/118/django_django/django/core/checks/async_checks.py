import os

from . import Error, Tags, register

E001 = Error(
    "You should not set the DJANGO_ALLOW_ASYNC_UNSAFE environment variable in "
    "deployment. This disables async safety protection.",
    id="async.E001",
)


@register(Tags.async_support, deploy=True)
def check_async_unsafe(app_configs, **kwargs):
    """
    Check if the Django application is configured to allow async unsafety.
    
    This function checks if the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is set. If it is set, it indicates that the application is configured to allow async unsafety, which can lead to potential issues with asynchronous operations. If the environment variable is not set, the function returns without any issues.
    
    Parameters:
    app_configs (list): A list of configuration objects for the Django application.
    **kwargs: Additional keyword arguments.
    """

    if os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE"):
        return [E001]
    return []
