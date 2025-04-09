"""
The provided Python file is part of a Django project and serves to ensure that the `CSRF_TRUSTED_ORIGINS` setting is correctly configured according to Django's security guidelines. Specifically, it checks that each origin in the `CSRF_TRUSTED_ORIGINS` setting starts with a scheme (e.g., `http://` or `https://`). If any origin is improperly formatted, it generates an error message detailing the issue.

#### Key Components:
- **Class/Function Definitions**:
  - **`check_csrf_trusted_origins`**: This function is registered as a checker for compatibility issues using the `register` decorator from the `django.utils.lru_cache` module. It takes `app_configs` and `
"""
from django.conf import settings

from .. import Error, Tags, register


@register(Tags.compatibility)
def check_csrf_trusted_origins(app_configs, **kwargs):
    """
    Check that all origins in CSRF_TRUSTED_ORIGINS setting are properly formatted.
    
    Args:
    app_configs: Configuration objects for installed Django apps.
    kwargs: Additional keyword arguments.
    
    Returns:
    A list of `Error` objects if any origins are improperly formatted, otherwise an empty list.
    
    Raises:
    None
    
    Important Functions:
    - `settings.CSRF_TRUSTED_ORIGINS`: The setting containing the list of trusted origins.
    - `Error`: The
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
