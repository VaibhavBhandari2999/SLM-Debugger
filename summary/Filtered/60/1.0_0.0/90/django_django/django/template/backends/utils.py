from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generate a CSRF (Cross-Site Request Forgery) protection input field for a Django web application.
    
    This function creates a hidden input field for CSRF protection, which is essential for securing web applications against CSRF attacks.
    
    Parameters:
    request (HttpRequest): The Django HttpRequest object representing the current request.
    
    Returns:
    SafeString: A formatted HTML string containing the CSRF input field.
    
    Key Details:
    - The CSRF token is retrieved using the `get_token(request)` function, which should be defined elsewhere in your
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request))


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
