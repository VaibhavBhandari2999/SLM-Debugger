from django.middleware.csrf import get_token
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.safestring import SafeString


def csrf_input(request):
    """
    Generates a CSRF input field for a Django web application.
    
    This function creates a hidden input field for CSRF protection, which is essential for preventing Cross-Site Request Forgery attacks.
    
    Args:
    request (HttpRequest): The current request object from Django.
    
    Returns:
    SafeString: A formatted HTML string containing the CSRF input field.
    
    Key Parameters:
    request: The request object used to retrieve the CSRF token.
    """

    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request))


csrf_input_lazy = lazy(csrf_input, SafeString, str)
csrf_token_lazy = lazy(get_token, str)
