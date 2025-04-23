import os
import time
import warnings

from asgiref.local import Local

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.db import connections, router
from django.db.utils import ConnectionRouter
from django.dispatch import Signal, receiver
from django.utils import timezone
from django.utils.formats import FORMAT_SETTINGS, reset_format_cache
from django.utils.functional import empty

template_rendered = Signal()

# Most setting_changed receivers are supposed to be added below,
# except for cases where the receiver is related to a contrib app.

# Settings that may not work well when using 'override_settings' (#19031)
COMPLEX_OVERRIDE_SETTINGS = {'DATABASES'}


@receiver(setting_changed)
def clear_cache_handlers(**kwargs):
    if kwargs['setting'] == 'CACHES':
        from django.core.cache import caches, close_caches
        close_caches()
        caches._settings = caches.settings = caches.configure_settings(None)
        caches._connections = Local()


@receiver(setting_changed)
def update_installed_apps(**kwargs):
    """
    Update various caches and settings in Django after modifying the 'INSTALLED_APPS' setting.
    
    This function is designed to clear caches and reload necessary components in Django when the 'INSTALLED_APPS' setting is updated. It performs the following actions:
    - Clears the cache for AppDirectoriesFinder instances.
    - Clears the cache for management commands.
    - Clears the cache for application template directories.
    - Clears the translations cache.
    
    Parameters:
    **kwargs: Keyword arguments containing the setting to be updated. The function expects the key
    """

    if kwargs['setting'] == 'INSTALLED_APPS':
        # Rebuild any AppDirectoriesFinder instance.
        from django.contrib.staticfiles.finders import get_finder
        get_finder.cache_clear()
        # Rebuild management commands cache
        from django.core.management import get_commands
        get_commands.cache_clear()
        # Rebuild get_app_template_dirs cache.
        from django.template.utils import get_app_template_dirs
        get_app_template_dirs.cache_clear()
        # Rebuild translations cache.
        from django.utils.translation import trans_real
        trans_real._translations = {}


@receiver(setting_changed)
def update_connections_time_zone(**kwargs):
    if kwargs['setting'] == 'TIME_ZONE':
        # Reset process time zone
        if hasattr(time, 'tzset'):
            if kwargs['value']:
                os.environ['TZ'] = kwargs['value']
            else:
                os.environ.pop('TZ', None)
            time.tzset()

        # Reset local time zone cache
        timezone.get_default_timezone.cache_clear()

    # Reset the database connections' time zone
    if kwargs['setting'] in {'TIME_ZONE', 'USE_TZ'}:
        for conn in connections.all():
            try:
                del conn.timezone
            except AttributeError:
                pass
            try:
                del conn.timezone_name
            except AttributeError:
                pass
            conn.ensure_timezone()


@receiver(setting_changed)
def clear_routers_cache(**kwargs):
    if kwargs['setting'] == 'DATABASE_ROUTERS':
        router.routers = ConnectionRouter().routers


@receiver(setting_changed)
def reset_template_engines(**kwargs):
    if kwargs['setting'] in {
        'TEMPLATES',
        'DEBUG',
        'INSTALLED_APPS',
    }:
        from django.template import engines
        try:
            del engines.templates
        except AttributeError:
            pass
        engines._templates = None
        engines._engines = {}
        from django.template.engine import Engine
        Engine.get_default.cache_clear()
        from django.forms.renderers import get_default_renderer
        get_default_renderer.cache_clear()


@receiver(setting_changed)
def clear_serializers_cache(**kwargs):
    """
    Clears the cache of Django's serialization modules.
    
    This function is used to reset the cache of serializers in Django, which can be useful when changing the settings for serialization modules.
    
    Parameters:
    setting (str): The setting key to check. Expected value is 'SERIALIZATION_MODULES'.
    
    Returns:
    None: This function does not return any value. It updates the internal state of Django's serializers module.
    
    Example:
    clear_serializers_cache(setting='SERIALIZATION_MODULES')
    """

    if kwargs['setting'] == 'SERIALIZATION_MODULES':
        from django.core import serializers
        serializers._serializers = {}


