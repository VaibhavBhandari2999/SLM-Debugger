from django.apps import apps
from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseGone, HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin


class RedirectFallbackMiddleware(MiddlewareMixin):
    # Defined as class-level attributes to be subclassing-friendly.
    response_gone_class = HttpResponseGone
    response_redirect_class = HttpResponsePermanentRedirect

    def __init__(self, get_response=None):
        """
        Initialize the RedirectFallbackMiddleware.
        
        Args:
        get_response (Callable, optional): A callable that takes a request and returns a response. This is used to chain middleware. Defaults to None.
        
        Raises:
        ImproperlyConfigured: If django.contrib.sites is not installed.
        
        This method is called when the middleware is initialized. It checks if 'django.contrib.sites' is installed and raises an ImproperlyConfigured exception if it is not. If 'django.contrib.sites' is installed
        """

        if not apps.is_installed('django.contrib.sites'):
            raise ImproperlyConfigured(
                "You cannot use RedirectFallbackMiddleware when "
                "django.contrib.sites is not installed."
            )
        super().__init__(get_response)

    def process_response(self, request, response):
        """
        Processes the HTTP response from a request.
        
        This function checks if the response status code is 404 (Not Found). If it is, it attempts to find a corresponding redirect in the database. If a redirect is found, it returns a redirect response to the new path. If no redirect is found, it returns the original response. If the request path does not end with a slash and settings.APPEND_SLASH is True, it tries to find a redirect for the path with an appended slash
        """

        # No need to check for a redirect for non-404 responses.
        if response.status_code != 404:
            return response

        full_path = request.get_full_path()
        current_site = get_current_site(request)

        r = None
        try:
            r = Redirect.objects.get(site=current_site, old_path=full_path)
        except Redirect.DoesNotExist:
            pass
        if r is None and settings.APPEND_SLASH and not request.path.endswith('/'):
            try:
                r = Redirect.objects.get(
                    site=current_site,
                    old_path=request.get_full_path(force_append_slash=True),
                )
            except Redirect.DoesNotExist:
                pass
        if r is not None:
            if r.new_path == '':
                return self.response_gone_class()
            return self.response_redirect_class(r.new_path)

        # No redirect was found. Return the response.
        return response
