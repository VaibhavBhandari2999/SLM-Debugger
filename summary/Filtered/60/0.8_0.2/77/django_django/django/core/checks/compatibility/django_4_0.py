from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Function to validate CSRF trusted origins in Django settings.
    
    This function checks if the values in the CSRF_TRUSTED_ORIGINS setting of a Django application are correctly formatted. As of Django 4.0, each origin in the setting must start with a scheme (http:// or https://).
    
    Parameters:
    - app_configs: Configuration objects for the Django apps.
    - kwargs: Additional keyword arguments.
    
    Returns:
    - A list of Error objects if any of the origins are incorrectly formatted, otherwise an empty list
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
