from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Function to validate CSRF trusted origins in Django settings.
    
    This function checks the CSRF_TRUSTED_ORIGINS setting in Django settings for compliance with the new requirement introduced in Django 4.0. Each origin in the setting must start with a scheme (http:// or https://).
    
    Parameters:
    - app_configs: The application configuration objects. This parameter is required by Django's app loading process and is not used within this function.
    - kwargs: Additional keyword arguments. This parameter is required by Django's app
    """

    errors = []
    for origin in settings.CSRF_TRUSTED_ORIGINS:
        if "://" not in origin:
            errors.append(
                Error(
                    "As of Django 4.0, the values in the CSRF_TRUSTED_ORIGINS "
                    "setting must start with a scheme (usually http:// or "
                    "https://) but found %s. See the release notes for details."
                    % origin,
                    id="4_0.E001",
                )
            )
    return errors
