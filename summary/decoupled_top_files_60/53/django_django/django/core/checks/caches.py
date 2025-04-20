from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

from . import Error, Tags, register

E001 = Error(
    "You must define a '%s' cache in your CACHES setting." % DEFAULT_CACHE_ALIAS,
    id='caches.E001',
)


@register(Tags.caches)
def check_default_cache_is_configured(app_configs, **kwargs):
    """
    Function to check if the default cache alias is configured in the Django settings.
    
    Args:
    app_configs (list): List of AppConfig instances for all installed apps.
    **kwargs: Additional keyword arguments.
    
    Returns:
    list: A list of error codes if the default cache alias is not configured, otherwise an empty list.
    
    This function is intended to be used as a Django app configuration check to ensure that the default cache alias is properly set in the Django settings file. If the default cache alias is not
    """

    if DEFAULT_CACHE_ALIAS not in settings.CACHES:
        return [E001]
    return []
