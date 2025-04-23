import copy
from collections import defaultdict

from django.conf import settings
from django.template.backends.django import get_template_tag_modules

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
E003 = Error(
    '{} is used for multiple template tag modules: {}',
    id='templates.E003',
)


@register(Tags.templates)
def check_setting_app_dirs_loaders(app_configs, **kwargs):
    """
    Function to check for the presence of 'APP_DIRS' set to True and 'loaders' in OPTIONS for any template configuration in settings.TEMPLATES.
    
    Args:
    app_configs (list): List of application configurations.
    kwargs (dict): Additional keyword arguments.
    
    Returns:
    list: A list containing the error code E001 if 'APP_DIRS' is set to True and 'loaders' is present in OPTIONS for any template configuration, otherwise an empty list.
    
    This function is used
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


@register(Tags.templates)
def check_for_template_tags_with_the_same_name(app_configs, **kwargs):
    """
    Check for template tags with the same name.
    
    This function checks for duplicate template tag names across different template libraries. It collects all custom template libraries from the settings and also includes any custom template tag modules. It then checks for any template tag names that are defined in more than one library and returns a list of errors.
    
    Parameters:
    app_configs (list): A list of application configurations.
    kwargs (dict): Additional keyword arguments (not used in this function).
    
    Returns:
    list: A list of
    """

    errors = []
    libraries = defaultdict(list)

    for conf in settings.TEMPLATES:
        custom_libraries = conf.get('OPTIONS', {}).get('libraries', {})
        for module_name, module_path in custom_libraries.items():
            libraries[module_name].append(module_path)

    for module_name, module_path in get_template_tag_modules():
        libraries[module_name].append(module_path)

    for library_name, items in libraries.items():
        if len(items) > 1:
            errors.append(Error(
                E003.msg.format(
                    repr(library_name),
                    ', '.join(repr(item) for item in items),
                ),
                id=E003.id,
            ))

    return errors
