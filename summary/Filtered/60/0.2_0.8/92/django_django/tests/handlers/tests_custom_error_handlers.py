from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.test import SimpleTestCase, modify_settings, override_settings
from django.urls import path


class MiddlewareAccessingContent:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        This method is called when the middleware is invoked. It processes the request and returns a response. The method first calls the `get_response` method to handle the request and obtain a response. It then asserts that the `content` attribute of the response is available, even if the response is based on a `TemplateResponse` with an exception. Finally, it returns the processed response.
        
        Parameters:
        - request: The incoming HTTP request object.
        
        Returns:
        - response: The processed HTTP response object.
        
        Note
        """

        response = self.get_response(request)
        # Response.content should be available in the middleware even with a
        # TemplateResponse-based exception response.
        assert response.content
        return response


def template_response_error_handler(request, exception=None):
    return TemplateResponse(request, "test_handler.html", status=403)


def permission_denied_view(request):
    raise PermissionDenied


urlpatterns = [
    path("", permission_denied_view),
]

handler403 = template_response_error_handler


@override_settings(ROOT_URLCONF="handlers.tests_custom_error_handlers")
@modify_settings(
    MIDDLEWARE={
        "append": "handlers.tests_custom_error_handlers.MiddlewareAccessingContent"
    }
)
class CustomErrorHandlerTests(SimpleTestCase):
    def test_handler_renders_template_response(self):
        """
        BaseHandler should render TemplateResponse if necessary.
        """
        response = self.client.get("/")
        self.assertContains(response, "Error handler content", status_code=403)
