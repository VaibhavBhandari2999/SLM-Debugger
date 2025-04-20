from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template import engines
from django.template.response import TemplateResponse


def normal_view(request):
    return HttpResponse("OK")


def template_response(request):
    """
    Generate a template response for a Django request.
    
    This function creates a response using a Django template engine. It takes a Django request object as input and returns a TemplateResponse object.
    
    Parameters:
    request (HttpRequest): The Django request object containing metadata about the incoming request.
    
    Returns:
    TemplateResponse: A Django TemplateResponse object containing the rendered template.
    
    Usage:
    response = template_response(request)
    """

    template = engines["django"].from_string(
        "template_response OK{% for m in mw %}\n{{ m }}{% endfor %}"
    )
    return TemplateResponse(request, template, context={"mw": []})


def server_error(request):
    raise Exception("Error in view")


def permission_denied(request):
    raise PermissionDenied()


def exception_in_render(request):
    class CustomHttpResponse(HttpResponse):
        def render(self):
            raise Exception("Exception in HttpResponse.render()")

    return CustomHttpResponse("Error")


async def async_exception_in_render(request):
    class CustomHttpResponse(HttpResponse):
        async def render(self):
            raise Exception("Exception in HttpResponse.render()")

    return CustomHttpResponse("Error")
