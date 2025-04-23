import logging
import sys
from functools import wraps

from django.conf import settings
from django.core import signals
from django.core.exceptions import (
    PermissionDenied, RequestDataTooBig, SuspiciousOperation,
    TooManyFieldsSent,
)
from django.http import Http404
from django.http.multipartparser import MultiPartParserError
from django.urls import get_resolver, get_urlconf
from django.utils.log import log_response
from django.views import debug


def convert_exception_to_response(get_response):
    """
    Wrap the given get_response callable in exception-to-response conversion.

    All exceptions will be converted. All known 4xx exceptions (Http404,
    PermissionDenied, MultiPartParserError, SuspiciousOperation) will be
    converted to the appropriate response, and all other exceptions will be
    converted to 500 responses.

    This decorator is automatically applied to all middleware to ensure that
    no middleware leaks an exception and that the next middleware in the stack
    can rely on getting a response instead of an exception.
    """
    @wraps(get_response)
    def inner(request):
        """
        Function to handle request processing.
        
        Parameters:
        request (HttpRequest): The incoming HTTP request object.
        
        Returns:
        HttpResponse: The outgoing HTTP response object.
        
        This function processes an incoming HTTP request. It attempts to call the `get_response` function with the request. If an exception occurs during this process, it catches the exception and generates an appropriate response using the `response_for_exception` function. The function then returns the resulting response.
        """

        try:
            response = get_response(request)
        except Exception as exc:
            response = response_for_exception(request, exc)
        return response
    return inner


def response_for_exception(request, exc):
    """
    Generate an appropriate HTTP response for a given exception.
    
    This function handles various types of exceptions and generates the corresponding HTTP response. It takes a Django request object and an exception object as input. The function checks the type of the exception and processes it accordingly. For example, it handles 404, 403, and 400 errors, as well as SuspiciousOperation and SystemExit exceptions. It also logs the exception and renders the response if necessary. The function returns the generated
    """

    if isinstance(exc, Http404):
        if settings.DEBUG:
            response = debug.technical_404_response(request, exc)
        else:
            response = get_exception_response(request, get_resolver(get_urlconf()), 404, exc)

    elif isinstance(exc, PermissionDenied):
        response = get_exception_response(request, get_resolver(get_urlconf()), 403, exc)
        log_response(
            'Forbidden (Permission denied): %s', request.path,
            response=response,
            request=request,
            exc_info=sys.exc_info(),
        )

    elif isinstance(exc, MultiPartParserError):
        response = get_exception_response(request, get_resolver(get_urlconf()), 400, exc)
        log_response(
            'Bad request (Unable to parse request body): %s', request.path,
            response=response,
            request=request,
            exc_info=sys.exc_info(),
        )

    elif isinstance(exc, SuspiciousOperation):
        if isinstance(exc, (RequestDataTooBig, TooManyFieldsSent)):
            # POST data can't be accessed again, otherwise the original
            # exception would be raised.
            request._mark_post_parse_error()

        # The request logger receives events for any problematic request
        # The security logger receives events for all SuspiciousOperations
        security_logger = logging.getLogger('django.security.%s' % exc.__class__.__name__)
        security_logger.error(
            str(exc),
            extra={'status_code': 400, 'request': request},
        )
        if settings.DEBUG:
            response = debug.technical_500_response(request, *sys.exc_info(), status_code=400)
        else:
            response = get_exception_response(request, get_resolver(get_urlconf()), 400, exc)

    elif isinstance(exc, SystemExit):
        # Allow sys.exit() to actually exit. See tickets #1023 and #4701
        raise

    else:
        signals.got_request_exception.send(sender=None, request=request)
        response = handle_uncaught_exception(request, get_resolver(get_urlconf()), sys.exc_info())
        log_response(
            '%s: %s', response.reason_phrase, request.path,
            response=response,
            request=request,
            exc_info=sys.exc_info(),
        )

    # Force a TemplateResponse to be rendered.
    if not getattr(response, 'is_rendered', True) and callable(getattr(response, 'render', None)):
        response = response.render()

    return response


def get_exception_response(request, resolver, status_code, exception):
    """
    Generate an exception response for a given request.
    
    This function handles the resolution of an error response when an exception occurs during request processing. It attempts to call a specific error handler based on the status code and the exception type. If the error handler fails, it falls back to handling the uncaught exception.
    
    Parameters:
    request (HttpRequest): The current HTTP request object.
    resolver (BaseHandler): The resolver object responsible for resolving error handlers.
    status_code (int): The HTTP status code associated with
    """

    try:
        callback, param_dict = resolver.resolve_error_handler(status_code)
        response = callback(request, **{**param_dict, 'exception': exception})
    except Exception:
        signals.got_request_exception.send(sender=None, request=request)
        response = handle_uncaught_exception(request, resolver, sys.exc_info())

    return response


def handle_uncaught_exception(request, resolver, exc_info):
    """
    Processing for any otherwise uncaught exceptions (those that will
    generate HTTP 500 responses).
    """
    if settings.DEBUG_PROPAGATE_EXCEPTIONS:
        raise

    if settings.DEBUG:
        return debug.technical_500_response(request, *exc_info)

    # Return an HttpResponse that displays a friendly error message.
    callback, param_dict = resolver.resolve_error_handler(500)
    return callback(request, **param_dict)
