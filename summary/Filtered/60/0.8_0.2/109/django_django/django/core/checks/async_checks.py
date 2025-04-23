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
    Function to check if the Django application is configured to allow asynchronous unsafe operations.
    
    Parameters:
    app_configs (list): A list of AppConfig instances representing the application configurations.
    **kwargs: Additional keyword arguments that may be passed to the function.
    
    Returns:
    list: A list of error codes or messages indicating whether the application is configured to allow asynchronous unsafe operations.
    
    Environment Variable:
    DJANGO_ALLOW_ASYNC_UNSAFE: If set, it allows the application to perform asynchronous unsafe operations.
    """

    if os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE"):
        return [E001]
    return []
