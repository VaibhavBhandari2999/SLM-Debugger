from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF (Cross-Site Request Forgery) input field for a Django web application.
    
    This function creates a hidden input field that is required for CSRF protection in Django web forms.
    
    Parameters:
    request (HttpRequest): The current HTTP request object.
    
    Returns:
    SafeString: A formatted HTML string containing the CSRF input field.
    
    Key Details:
    - The CSRF input field is generated using the CSRF token from the request.
    - The field is hidden and named 'csrfmiddlewaretoken'.
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request))


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
