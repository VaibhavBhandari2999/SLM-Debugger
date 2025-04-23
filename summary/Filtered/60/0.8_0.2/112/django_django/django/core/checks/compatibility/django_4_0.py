from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Function to check the CSRF trusted origins configuration.
    
    This function validates the settings.CSRF_TRUSTED_ORIGINS configuration to ensure that each origin starts with a scheme (http:// or https://). This is a requirement as of Django 4.0.
    
    Parameters:
    app_configs (Any): Configuration details of the Django apps.
    kwargs (Any): Additional keyword arguments.
    
    Returns:
    list: A list of errors if any origin in CSRF_TRUSTED_ORIGINS does not start with
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
