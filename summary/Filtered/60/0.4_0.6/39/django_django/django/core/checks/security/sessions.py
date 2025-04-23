from django.conf import settings

from .. import Tags, Warning, register


def add_session_cookie_message(message):
    """
    Adds a message to the given message string, emphasizing the importance of using a secure-only session cookie for enhancing security against session hijacking.
    
    Args:
    message (str): The original message to which the additional information will be appended.
    
    Returns:
    str: The original message appended with the additional information about secure-only session cookies.
    """

    return message + (
        " Using a secure-only session cookie makes it more difficult for "
        "network traffic sniffers to hijack user sessions."
    )


W010 = Warning(
    add_session_cookie_message(
        "You have 'django.contrib.sessions' in your INSTALLED_APPS, "
        "but you have not set SESSION_COOKIE_SECURE to True."
    ),
    id='security.W010',
)

W011 = Warning(
    add_session_cookie_message(
        "You have 'django.contrib.sessions.middleware.SessionMiddleware' "
        "in your MIDDLEWARE, but you have not set "
        "SESSION_COOKIE_SECURE to True."
    ),
    id='security.W011',
)

W012 = Warning(
    add_session_cookie_message("SESSION_COOKIE_SECURE is not set to True."),
    id='security.W012',
)


def add_httponly_message(message):
    """
    Add an HttpOnly message to the given message.
    
    Args:
    message (str): The original message to which the HttpOnly message will be appended.
    
    Returns:
    str: The original message with an appended HttpOnly message.
    """

    return message + (
        " Using an HttpOnly session cookie makes it more difficult for "
        "cross-site scripting attacks to hijack user sessions."
    )


W013 = Warning(
    add_httponly_message(
        "You have 'django.contrib.sessions' in your INSTALLED_APPS, "
        "but you have not set SESSION_COOKIE_HTTPONLY to True.",
    ),
    id='security.W013',
)

W014 = Warning(
    add_httponly_message(
        "You have 'django.contrib.sessions.middleware.SessionMiddleware' "
        "in your MIDDLEWARE, but you have not set "
        "SESSION_COOKIE_HTTPONLY to True."
    ),
    id='security.W014',
)

W015 = Warning(
    add_httponly_message("SESSION_COOKIE_HTTPONLY is not set to True."),
    id='security.W015',
)


@register(Tags.security, deploy=True)
def check_session_cookie_secure(app_configs, **kwargs):
    errors = []
    if not settings.SESSION_COOKIE_SECURE:
        if _session_app():
            errors.append(W010)
        if _session_middleware():
            errors.append(W011)
        if len(errors) > 1:
            errors = [W012]
    return errors


@register(Tags.security, deploy=True)
def check_session_cookie_httponly(app_configs, **kwargs):
    """
    Function to check if the session cookie has the HTTPOnly flag enabled.
    
    This function checks if the `SESSION_COOKIE_HTTPONLY` setting is enabled. If it is not, it appends one or more warning codes to the `errors` list based on the presence of the session app and middleware.
    
    Parameters:
    - app_configs: Configuration settings for the application.
    - kwargs: Additional keyword arguments.
    
    Returns:
    - A list of warning codes (integers) indicating issues found.
    
    Key Points:
    - The function
    """

    errors = []
    if not settings.SESSION_COOKIE_HTTPONLY:
        if _session_app():
            errors.append(W013)
        if _session_middleware():
            errors.append(W014)
        if len(errors) > 1:
            errors = [W015]
    return errors


def _session_middleware():
    return 'django.contrib.sessions.middleware.SessionMiddleware' in settings.MIDDLEWARE


def _session_app():
    return "django.contrib.sessions" in settings.INSTALLED_APPS
