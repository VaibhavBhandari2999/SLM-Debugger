from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Function to validate CSRF trusted origins in Django settings.
    
    This function checks if all origins in the CSRF_TRUSTED_ORIGINS setting start with a scheme (http:// or https://).
    It returns a list of errors if any origin is missing the scheme.
    
    Parameters:
    - app_configs: Configuration objects for installed Django apps.
    - kwargs: Additional keyword arguments.
    
    Returns:
    - A list of errors (if any) found in the CSRF_TRUSTED_ORIGINS setting.
    
    Note:
    - This function is
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
