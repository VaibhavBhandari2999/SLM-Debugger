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
    
    This function is designed to be used as a Django app configuration check. It verifies whether the default cache alias specified in the settings is present in the CACHES dictionary. If the default cache alias is not found, it returns a list containing an error code (E001). Otherwise, it returns an empty list indicating no issues.
    
    Parameters:
    app_configs (list): A list of app configuration objects.
    **
    """

    if DEFAULT_CACHE_ALIAS not in settings.CACHES:
        return [E001]
    return []
