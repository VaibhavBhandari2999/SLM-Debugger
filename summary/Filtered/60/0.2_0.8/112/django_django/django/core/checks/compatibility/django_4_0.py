from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Function to check the CSRF trusted origins setting in Django.
    
    This function checks if the values in the CSRF_TRUSTED_ORIGINS setting are correctly formatted. Starting from Django 4.0, each origin in the setting must start with a scheme (http:// or https://).
    
    Parameters:
    - app_configs: Configuration objects for installed Django apps. This parameter is required by Django's app configuration hooks but is not used in this function.
    - kwargs: Additional keyword arguments. This parameter is required by Django
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
