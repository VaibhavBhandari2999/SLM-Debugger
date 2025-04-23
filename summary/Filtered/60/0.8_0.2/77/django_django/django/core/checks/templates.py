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
    Function to check for the presence of 'APP_DIRS' and 'loaders' in the TEMPLATES settings.
    
    This function is designed to validate the Django settings related to template handling. It checks if any template configuration in the TEMPLATES setting has both 'APP_DIRS' set to True and 'loaders' specified in the OPTIONS. If such a configuration is found, it returns a list containing the error code E001. Otherwise, it returns an empty list.
    
    Parameters:
    app
    """

    return [E001] if any(
        conf.get('APP_DIRS') and 'loaders' in conf.get('OPTIONS', {})
        for conf in settings.TEMPLATES
    ) else []


@register(Tags.templates)
def check_string_if_invalid_is_string(app_configs, **kwargs):
    """
    Checks if the 'string_if_invalid' option in the Django template settings is a string.
    
    This function iterates over the TEMPLATES setting in Django settings. For each template configuration, it checks if the 'string_if_invalid' option is set and whether it is a string. If 'string_if_invalid' is not a string, an error is appended to the errors list.
    
    Parameters:
    app_configs (list): A list of application configurations.
    kwargs (dict): Additional keyword arguments.
    
    Returns
    """

    errors = []
    for conf in settings.TEMPLATES:
        string_if_invalid = conf.get('OPTIONS', {}).get('string_if_invalid', '')
        if not isinstance(string_if_invalid, str):
            error = copy.copy(E002)
            error.msg = error.msg.format(string_if_invalid, type(string_if_invalid).__name__)
            errors.append(error)
    return errors