@receiver(setting_changed)
def language_changed(**kwargs):
    if kwargs['setting'] in {'LANGUAGES', 'LANGUAGE_CODE', 'LOCALE_PATHS'}:
        from django.utils.translation import trans_real
        trans_real._default = None
        trans_real._active = Local()
    if kwargs['setting'] in {'LANGUAGES', 'LOCALE_PATHS'}:
        from django.utils.translation import trans_real
        trans_real._translations = {}
        trans_real.check_for_language.cache_clear()


@receiver(setting_changed)
def localize_settings_changed(**kwargs):
    if kwargs['setting'] in FORMAT_SETTINGS or kwargs['setting'] == 'USE_THOUSAND_SEPARATOR':
        reset_format_cache()


@receiver(setting_changed)
def file_storage_changed(**kwargs):
    if kwargs['setting'] == 'DEFAULT_FILE_STORAGE':
        from django.core.files.storage import default_storage
        default_storage._wrapped = empty


@receiver(setting_changed)
def complex_setting_changed(**kwargs):
    """
    Warns about overriding complex settings.
    
    This function is triggered when a setting is overridden during a test. If the setting is in the `COMPLEX_OVERRIDE_SETTINGS` list and the `enter` flag is set to `True`, a warning is issued to inform the user that overriding this setting can lead to unexpected behavior. The warning is raised with a stack level of 6 to pinpoint the exact location of the override_settings call.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments. Expected keys are 'enter
    """

    if kwargs['enter'] and kwargs['setting'] in COMPLEX_OVERRIDE_SETTINGS:
        # Considering the current implementation of the signals framework,
        # this stacklevel shows the line containing the override_settings call.
        warnings.warn("Overriding setting %s can lead to unexpected behavior."
                      % kwargs['setting'], stacklevel=6)


@receiver(setting_changed)
def root_urlconf_changed(**kwargs):
    if kwargs['setting'] == 'ROOT_URLCONF':
        from django.urls import clear_url_caches, set_urlconf
        clear_url_caches()
        set_urlconf(None)


@receiver(setting_changed)
def static_storage_changed(**kwargs):
    if kwargs['setting'] in {
        'STATICFILES_STORAGE',
        'STATIC_ROOT',
        'STATIC_URL',
    }:
        from django.contrib.staticfiles.storage import staticfiles_storage
        staticfiles_storage._wrapped = empty


@receiver(setting_changed)
def static_finders_changed(**kwargs):
    """
    Clear the cache of static file finders.
    
    This function is designed to clear the cache of static file finders in Django, which is useful when the settings related to static files have changed.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments. This function specifically looks for changes in 'STATICFILES_DIRS' and 'STATIC_ROOT' settings.
    
    Returns:
    None: This function does not return anything. It clears the cache of the static file finders.
    """

    if kwargs['setting'] in {
        'STATICFILES_DIRS',
        'STATIC_ROOT',
    }:
        from django.contrib.staticfiles.finders import get_finder
        get_finder.cache_clear()


@receiver(setting_changed)
def auth_password_validators_changed(**kwargs):
    """
    Clear the cache of default password validators.
    
    This function is triggered when the 'AUTH_PASSWORD_VALIDATORS' setting changes. It clears the cache of default password validators to ensure that the latest configuration is used.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments. This function expects the 'setting' key to be present and should have a value of 'AUTH_PASSWORD_VALIDATORS'.
    
    Returns:
    None: This function does not return anything. It modifies the cache in place.
    
    Example:
    >>> auth_password_validators
    """

    if kwargs['setting'] == 'AUTH_PASSWORD_VALIDATORS':
        from django.contrib.auth.password_validation import (
            get_default_password_validators,
        )
        get_default_password_validators.cache_clear()


@receiver(setting_changed)
def user_model_swapped(**kwargs):
    if kwargs['setting'] == 'AUTH_USER_MODEL':
        apps.clear_cache()
        try:
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
        except ImproperlyConfigured:
            # Some tests set an invalid AUTH_USER_MODEL.
            pass
        else:
            from django.contrib.auth import backends
            backends.UserModel = UserModel

            from django.contrib.auth import forms
            forms.UserModel = UserModel

            from django.contrib.auth.handlers import modwsgi
            modwsgi.UserModel = UserModel

            from django.contrib.auth.management.commands import changepassword
            changepassword.UserModel = UserModel

            from django.contrib.auth import views
            views.UserModel = UserModel
erModel = UserModel
