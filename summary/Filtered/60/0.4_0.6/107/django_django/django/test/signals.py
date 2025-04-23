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
COMPLEX_OVERRIDE_SETTINGS = {"DATABASES"}


@receiver(setting_changed)
def clear_cache_handlers(*, setting, **kwargs):
    """
    Clears the Django cache handlers.
    
    This function is used to clear the cache handlers for the Django application.
    
    Parameters:
    setting (str): The setting to clear, specifically "CACHES".
    
    Keyword Arguments:
    None
    
    Returns:
    None: This function does not return anything. It clears the cache handlers in place.
    
    Example:
    clear_cache_handlers(setting="CACHES")
    """

    if setting == "CACHES":
        from django.core.cache import caches, close_caches

        close_caches()
        caches._settings = caches.settings = caches.configure_settings(None)
        caches._connections = Local()


@receiver(setting_changed)
def update_installed_apps(*, setting, **kwargs):
    if setting == "INSTALLED_APPS":
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
def update_connections_time_zone(*, setting, **kwargs):
    if setting == "TIME_ZONE":
        # Reset process time zone
        if hasattr(time, "tzset"):
            if kwargs["value"]:
                os.environ["TZ"] = kwargs["value"]
            else:
                os.environ.pop("TZ", None)
            time.tzset()

        # Reset local time zone cache
        timezone.get_default_timezone.cache_clear()

    # Reset the database connections' time zone
    if setting in {"TIME_ZONE", "USE_TZ"}:
        for conn in connections.all(initialized_only=True):
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
def clear_routers_cache(*, setting, **kwargs):
    if setting == "DATABASE_ROUTERS":
        router.routers = ConnectionRouter().routers


@receiver(setting_changed)
def reset_template_engines(*, setting, **kwargs):
    """
    Reset Django template engines.
    
    This function clears the cached template engines and reloads them with the provided settings.
    
    Parameters:
    setting (str): The setting to reset, which can be one of the following:
    - 'TEMPLATES': Resets the template configurations.
    - 'DEBUG': Resets the debug settings.
    - 'INSTALLED_APPS': Resets the installed applications.
    
    Keyword Arguments:
    kwargs: Additional keyword arguments that are not used in this function but may be required for other functions that call this
    """

    if setting in {
        "TEMPLATES",
        "DEBUG",
        "INSTALLED_APPS",
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
def clear_serializers_cache(*, setting, **kwargs):
    if setting == "SERIALIZATION_MODULES":
        from django.core import serializers

        serializers._serializers = {}


@receiver(setting_changed)
def language_changed(*, setting, **kwargs):
    """
    Change the language settings for Django translations.
    
    This function updates the translation settings based on the provided parameters.
    
    Parameters:
    setting (str): The setting to change, which can be one of the following:
    - 'LANGUAGES': Update the list of supported languages.
    - 'LANGUAGE_CODE': Set the default language code.
    - 'LOCALE_PATHS': Update the paths where Django looks for locale files.
    
    kwargs: Additional keyword arguments (currently not used in the function).
    
    Returns:
    """

    if setting in {"LANGUAGES", "LANGUAGE_CODE", "LOCALE_PATHS"}:
        from django.utils.translation import trans_real

        trans_real._default = None
        trans_real._active = Local()
    if setting in {"LANGUAGES", "LOCALE_PATHS"}:
        from django.utils.translation import trans_real

        trans_real._translations = {}
        trans_real.check_for_language.cache_clear()


@receiver(setting_changed)
def localize_settings_changed(*, setting, **kwargs):
    if setting in FORMAT_SETTINGS or setting == "USE_THOUSAND_SEPARATOR":
        reset_format_cache()


@receiver(setting_changed)
def file_storage_changed(*, setting, **kwargs):
    if setting == "DEFAULT_FILE_STORAGE":
        from django.core.files.storage import default_storage

        default_storage._wrapped = empty


@receiver(setting_changed)
def complex_setting_changed(*, enter, setting, **kwargs):
    if enter and setting in COMPLEX_OVERRIDE_SETTINGS:
        # Considering the current implementation of the signals framework,
        # this stacklevel shows the line containing the override_settings call.
        warnings.warn(
            f"Overriding setting {setting} can lead to unexpected behavior.",
            stacklevel=6,
        )


@receiver(setting_changed)
def root_urlconf_changed(*, setting, **kwargs):
    if setting == "ROOT_URLCONF":
        from django.urls import clear_url_caches, set_urlconf

        clear_url_caches()
        set_urlconf(None)


@receiver(setting_changed)
def static_storage_changed(*, setting, **kwargs):
    if setting in {
        "STATICFILES_STORAGE",
        "STATIC_ROOT",
        "STATIC_URL",
    }:
        from django.contrib.staticfiles.storage import staticfiles_storage

        staticfiles_storage._wrapped = empty


@receiver(setting_changed)
def static_finders_changed(*, setting, **kwargs):
    if setting in {
        "STATICFILES_DIRS",
        "STATIC_ROOT",
    }:
        from django.contrib.staticfiles.finders import get_finder

        get_finder.cache_clear()


@receiver(setting_changed)
def auth_password_validators_changed(*, setting, **kwargs):
    """
    Clears the cache of default password validators.
    
    This function is triggered when the 'AUTH_PASSWORD_VALIDATORS' setting changes. It clears the cache of default password validators to ensure that the latest configuration is used.
    
    Parameters:
    setting (str): The setting that has changed ('AUTH_PASSWORD_VALIDATORS' in this case).
    
    Returns:
    None: This function does not return any value. It only clears the cache.
    """

    if setting == "AUTH_PASSWORD_VALIDATORS":
        from django.contrib.auth.password_validation import (
            get_default_password_validators,
        )

        get_default_password_validators.cache_clear()


@receiver(setting_changed)
def user_model_swapped(*, setting, **kwargs):
    if setting == "AUTH_USER_MODEL":
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
