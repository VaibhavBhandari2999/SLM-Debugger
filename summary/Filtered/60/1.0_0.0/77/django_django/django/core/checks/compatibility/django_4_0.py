from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Function to validate the CSRF_TRUSTED_ORIGINS setting in Django.
    
    This function checks if each origin in the CSRF_TRUSTED_ORIGINS setting starts with a scheme (http:// or https://).
    If any origin does not start with a scheme, an error is appended to the errors list.
    
    Parameters:
    app_configs (list): A list of application configurations.
    kwargs (dict): Additional keyword arguments.
    
    Returns:
    list: A list of errors, where each error is an instance
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
