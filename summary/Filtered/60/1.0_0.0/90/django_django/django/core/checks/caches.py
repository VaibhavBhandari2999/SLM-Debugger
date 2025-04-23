import pathlib

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.core.cache.backends.filebased import FileBasedCache

from . import Error, Tags, Warning, register

E001 = Error(
    "You must define a '%s' cache in your CACHES setting." % DEFAULT_CACHE_ALIAS,
    id='caches.E001',
)


@register(Tags.caches)
def check_default_cache_is_configured(app_configs, **kwargs):
    """
    Function to check if the default cache alias is configured in the Django settings.
    
    Args:
    app_configs (list): A list of AppConfig instances for the currently registered apps.
    **kwargs: Additional keyword arguments.
    
    Returns:
    list: A list of error codes if the default cache alias is not found in the CACHES setting, otherwise an empty list.
    
    This function is intended to be used as a check function in Django's app configuration process. It verifies that the default cache alias is properly configured
    """

    if DEFAULT_CACHE_ALIAS not in settings.CACHES:
        return [E001]
    return []


@register(Tags.caches, deploy=True)
def check_cache_location_not_exposed(app_configs, **kwargs):
    errors = []
    for name in ('MEDIA_ROOT', 'STATIC_ROOT', 'STATICFILES_DIRS'):
        setting = getattr(settings, name, None)
        if not setting:
            continue
        if name == 'STATICFILES_DIRS':
            paths = set()
            for staticfiles_dir in setting:
                if isinstance(staticfiles_dir, (list, tuple)):
                    _, staticfiles_dir = staticfiles_dir
                paths.add(pathlib.Path(staticfiles_dir).resolve())
        else:
            paths = {pathlib.Path(setting).resolve()}
        for alias in settings.CACHES:
            cache = caches[alias]
            if not isinstance(cache, FileBasedCache):
                continue
            cache_path = pathlib.Path(cache._dir).resolve()
            if any(path == cache_path for path in paths):
                relation = 'matches'
            elif any(path in cache_path.parents for path in paths):
                relation = 'is inside'
            elif any(cache_path in path.parents for path in paths):
                relation = 'contains'
            else:
                continue
            errors.append(Warning(
                f"Your '{alias}' cache configuration might expose your cache "
                f"or lead to corruption of your data because its LOCATION "
                f"{relation} {name}.",
                id='caches.W002',
            ))
    return errors


@register(Tags.caches)
def check_file_based_cache_is_absolute(app_configs, **kwargs):
    """
    Function to check if the cache LOCATION path is absolute for file-based caches.
    
    This function iterates through the cache configurations in the Django settings and checks if the LOCATION path for file-based caches is absolute. If a relative path is found, it generates a warning.
    
    Parameters:
    - app_configs: A list of AppConfig instances. Not used in this function.
    - kwargs: Additional keyword arguments. Not used in this function.
    
    Returns:
    - A list of warnings (if any) indicating relative paths for file-based
    """

    errors = []
    for alias, config in settings.CACHES.items():
        cache = caches[alias]
        if not isinstance(cache, FileBasedCache):
            continue
        if not pathlib.Path(config['LOCATION']).is_absolute():
            errors.append(Warning(
                f"Your '{alias}' cache LOCATION path is relative. Use an "
                f"absolute path instead.",
                id='caches.W003',
            ))
    return errors
