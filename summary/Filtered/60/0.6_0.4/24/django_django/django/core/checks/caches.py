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
    
    This function is designed to be used as a check function in Django's apps registry. It verifies whether the default cache alias specified in the `settings.CACHES` dictionary is properly configured.
    
    Parameters:
    app_configs (list): A list of AppConfig instances for all installed apps.
    **kwargs: Additional keyword arguments passed to the check function.
    
    Returns:
    list: A list of warning codes if the default cache alias is
    """

    if DEFAULT_CACHE_ALIAS not in settings.CACHES:
        return [E001]
    return []
