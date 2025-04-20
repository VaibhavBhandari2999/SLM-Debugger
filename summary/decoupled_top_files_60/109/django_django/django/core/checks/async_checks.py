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
    Check if the Django application is configured to allow asynchronous unsafe operations.
    
    This function checks if the environment variable `DJANGO_ALLOW_ASYNC_UNSAFE` is set. If it is set, it indicates that the application is configured to allow potentially unsafe asynchronous operations, which can lead to race conditions and other concurrency issues. The function returns a list containing a specific error code `E001` if the environment variable is set, otherwise it returns an empty list.
    
    Parameters:
    - app_configs (list): A
    """

    if os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE"):
        return [E001]
    return []
