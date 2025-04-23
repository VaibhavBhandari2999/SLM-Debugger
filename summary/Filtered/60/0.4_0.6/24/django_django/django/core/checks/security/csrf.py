from django.conf import settings

from .. import Tags, Warning, register

W003 = Warning(
    "You don't appear to be using Django's built-in "
    "cross-site request forgery protection via the middleware "
    "('django.middleware.csrf.CsrfViewMiddleware' is not in your "
    "MIDDLEWARE). Enabling the middleware is the safest approach "
    "to ensure you don't leave any holes.",
    id='security.W003',
)

W016 = Warning(
    "You have 'django.middleware.csrf.CsrfViewMiddleware' in your "
    "MIDDLEWARE, but you have not set CSRF_COOKIE_SECURE to True. "
    "Using a secure-only CSRF cookie makes it more difficult for network "
    "traffic sniffers to steal the CSRF token.",
    id='security.W016',
)


def _csrf_middleware():
    return 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE


@register(Tags.security, deploy=True)
def check_csrf_middleware(app_configs, **kwargs):
    passed_check = _csrf_middleware()
    return [] if passed_check else [W003]


@register(Tags.security, deploy=True)
def check_csrf_cookie_secure(app_configs, **kwargs):
    """
    Function to check if the CSRF cookie is secure.
    
    This function evaluates whether the CSRF cookie is secure based on certain conditions. It returns a list of warnings if the conditions are not met, otherwise it returns an empty list.
    
    Parameters:
    app_configs (object): Configuration details of the Django application.
    kwargs (dict): Additional keyword arguments.
    
    Returns:
    list: A list of warnings if the CSRF cookie is not secure, otherwise an empty list.
    
    Key Conditions:
    1. If CSRF_USE_SESSIONS
    """

    passed_check = (
        settings.CSRF_USE_SESSIONS or
        not _csrf_middleware() or
        settings.CSRF_COOKIE_SECURE
    )
    return [] if passed_check else [W016]
