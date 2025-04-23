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
    Clears the cache handlers based on the given setting.
    
    This function is used to clear the cache handlers in Django applications.
    
    Parameters:
    setting (str): The setting to clear the cache for. Currently, it should be set to "CACHES".
    **kwargs: Additional keyword arguments. Currently, no additional keyword arguments are used.
    
    Returns:
    None: This function does not return any value. It modifies the cache settings and connections directly.
    
    Note:
    - The function uses Django's internal
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
    """
    Updates the time zone settings for database connections and the process.
    
    This function adjusts the time zone settings for database connections and the process environment based on the provided setting and value.
    
    Parameters:
    setting (str): The setting to update, either 'TIME_ZONE' or 'USE_TZ'.
    value (str, optional): The new time zone value to set. Required if setting is 'TIME_ZONE'. Ignored if setting is 'USE_TZ'.
    
    Keywords:
    **kwargs: Additional keyword arguments.
    """

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
    
    This function clears the cached template engines and related configurations.
    
    Parameters:
    setting (str): The setting to check against. Must be one of 'TEMPLATES', 'DEBUG', or 'INSTALLED_APPS'.
    **kwargs: Additional keyword arguments (not used in this function).
    
    Returns:
    None: This function does not return any value. It modifies the global state of Django template engines.
    
    Note:
    This function is intended for use in development or testing environments where template configurations
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
    """
    Clears the URL caches and sets the URL configuration to None when the ROOT_URLCONF setting is changed.
    
    Parameters:
    setting (str): The setting that has been changed. Expected to be "ROOT_URLCONF".
    
    Returns:
    None: This function does not return any value. It clears the URL caches and resets the URL configuration.
    
    Notes:
    This function is typically used in Django to ensure that URL patterns are reloaded when the ROOT_URLCONF setting changes.
    """

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
