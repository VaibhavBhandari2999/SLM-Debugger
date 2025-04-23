from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template import engines
from django.template.response import TemplateResponse


def normal_view(request):
    return HttpResponse('OK')


def template_response(request):
    template = engines['django'].from_string('template_response OK{% for m in mw %}\n{{ m }}{% endfor %}')
    return TemplateResponse(request, template, context={'mw': []})


def server_error(request):
    raise Exception('Error in view')


def permission_denied(request):
    raise PermissionDenied()


def exception_in_render(request):
    """
    Generate a custom HTTP response that raises an exception during rendering.
    
    This function returns an instance of a custom HttpResponse class that overrides the render method to raise an exception.
    
    Parameters:
    request (HttpRequest): The HTTP request object.
    
    Returns:
    CustomHttpResponse: A custom HTTP response object that raises an exception when its render method is called.
    
    Raises:
    Exception: An exception is raised during the rendering process.
    """

    class CustomHttpResponse(HttpResponse):
        def render(self):
            raise Exception('Exception in HttpResponse.render()')

    return CustomHttpResponse('Error')
