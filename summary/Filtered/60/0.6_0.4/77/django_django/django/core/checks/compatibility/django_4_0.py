from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Function to validate CSRF trusted origins in Django settings.
    
    This function checks if each origin in the CSRF_TRUSTED_ORIGINS setting starts with a scheme (http:// or https://).
    If any origin does not start with a scheme, it raises an error.
    
    Parameters:
    app_configs (object): Django application configuration objects.
    kwargs (dict): Additional keyword arguments.
    
    Returns:
    list: A list of errors if any origin is not correctly formatted, otherwise an empty list.
    
    Note:
    This
    """

    errors = []
    for origin in settings.CSRF_TRUSTED_ORIGINS:
        if '://' not in origin:
            errors.append(Error(
                'As of Django 4.0, the values in the CSRF_TRUSTED_ORIGINS '
                'setting must start with a scheme (usually http:// or '
                'https://) but found %s. See the release notes for details.'
                % origin,
                id='4_0.E001',
            ))
    return errors
