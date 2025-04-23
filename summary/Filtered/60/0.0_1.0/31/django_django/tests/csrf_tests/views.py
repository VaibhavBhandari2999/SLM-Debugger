from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.template import Context, RequestContext, Template
from django.template.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie


def post_form_view(request):
    """Return a POST form (without a token)."""
    return HttpResponse(content="""
<html><body><h1>\u00a1Unicode!<form method="post"><input type="text"></form></body></html>
""")


@ensure_csrf_cookie
def ensure_csrf_cookie_view(request):
    # Doesn't insert a token or anything.
    return HttpResponse()


def token_view(request):
    """
    Generates a CSRF token for the request.
    
    This function creates a context with CSRF processing and renders a template containing the CSRF token. It returns an HTTP response with the rendered template.
    
    Parameters:
    - request (HttpRequest): The HTTP request object.
    
    Returns:
    - HttpResponse: An HTTP response containing the rendered template with the CSRF token.
    """

    context = RequestContext(request, processors=[csrf])
    template = Template('{% csrf_token %}')
    return HttpResponse(template.render(context))


def non_token_view_using_request_processor(request):
    """Use the csrf view processor instead of the token."""
    context = RequestContext(request, processors=[csrf])
    template = Template('')
    return HttpResponse(template.render(context))


def csrf_token_error_handler(request, **kwargs):
    """This error handler accesses the CSRF token."""
    template = Template(get_token(request))
    return HttpResponse(template.render(Context()), status=599)
