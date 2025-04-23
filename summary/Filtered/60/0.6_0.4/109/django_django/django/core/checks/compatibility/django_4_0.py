from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Function to validate CSRF trusted origins.
    
    This function checks the CSRF_TRUSTED_ORIGINS setting for the presence of a scheme (http:// or https://) in each origin. It returns a list of errors if any origin is missing a scheme.
    
    Parameters:
    - app_configs: Configuration objects for installed Django apps. Not used in this function.
    - kwargs: Additional keyword arguments. Not used in this function.
    
    Returns:
    - A list of Django error objects if any origin in CSRF_TRUSTED_OR
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
