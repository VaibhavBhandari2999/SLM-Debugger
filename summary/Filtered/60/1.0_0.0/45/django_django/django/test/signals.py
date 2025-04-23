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
        caches._caches = Local()


@receiver(setting_changed)
def update_installed_apps(**kwargs):
    """
    Update various Django caches and objects after modifying the 'INSTALLED_APPS' setting.
    
    This function is designed to clear caches and reload necessary Django components
    when the 'INSTALLED_APPS' setting is updated. This ensures that the system remains
    consistent and up-to-date with the latest configuration.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments. The only expected key is 'setting',
    which should be set to 'INSTALLED_APPS' for this function to execute.
    
    Returns:
    None: This function does
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
    if kwargs['enter'] and kwargs['setting'] in COMPLEX_OVERRIDE_SETTINGS:
        # Considering the current implementation of the signals framework,
        # this stacklevel shows the line containing the override_settings call.
        warnings.warn("Overriding setting %s can lead to unexpected behavior."
                      % kwargs['setting'], stacklevel=6)


@receiver(setting_changed)
def root_urlconf_changed(**kwargs):
    """
    Clears the URL caches and resets the URL configuration when the ROOT_URLCONF setting is changed.
    
    This function is designed to be used as a signal receiver for Django's settings_changed signal. It ensures that any changes to the ROOT_URLCONF setting are immediately reflected in the URL configuration.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments. Expected to include a 'setting' key with the value 'ROOT_URLCONF'.
    
    Returns:
    None: This function does not return any value. It performs side effects such
    """

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
    
    This function is used to invalidate the cache of static file finders when certain settings are changed. It is particularly useful when modifying `STATICFILES_DIRS` or `STATIC_ROOT`.
    
    Parameters:
    **kwargs: Arbitrary keyword arguments. The function checks if the provided `setting` key is either 'STATICFILES_DIRS' or 'STATIC_ROOT'.
    
    Returns:
    None: This function does not return anything. It clears the cache of the static file finders.
    
    Example
    """

    if kwargs['setting'] in {
        'STATICFILES_DIRS',
        'STATIC_ROOT',
    }:
        from django.contrib.staticfiles.finders import get_finder
        get_finder.cache_clear()


@receiver(setting_changed)
def auth_password_validators_changed(**kwargs):
    if kwargs['setting'] == 'AUTH_PASSWORD_VALIDATORS':
        from django.contrib.auth.password_validation import get_default_password_validators
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
s.UserModel = UserModel
