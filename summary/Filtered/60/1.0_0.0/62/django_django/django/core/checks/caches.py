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
    if DEFAULT_CACHE_ALIAS not in settings.CACHES:
        return [E001]
    return []


@register(Tags.caches, deploy=True)
def check_cache_location_not_exposed(app_configs, **kwargs):
    """
    Check if cache locations are not exposed to media or static files.
    
    This function checks if the cache locations are configured in a way that they
    might expose sensitive data or lead to data corruption. It examines the
    settings for `MEDIA_ROOT`, `STATIC_ROOT`, and `STATICFILES_DIRS` and compares
    them with the cache directories defined in the `CACHES` setting.
    
    Parameters:
    app_configs (list): A list of application configurations.
    **kwargs: Additional keyword arguments.
    
    Returns:
    """

    errors = []
    for name in ('MEDIA_ROOT', 'STATIC_ROOT', 'STATICFILES_DIRS'):
        setting = getattr(settings, name, None)
        if not setting:
            continue
        if name == 'STATICFILES_DIRS':
            paths = {
                pathlib.Path(staticfiles_dir).resolve()
                for staticfiles_dir in setting
            }
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
    
    This function iterates through the cache configurations in the Django settings. It checks if the cache is file-based and if the LOCATION path is absolute. If the path is relative, a warning is generated.
    
    Parameters:
    app_configs (list): List of application configurations.
    kwargs (dict): Additional keyword arguments.
    
    Returns:
    list: A list of warnings if the LOCATION path is relative, otherwise an empty list.
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
