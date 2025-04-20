import copy

from django.conf import settings

from . import Error, Tags, register

E001 = Error(
    "You have 'APP_DIRS': True in your TEMPLATES but also specify 'loaders' "
    "in OPTIONS. Either remove APP_DIRS or remove the 'loaders' option.",
    id='templates.E001',
)
E002 = Error(
    "'string_if_invalid' in TEMPLATES OPTIONS must be a string but got: {} ({}).",
    id="templates.E002",
)


@register(Tags.templates)
def check_setting_app_dirs_loaders(app_configs, **kwargs):
    """
    Function: check_setting_app_dirs_loaders
    
    This function checks if any of the settings in the TEMPLATES configuration have both 'APP_DIRS' set to True and 'loaders' specified in the OPTIONS. If such a configuration is found, it returns a list containing the error code E001. Otherwise, it returns an empty list.
    
    Parameters:
    - app_configs: A list of application configurations. Not used in this function but included for compatibility with Django's signal handling.
    - kwargs
    """

    return [E001] if any(
        conf.get('APP_DIRS') and 'loaders' in conf.get('OPTIONS', {})
        for conf in settings.TEMPLATES
    ) else []


@register(Tags.templates)
def check_string_if_invalid_is_string(app_configs, **kwargs):
    errors = []
    for conf in settings.TEMPLATES:
        string_if_invalid = conf.get('OPTIONS', {}).get('string_if_invalid', '')
        if not isinstance(string_if_invalid, str):
            error = copy.copy(E002)
            error.msg = error.msg.format(string_if_invalid, type(string_if_invalid).__name__)
            errors.append(error)
    return errors
