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
    Function to check the CSRF cookie security settings.
    
    This function evaluates the security settings related to CSRF (Cross-Site Request Forgery) protection in a Django application. It checks if the CSRF cookie is marked as secure, which means it is only sent over HTTPS. The function returns a list of warnings if the CSRF cookie is not secure, otherwise it returns an empty list.
    
    Parameters:
    - app_configs: Configuration settings for the Django application.
    - kwargs: Additional keyword arguments.
    
    Returns:
    - A list of
    """

    passed_check = (
        settings.CSRF_USE_SESSIONS or
        not _csrf_middleware() or
        settings.CSRF_COOKIE_SECURE
    )
    return [] if passed_check else [W016]
