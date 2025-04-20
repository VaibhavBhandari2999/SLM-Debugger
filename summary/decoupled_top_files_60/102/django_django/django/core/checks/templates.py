import copy
from collections import defaultdict

from django.conf import settings
from django.template.backends.django import get_template_tag_modules

from . import Error, Tags, register

E001 = Error(
    "You have 'APP_DIRS': True in your TEMPLATES but also specify 'loaders' "
    "in OPTIONS. Either remove APP_DIRS or remove the 'loaders' option.",
    id="templates.E001",
)
E002 = Error(
    "'string_if_invalid' in TEMPLATES OPTIONS must be a string but got: {} ({}).",
    id="templates.E002",
)
E003 = Error(
    "{} is used for multiple template tag modules: {}",
    id="templates.E003",
)


@register(Tags.templates)
def check_setting_app_dirs_loaders(app_configs, **kwargs):
    """
    Function to check for the use of `APP_DIRS` and `loaders` in Django template settings.
    
    This function is designed to validate Django template settings to ensure that `APP_DIRS` and `loaders` are not used together, as this can lead to unexpected behavior. It checks each template configuration in the `TEMPLATES` setting for the presence of `APP_DIRS` and `loaders` in the `OPTIONS` dictionary.
    
    Parameters:
    app_configs (list): A list of application configurations
    """

    return (
        [E001]
        if any(
            conf.get("APP_DIRS") and "loaders" in conf.get("OPTIONS", {})
            for conf in settings.TEMPLATES
        )
        else []
    )


@register(Tags.templates)
def check_string_if_invalid_is_string(app_configs, **kwargs):
    """
    Checks if the 'string_if_invalid' option in the Django template settings is a string.
    
    This function iterates over the TEMPLATES setting in Django's settings module. For each template configuration, it checks if the 'string_if_invalid' option is set and whether it is of type string. If 'string_if_invalid' is not a string, an error is appended to the errors list.
    
    Parameters:
    - app_configs: Not used in this function but required for the AppConfig.ready() method.
    -
    """

    errors = []
    for conf in settings.TEMPLATES:
        string_if_invalid = conf.get("OPTIONS", {}).get("string_if_invalid", "")
        if not isinstance(string_if_invalid, str):
            error = copy.copy(E002)
            error.msg = error.msg.format(
                string_if_invalid, type(string_if_invalid).__name__
            )
            errors.append(error)
    return errors


@register(Tags.templates)
def check_for_template_tags_with_the_same_name(app_configs, **kwargs):
    errors = []
    libraries = defaultdict(set)

    for conf in settings.TEMPLATES:
        custom_libraries = conf.get("OPTIONS", {}).get("libraries", {})
        for module_name, module_path in custom_libraries.items():
            libraries[module_name].add(module_path)

    for module_name, module_path in get_template_tag_modules():
        libraries[module_name].add(module_path)

    for library_name, items in libraries.items():
        if len(items) > 1:
            errors.append(
                Error(
                    E003.msg.format(
                        repr(library_name),
                        ", ".join(repr(item) for item in sorted(items)),
                    ),
                    id=E003.id,
                )
            )

    return errors
