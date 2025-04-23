from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Function to validate CSRF trusted origins in Django settings.
    
    This function checks if the values in the CSRF_TRUSTED_ORIGINS setting start with a scheme (http:// or https://).
    It returns a list of errors if any of the origins do not meet this requirement.
    
    Parameters:
    app_configs (list): A list of AppConfig instances for the Django application.
    kwargs (dict): Additional keyword arguments.
    
    Returns:
    list: A list of Error objects if any CSRF trusted origins are invalid, otherwise
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
